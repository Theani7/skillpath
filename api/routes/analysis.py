import hashlib
import io
import json
import logging
import os
import re
import secrets
import tempfile
import time
import zipfile
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, EmailStr, Field

from api.auth import get_current_optional_user, get_current_user
from api.career_services import compute_resume_score_breakdown, generate_job_matches
from api.database import get_db_connection
from api.exceptions import LLMServiceException, ResumeParseException
from api.extractor import extract_text_from_docx, extract_text_from_pdf, parse_resume_with_gemini
from api.resume_parser import parse_resume_fallback
from api.market_data import get_market_trends_for_role

logger = logging.getLogger("resume-analyzer")

router = APIRouter(tags=["analysis"])

# Bump this when scoring/parsing logic changes to auto-invalidate stale cache entries.
_CACHE_VERSION = 3

# Limit upload size to 5 MiB to mitigate DoS attacks
MAX_FILE_SIZE = 5 * 1024 * 1024

PDF_MAGIC = b"%PDF"
ZIP_MAGIC = b"PK\x03\x04"


class Feedback(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    score: int = Field(..., ge=1, le=5)
    comments: str = Field(default="", max_length=2000)


def get_content_hash(data: bytes) -> str:
    """Generate SHA-256 hash of file content for caching.
    Includes _CACHE_VERSION so bumping it auto-invalidates all old entries."""
    return hashlib.sha256(f"{_CACHE_VERSION}:".encode() + data).hexdigest()


def _detect_filetype(contents: bytes, filename: str) -> Optional[str]:
    if contents.startswith(PDF_MAGIC):
        return "pdf"
    if contents.startswith(ZIP_MAGIC):
        # PK\x03\x04 is the generic ZIP signature - xlsx, pptx, jar and any
        # plain .zip share it. Only a real OOXML wordprocessing package has
        # [Content_Types].xml plus word/document.xml, so check the members
        # rather than trusting the prefix.
        try:
            with zipfile.ZipFile(io.BytesIO(contents)) as z:
                names = set(z.namelist())
        except zipfile.BadZipFile:
            return None
        if "[Content_Types].xml" in names and "word/document.xml" in names:
            return "docx"
        return None
    return None


@router.post("/api/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    target_role: str = Form(None),
    current_user: dict = Depends(get_current_user)
):
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 5MB.")
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file upload")

    filetype = _detect_filetype(contents, file.filename or "")
    if not filetype:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    safe_filename = re.sub(r"[^\w.\-]", "_", (file.filename or "resume")[:120])
    content_hash = get_content_hash(contents)
    t_role = (target_role or "General")[:200]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT result_json FROM analysis_cache WHERE content_hash = %s AND target_role = %s AND (expires_at IS NULL OR expires_at > %s)",
        (content_hash, t_role, int(time.time())),
    )
    cache_row = cursor.fetchone()
    if cache_row:
        # Cache hit - reuse the result but STILL insert a new user_data row
        # so that /api/user/latest-analysis always reflects the latest upload.
        final_response_payload = None
        try:
            final_response_payload = json.loads(cache_row["result_json"])
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"Corrupt cache entry for {safe_filename}, deleting and re-parsing")
            cursor.execute("DELETE FROM analysis_cache WHERE content_hash = %s AND target_role = %s", (content_hash, t_role))
            conn.commit()
        else:
            logger.info(f"Cache hit for {safe_filename} - reusing result, saving new user_data row")

        if final_response_payload is not None:
            try:
                sec_token = secrets.token_hex(16)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                u_id = current_user['id'] if current_user and 'id' in current_user else -1
                resume_data_c = final_response_payload.get("data", {})
                skills_c = resume_data_c.get('skills', [])
                recommended_skills_c = final_response_payload.get("recommended_skills", [])
                missing_skills_c = final_response_payload.get("missing_skill_names", [])
                missing_skills_str_c = ", ".join(missing_skills_c) if missing_skills_c else ""
                resume_score_c = final_response_payload.get("resume_score", 0)
                predicted_field_c = final_response_payload.get("predicted_field", "")
                cursor.execute(
                    """INSERT INTO user_data (sec_token, act_name, act_mail, act_mob, "Name", "Email_ID", resume_score, "Timestamp", "Page_no", "Predicted_Field", "User_level", "Actual_skills", "Recommended_skills", "Recommended_courses", pdf_name, target_role, missing_skills, user_id, analysis_data, content_hash)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        sec_token,
                        resume_data_c.get('name') or 'N/A',
                        resume_data_c.get('email') or 'N/A',
                        resume_data_c.get('mobile_number') or 'N/A',
                        resume_data_c.get('name') or 'N/A',
                        resume_data_c.get('email') or 'N/A',
                        str(resume_score_c),
                        timestamp,
                        str(resume_data_c.get('no_of_pages', 1)),
                        predicted_field_c,
                        "Unknown Level",
                        ", ".join(skills_c) if skills_c else "",
                        ", ".join(recommended_skills_c) if recommended_skills_c else "",
                        "Courses mapped via API",
                        safe_filename,
                        t_role,
                        missing_skills_str_c,
                        u_id,
                        json.dumps(final_response_payload),
                        content_hash
                    )
                )
                conn.commit()
            except Exception as db_error:
                conn.rollback()
                logger.error(f"Cache-hit user_data insert failed: {db_error}")
            finally:
                conn.close()
            return final_response_payload
        conn.close()

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{filetype}") as tmp:
            try:
                os.chmod(tmp.name, 0o600)
            except (OSError, PermissionError):
                pass
            tmp.write(contents)
            tmp_path = tmp.name

        if filetype == "pdf":
            resume_text = extract_text_from_pdf(tmp_path)
        else:
            resume_text = extract_text_from_docx(tmp_path)

        if not resume_text.strip():
            raise ResumeParseException("Could not extract any text from the uploaded file.")

# Step 2: Local Hybrid Parsing (Fast, Free, Regex-based)
        local_data = parse_resume_fallback(resume_text, target_role, file_path=tmp_path)

        # Step 3: Try Gemini first (if API key is configured)
        has_gemini_key = os.getenv("GEMINI_API_KEY") and os.getenv("GEMINI_API_KEY").strip()
        resume_data = None
        
        if has_gemini_key:
            logger.info("Attempting Gemini parse...")
            try:
                resume_data = parse_resume_with_gemini(tmp_path, target_role)
                if resume_data and resume_data.get("skills"):
                    logger.info(f"Gemini parse successful: {len(resume_data.get('skills', []))} skills extracted")
                else:
                    logger.warning("Gemini returned empty/incomplete data")
                    resume_data = None
            except Exception as e:
                logger.warning(f"Gemini parse failed: {e}")
                resume_data = None
        
        # Step 4: Fall back to local regex parser if AI provider returned nothing
        if not resume_data:
            logger.info("AI provider returned no data, using local regex parser")
            resume_data = local_data

        if not resume_data:
            raise LLMServiceException("AI service returned no data and local fallback failed.")
        
        # Explainable scoring with evidence
        resume_score, feedback_msgs, score_breakdown = compute_resume_score_breakdown(resume_data, target_role)
            
        # Advanced Field Prediction based on keyword density
        skills = resume_data.get('skills', [])
        skills_lower = [s.lower() for s in skills]
        
        predicted_field = "Unknown"
        recommended_skills = []
        recommended_courses = []
        # recommended_courses = [] # This will be populated from DB
        
        # New Match Score and Missing Skills logic
        match_score = resume_data.get('match_score', 0)
        missing_skills = resume_data.get('missing_skills', [])
        missing_skills_videos = []
        
        from api.courses import predict_field_with_ai, generate_youtube_search_links
        from api.seed_data import get_skill_recommendations, get_roadmaps, get_resume_videos, get_interview_videos
        
        # Call out to our new ML Model to get the closest semantic field
        predicted_field = predict_field_with_ai(resume_data)
        
        
        dynamic_resume_videos = get_resume_videos().get('General', [])
        dynamic_interview_videos = get_interview_videos().get('General', [])
        skill_videos = []
        
        # Extract dynamic roadmap from Gemini payload
        roadmap = resume_data.get('roadmap', [])
        if not roadmap:
            roadmap = get_roadmaps().get('General', [])
            
        trends = get_market_trends_for_role('General')
        
        # Initialize Database connection early for courses
        # Use existing conn
        cursor = conn.cursor()

        # Fetch courses from dynamic DB instead of static dictionary
        recommended_courses = []
        cursor.execute("SELECT course_name, course_url FROM courses WHERE field = %s", ('General',))
        for row in cursor.fetchall():
            recommended_courses.append({"name": row['course_name'], "url": row['course_url']})
        
        mapping_field = target_role if target_role else predicted_field

        if mapping_field != "Unknown":
            # Personalized recommendations: only suggest skills the user is actually missing
            skill_recs = get_skill_recommendations()
            all_field_skills = skill_recs.get(mapping_field, [])
            found_skills_lower = {s.lower() for s in (resume_data.get("skills") or [])}
            recommended_skills = [s for s in all_field_skills if s.lower() not in found_skills_lower]
            if not recommended_skills:
                recommended_skills = all_field_skills[:5]
            
            # Fetch field-specific courses
            cursor.execute("SELECT course_name, course_url FROM courses WHERE field = %s", (mapping_field,))
            field_courses = cursor.fetchall()
            if field_courses:
                recommended_courses = [{"name": row['course_name'], "url": row['course_url']} for row in field_courses]

            # Fallback to static roadmap only if dynamic extraction failed
            if not resume_data.get('roadmap', []):
                roadmap = get_roadmaps().get(mapping_field, get_roadmaps().get('General', []))
            trends = get_market_trends_for_role(mapping_field)
            resume_vids = get_resume_videos()
            interview_vids = get_interview_videos()
            dynamic_resume_videos = resume_vids.get(mapping_field, resume_vids.get('General', []))
            dynamic_interview_videos = interview_vids.get(mapping_field, interview_vids.get('General', []))
            # Generate personalized youtube links for missing skills specifically
            skill_videos = generate_youtube_search_links(recommended_skills[:6])
            
        # Generate course links specifically for missing skills if they exist
        if missing_skills:
             missing_skills_videos = generate_youtube_search_links(missing_skills[:6])
            
        sec_token = secrets.token_hex(10)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        missing_skills_str = ", ".join(missing_skills) if missing_skills else ""
        
        u_id = -1
        if current_user and 'id' in current_user:
            u_id = current_user['id']
            
        final_response_payload = {
            "status": "success",
            "data": resume_data,
            "target_role": target_role,
            "predicted_field": predicted_field,
            "recommended_skills": recommended_skills,
            "recommended_courses": recommended_courses,
            "match_score": match_score,
            "missing_skills": missing_skills_videos,
            "missing_skill_names": missing_skills,
            "roadmap": roadmap,
            "trends": trends,
            "job_matches": generate_job_matches(mapping_field, skills, missing_skills),
            "resume_score": resume_score,
            "score_breakdown": score_breakdown,
            "feedback": feedback_msgs,
            "videos": {
                "resume": list(set(dynamic_resume_videos)),
                "interview": list(set(dynamic_interview_videos)),
                "tutorials": skill_videos
            }
        }

        cache_expires = int(time.time()) + 7 * 24 * 3600
        cursor.execute(
            "INSERT INTO analysis_cache (content_hash, target_role, result_json, expires_at) VALUES (%s, %s, %s, %s) "
            "ON CONFLICT (content_hash, target_role) DO UPDATE SET result_json = excluded.result_json, expires_at = excluded.expires_at",
            (content_hash, t_role, json.dumps(final_response_payload), cache_expires),
        )

        cursor.execute(
            """INSERT INTO user_data (sec_token, act_name, act_mail, act_mob, "Name", "Email_ID", resume_score, "Timestamp", "Page_no", "Predicted_Field", "User_level", "Actual_skills", "Recommended_skills", "Recommended_courses", pdf_name, target_role, missing_skills, user_id, analysis_data, content_hash)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                sec_token,
                resume_data.get('name') or 'N/A',
                resume_data.get('email') or 'N/A',
                resume_data.get('mobile_number') or 'N/A',
                resume_data.get('name') or 'N/A',
                resume_data.get('email') or 'N/A',
                str(resume_score),
                timestamp,
                str(resume_data.get('no_of_pages', 1)),
                predicted_field,
                "Unknown Level",
                ", ".join(skills) if skills else "",
                ", ".join(recommended_skills) if recommended_skills else "",
                "Courses mapped via API",
                safe_filename,
                t_role,
                missing_skills_str,
                u_id,
                json.dumps(final_response_payload),
                content_hash
            )
        )
        conn.commit()

        return final_response_payload

    except Exception as parse_error:
        logger.error(f"Analysis error for {safe_filename}: {parse_error}")
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        conn.close()
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


@router.post("/api/feedback")
def submit_feedback(feedback: Feedback, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute(
            """INSERT INTO user_feedback (feed_name, feed_email, feed_score, comments, "Timestamp") VALUES (%s, %s, %s, %s, %s)""",
            (feedback.name, feedback.email, feedback.score, feedback.comments, timestamp)
        )
        conn.commit()
    finally:
        conn.close()
    return {"status": "success", "message": "Feedback saved."}


@router.get("/api/job-roles")
def get_public_job_roles():
    """Get active job roles for the target role selector (no auth required)."""
    default_roles = [
        'Software Engineering', 'Frontend Development', 'Backend Development',
        'Data Science', 'DevOps', 'Mobile Development', 'Full Stack Development',
        'Cybersecurity', 'Product Management', 'Business Analysis',
        'Technical Writing', 'IT Support', 'Network Administration',
        'Cloud Engineering', 'Data Engineering', 'Machine Learning',
        'Cloud Architecture', 'Web Development', 'UI/UX Design',
        'Android Development', 'iOS Development', 'Quality Assurance',
    ]

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM job_roles WHERE is_active = 1 ORDER BY title")
        rows = cursor.fetchall()
        db_roles = [row["title"] for row in rows]
    except Exception:
        db_roles = []
    finally:
        conn.close()

    combined = list(dict.fromkeys(db_roles + default_roles))
    return {"roles": combined}
