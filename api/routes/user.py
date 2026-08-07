import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.auth import get_current_user
from api.database import get_db_connection

logger = logging.getLogger("resume-analyzer")

router = APIRouter(prefix="/api/user", tags=["user"])


class UserProfileUpdate(BaseModel):
    full_name: str = Field(default="", max_length=200)
    phone: str = Field(default="", max_length=20)
    location: str = Field(default="", max_length=200)
    bio: str = Field(default="", max_length=500)
    current_role: str = Field(default="", max_length=100)
    experience_years: str = Field(default="", max_length=10)
    linkedin_url: str = Field(default="", max_length=500)
    github_url: str = Field(default="", max_length=500)


class PreferencesInput(BaseModel):
    target_role: str = Field(default="", max_length=200)
    timeline_months: int = Field(default=6, ge=1, le=120)
    preferred_location: str = Field(default="", max_length=200)
    salary_target: int = Field(default=0, ge=0, le=10_000_000)
    locale: str = Field(default="en", max_length=10)


@router.get("/latest-analysis")
def get_latest_analysis(current_user: dict = Depends(get_current_user)):
    """
    Return the most recent saved analysis for the logged-in user.
    Reads from the user_data table only - never re-invokes the AI.
    Use this to render the persistent "My Analysis" view in the sidebar
    without consuming Gemini tokens.
    """
    if not current_user or 'id' not in current_user:
        raise HTTPException(status_code=401, detail="Unauthorized request")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT ID, Timestamp, Predicted_Field, resume_score, target_role,
                   missing_skills, Actual_skills, Recommended_skills,
                   pdf_name, analysis_data
            FROM user_data
            WHERE user_id = %s
            ORDER BY ID DESC
            LIMIT 1
            ''',
            (current_user['id'],),
        )
        row = cursor.fetchone()

        # Fetch role skills info for Core/nice-to-have badges
        role_skills_info = []
        if row and row['target_role']:
            cursor.execute(
                "SELECT js.skill_name, js.is_required FROM job_role_skills js "
                "JOIN job_roles jr ON js.job_role_id = jr.id "
                "WHERE jr.title = %s AND jr.is_active = 1",
                (row['target_role'],),
            )
            role_skills_info = [{"skill": r["skill_name"], "is_required": bool(r["is_required"])} for r in cursor.fetchall()]
    finally:
        conn.close()

    if not row:
        return {"found": False}

    payload = None
    if row['analysis_data']:
        try:
            payload = json.loads(row['analysis_data'])
        except (json.JSONDecodeError, TypeError):
            payload = None

    if payload is None:
        # Old rows without full analysis_data JSON - synthesize from columns
        payload = {
            "status": "success",
            "data": {
                "name": "",
                "email": "",
                "skills": row['Actual_skills'].split(',') if row['Actual_skills'] else [],
                "no_of_pages": 1,
            },
            "target_role": row['target_role'],
            "predicted_field": row['Predicted_Field'],
            "resume_score": float(row['resume_score']) if row['resume_score'] else 0,
            "missing_skill_names": row['missing_skills'].split(',') if row['missing_skills'] else [],
            "missing_skills": [],
            "feedback": [],
            "videos": {"resume": [], "interview": [], "tutorials": []},
            "roadmap": [],
            "trends": None,
            "score_breakdown": {},
        }

    return {
        "found": True,
        "id": row['ID'],
        "timestamp": row['Timestamp'],
        "pdf_name": row['pdf_name'],
        "predicted_field": row['Predicted_Field'],
        "target_role": row['target_role'],
        "resume_score": float(row['resume_score']) if row['resume_score'] else 0,
        "analysis": payload,
        "role_skills": role_skills_info,
    }


@router.get("/history")
def get_user_history(current_user: dict = Depends(get_current_user)):
    """Fetch all past resume analyses for the logged-in user."""
    if not current_user or 'id' not in current_user:
        raise HTTPException(status_code=401, detail="Unauthorized request")
        
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ID, Timestamp, Predicted_Field, resume_score, target_role, missing_skills, Actual_skills, Recommended_skills, analysis_data
            FROM user_data
            WHERE user_id = %s
            ORDER BY ID DESC
        ''', (current_user['id'],))
        rows = cursor.fetchall()
    finally:
        conn.close()
    
    # Format the data for the frontend
    history = []
    for row in rows:
        analysis_data = None
        if row['analysis_data']:
            try:
                analysis_data = json.loads(row['analysis_data'])
            except json.JSONDecodeError:
                pass
                
        history.append({
            "id": row['ID'],
            "timestamp": row['Timestamp'],
            "predicted_field": row['Predicted_Field'],
            "target_role": row['target_role'],
            "resume_score": float(row['resume_score']) if row['resume_score'] else 0,
            "missing_skills": row['missing_skills'].split(',') if row['missing_skills'] else [],
            "actual_skills": row['Actual_skills'].split(',') if row['Actual_skills'] else [],
            "recommended_skills": row['Recommended_skills'].split(',') if row['Recommended_skills'] else [],
            "analysis_data": analysis_data
        })
        
    return {"history": history}


@router.delete("/history")
def delete_user_history(current_user: dict = Depends(get_current_user)):
    """Delete all past resume analyses for the logged-in user."""
    if not current_user or 'id' not in current_user:
        raise HTTPException(status_code=401, detail="Unauthorized request")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_data WHERE user_id = %s", (current_user['id'],))
        deleted = cursor.rowcount
        conn.commit()
    finally:
        conn.close()
    return {"status": "success", "deleted": deleted}


@router.delete("/analysis/{analysis_id}")
def delete_user_analysis(analysis_id: int, current_user: dict = Depends(get_current_user)):
    """Delete a single analysis by ID. Ownership-checked. Also cleans up cache."""
    if not current_user or 'id' not in current_user:
        raise HTTPException(status_code=401, detail="Unauthorized request")
    if not isinstance(analysis_id, int) or analysis_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid analysis id")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Get the analysis data and content_hash for cache cleanup
        cursor.execute(
            "SELECT content_hash, target_role FROM user_data WHERE ID = %s AND user_id = %s",
            (analysis_id, current_user['id']),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Analysis not found")

        # Delete from analysis_cache if we have the content_hash
        if row['content_hash'] and row['target_role']:
            cursor.execute(
                "DELETE FROM analysis_cache WHERE content_hash = %s AND target_role = %s",
                (row['content_hash'], row['target_role']),
            )

        # Delete from user_roadmap_progress for this analysis
        cursor.execute("DELETE FROM user_roadmap_progress WHERE user_id = %s AND analysis_id = %s",
                       (current_user['id'], analysis_id))

        # Delete from shared_reports for this analysis
        cursor.execute("DELETE FROM shared_reports WHERE user_id = %s AND analysis_id = %s",
                       (current_user['id'], analysis_id))

        # Delete the analysis itself
        cursor.execute(
            "DELETE FROM user_data WHERE ID = %s AND user_id = %s",
            (analysis_id, current_user['id']),
        )
        deleted = cursor.rowcount
        conn.commit()
    finally:
        conn.close()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {"status": "success", "deleted": deleted}


@router.get("/profile")
def get_user_profile(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_profiles WHERE user_id = %s", (current_user["id"],))
        row = cursor.fetchone()
    finally:
        conn.close()
    return {"profile": dict(row) if row else {}}


@router.put("/profile")
def update_user_profile(profile: UserProfileUpdate, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO user_profiles(user_id, full_name, phone, location, bio, current_role, experience_years, linkedin_url, github_url, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                full_name = excluded.full_name,
                phone = excluded.phone,
                location = excluded.location,
                bio = excluded.bio,
                current_role = excluded.current_role,
                experience_years = excluded.experience_years,
                linkedin_url = excluded.linkedin_url,
                github_url = excluded.github_url,
                updated_at = CURRENT_TIMESTAMP
            """,
            (current_user["id"], profile.full_name, profile.phone, profile.location, profile.bio, 
             profile.current_role, profile.experience_years, profile.linkedin_url, profile.github_url)
        )
        conn.commit()
    finally:
        conn.close()
    return {"message": "Profile updated successfully"}


@router.get("/preferences")
def get_preferences(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_preferences WHERE user_id = %s", (current_user["id"],))
        row = cursor.fetchone()
    finally:
        conn.close()
    return {"preferences": dict(row) if row else {}}


@router.put("/preferences")
def update_preferences(payload: PreferencesInput, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO user_preferences(user_id, target_role, timeline_months, preferred_location, salary_target, locale, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                target_role = excluded.target_role,
                timeline_months = excluded.timeline_months,
                preferred_location = excluded.preferred_location,
                salary_target = excluded.salary_target,
                locale = excluded.locale,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                current_user["id"],
                payload.target_role,
                payload.timeline_months,
                payload.preferred_location,
                payload.salary_target,
                payload.locale,
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return {"status": "success"}


class RoadmapProgressUpdate(BaseModel):
    analysis_id: Optional[int] = None
    phase_index: int = Field(..., ge=0)
    task_index: int = Field(..., ge=0)
    completed: bool


@router.get("/roadmap-progress")
def get_roadmap_progress(analysis_id: Optional[int] = None, current_user: dict = Depends(get_current_user)):
    """Get all roadmap progress for the logged-in user."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if analysis_id:
            cursor.execute(
                "SELECT phase_index, task_index, completed FROM user_roadmap_progress WHERE user_id = %s AND analysis_id = %s",
                (current_user["id"], analysis_id),
            )
        else:
            cursor.execute(
                "SELECT phase_index, task_index, completed, analysis_id FROM user_roadmap_progress WHERE user_id = %s",
                (current_user["id"],),
            )
        rows = cursor.fetchall()
    finally:
        conn.close()

    progress = {}
    for row in rows:
        key = f"{row['phase_index']}:{row['task_index']}"
        progress[key] = bool(row["completed"])

    return {"progress": progress}


@router.put("/roadmap-progress")
def update_roadmap_progress(payload: RoadmapProgressUpdate, current_user: dict = Depends(get_current_user)):
    """Update a single roadmap task's completion status."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO user_roadmap_progress (user_id, analysis_id, phase_index, task_index, completed, completed_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT(user_id, analysis_id, phase_index, task_index)
            DO UPDATE SET completed = excluded.completed,
                completed_at = CASE WHEN excluded.completed = 1 THEN CURRENT_TIMESTAMP ELSE NULL END""",
            (
                current_user["id"],
                payload.analysis_id,
                payload.phase_index,
                payload.task_index,
                1 if payload.completed else 0,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S") if payload.completed else None,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    return {"status": "success"}


@router.get("/skill-trends")
def get_skill_trends(current_user: dict = Depends(get_current_user)):
    """Get skill improvement trends across all analyses."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT ID, Timestamp, Actual_skills, missing_skills
            FROM user_data
            WHERE user_id = %s
            ORDER BY ID ASC""",
            (current_user["id"],),
        )
        rows = cursor.fetchall()
    finally:
        conn.close()

    if not rows:
        return {"trends": [], "summary": {"improved": [], "new": [], "lost": []}}

    analyses = []
    for row in rows:
        actual = set(s.strip() for s in (row["Actual_skills"] or "").split(",") if s.strip())
        missing = set(s.strip() for s in (row["missing_skills"] or "").split(",") if s.strip())
        analyses.append({
            "id": row["ID"],
            "timestamp": row["Timestamp"],
            "skills": actual,
            "gaps": missing,
        })

    trends = []
    if len(analyses) >= 2:
        first = analyses[0]
        latest = analyses[-1]

        gained = latest["skills"] - first["skills"]
        lost = first["skills"] - latest["skills"]
        still_missing = latest["gaps"] - first["gaps"]
        resolved = first["gaps"] - latest["gaps"]

        trends = [
            {"type": "improved", "skills": list(resolved), "count": len(resolved)},
            {"type": "gained", "skills": list(gained), "count": len(gained)},
            {"type": "lost", "skills": list(lost), "count": len(lost)},
            {"type": "new_gaps", "skills": list(still_missing), "count": len(still_missing)},
        ]

    return {
        "trends": trends,
        "analyses_count": len(analyses),
        "latest_skills": list(analyses[-1]["skills"]) if analyses else [],
        "latest_gaps": list(analyses[-1]["gaps"]) if analyses else [],
    }


class DeleteAccountRequest(BaseModel):
    password: str = Field(..., min_length=8, max_length=128)


@router.delete("/account")
def delete_account(payload: DeleteAccountRequest, current_user: dict = Depends(get_current_user)):
    """Delete the current user's account and all associated data."""
    if not current_user or 'id' not in current_user:
        raise HTTPException(status_code=401, detail="Unauthorized request")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Verify password
        cursor.execute("SELECT hashed_password FROM users WHERE id = %s", (current_user['id'],))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")

        from api.security import verify_password
        if not verify_password(payload.password, row['hashed_password']):
            raise HTTPException(status_code=400, detail="Incorrect password")

        user_id = current_user['id']

        # Delete all user data
        cursor.execute("DELETE FROM user_data WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM user_profiles WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM user_preferences WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM refresh_tokens WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM user_roadmap_progress WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM shared_reports WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM notifications WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))

        conn.commit()
    finally:
        conn.close()

    return {"status": "success", "message": "Account deleted"}


class ContactSupportRequest(BaseModel):
    subject: str = Field(..., min_length=5, max_length=200)
    message: str = Field(..., min_length=10, max_length=2000)


@router.post("/contact-support")
def contact_support(payload: ContactSupportRequest, current_user: dict = Depends(get_current_user)):
    """Submit a support request (stored in DB for admin review)."""
    if not current_user or 'id' not in current_user:
        raise HTTPException(status_code=401, detail="Unauthorized request")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO notifications (user_id, channel, message, status, created_at)
            VALUES (%s, 'support', %s, 'pending', %s)""",
            (
                current_user['id'],
                f"[{payload.subject}] {payload.message}",
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            ),
        )
        conn.commit()
    finally:
        conn.close()

    return {"status": "success", "message": "Support request submitted"}
