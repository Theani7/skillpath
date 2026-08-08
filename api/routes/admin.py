import json
import logging
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from psycopg2 import sql
from pydantic import BaseModel, Field

from api.auth import get_current_admin
from api.seed_data import invalidate_all_caches
from api.database import get_db_connection
from api.scraper import simulate_trend_update
from api.course_scraper import scrape_courses_for_field, FIELD_SEARCH_QUERIES

logger = logging.getLogger("resume-analyzer")

router = APIRouter(tags=["admin"])


def log_audit_action(admin_user: dict, action: str, target_type: str, target_id: str = None, details: str = "", request: Request = None):
    """Log an admin action to the audit_logs table."""
    ip_address = ""
    if request:
        ip_address = request.client.host if request.client else ""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO audit_logs (admin_user_id, admin_username, action, target_type, target_id, details, ip_address) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (admin_user.get("id"), admin_user.get("username", ""), action, target_type, str(target_id) if target_id else "", details, ip_address)
        )
        conn.commit()
    except Exception as e:
        logger.warning(f"Failed to write audit log: {e}")
    finally:
        if conn:
            conn.close()


class CourseInput(BaseModel):
    field: str
    course_name: str
    course_url: str


@router.post("/api/admin/trigger-scrape")
def trigger_simulated_scrape(current_admin: dict = Depends(get_current_admin)):
    """Allows an admin to manually trigger a simulated market shift."""
    result = simulate_trend_update()
    return result


@router.get("/api/admin/users")
def get_admin_users(
    current_admin: dict = Depends(get_current_admin),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Select only safe columns, exclude sensitive system info
        cursor.execute(
            """
            SELECT id, user_id, "Name", "Email_ID", "Timestamp", "Predicted_Field", resume_score,
                   target_role, missing_skills, "Actual_skills", "Recommended_skills",
                   pdf_name
            FROM user_data
            ORDER BY id DESC
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
        )
        rows = cursor.fetchall()
        # Get total count for pagination
        cursor.execute("SELECT COUNT(*) as total FROM user_data")
        total = cursor.fetchone()["total"]
    finally:
        conn.close()
    return {"users": [dict(r) for r in rows], "total": total, "limit": limit, "offset": offset}


@router.get("/api/admin/users/{analysis_id}")
def get_admin_user_detail(analysis_id: int, current_admin: dict = Depends(get_current_admin)):
    """Fetch full analysis data for a single resume upload."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, user_id, "Name", "Email_ID", "Timestamp", "Predicted_Field", resume_score,
                   target_role, missing_skills, "Actual_skills", "Recommended_skills",
                   pdf_name, analysis_data
            FROM user_data
            WHERE id = %s
            """,
            (analysis_id,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Analysis not found")
    finally:
        conn.close()
    return {"analysis": dict(row)}


@router.get("/api/admin/feedback")
def get_admin_feedback(
    current_admin: dict = Depends(get_current_admin),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, feed_name, feed_email, feed_score, comments, "Timestamp" FROM user_feedback ORDER BY id DESC LIMIT %s OFFSET %s""",
            (limit, offset),
        )
        rows = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) as total FROM user_feedback")
        total = cursor.fetchone()["total"]
    finally:
        conn.close()
    return {"feedback": [dict(r) for r in rows], "total": total, "limit": limit, "offset": offset}


@router.get("/api/admin/feedback/stats")
def get_feedback_stats(current_admin: dict = Depends(get_current_admin)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM user_feedback")
        total = cursor.fetchone()["total"]
        cursor.execute("SELECT feed_score, COUNT(*) as count FROM user_feedback GROUP BY feed_score")
        by_score = {row["feed_score"]: row["count"] for row in cursor.fetchall()}
    finally:
        conn.close()

    positive = by_score.get(4, 0) + by_score.get(5, 0)
    neutral = by_score.get(3, 0)
    negative = by_score.get(1, 0) + by_score.get(2, 0)
    ratio = round(positive / negative, 2) if negative > 0 else (float('inf') if positive > 0 else 0)

    return {
        "total": total,
        "positive": positive,
        "neutral": neutral,
        "negative": negative,
        "ratio": ratio if ratio != float('inf') else "∞",
        "by_score": {i: by_score.get(i, 0) for i in range(1, 6)},
    }


@router.delete("/api/admin/users/{analysis_id}")
def delete_admin_resume_log(analysis_id: int, current_admin: dict = Depends(get_current_admin)):
    """Delete a single resume analysis row (user_data.id).

    This path is the resume-log view. It must NOT touch the users table -
    the id here is a user_data row id, not a user account id.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_roadmap_progress WHERE analysis_id = %s", (analysis_id,))
        cursor.execute("DELETE FROM shared_reports WHERE analysis_id = %s", (analysis_id,))
        cursor.execute("DELETE FROM user_data WHERE id = %s", (analysis_id,))
        deleted = cursor.rowcount
        conn.commit()
    finally:
        conn.close()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Analysis not found")
    log_audit_action(current_admin, "delete_resume_log", "user_data", analysis_id)
    return {"status": "success", "message": f"Analysis {analysis_id} deleted."}


@router.delete("/api/admin/feedback/{feedback_id}")
def delete_admin_feedback(feedback_id: int, current_admin: dict = Depends(get_current_admin)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_feedback WHERE id = %s", (feedback_id,))
        conn.commit()
        invalidate_all_caches()
    finally:
        conn.close()
    return {"status": "success", "message": f"Feedback {feedback_id} deleted."}


@router.get("/api/admin/registered-users")
def get_registered_users(
    current_admin: dict = Depends(get_current_admin),
    q: str = Query(default="", description="Search by username or email"),
):
    """Fetch all actual registered users (not anonymous uploads)."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if q:
            like = f"%{q}%"
            cursor.execute(
                "SELECT id, username, email, role, is_active FROM users WHERE username LIKE %s OR email LIKE %s ORDER BY id DESC",
                (like, like),
            )
        else:
            cursor.execute("SELECT id, username, email, role, is_active FROM users ORDER BY id DESC")
        rows = cursor.fetchall()
    finally:
        conn.close()
    return {"users": [dict(r) for r in rows]}


class RoleUpdate(BaseModel):
    role: str = Field(..., pattern=r"^(admin|user)$")


@router.patch("/api/admin/registered-users/{user_id}/role")
def update_user_role(user_id: int, body: RoleUpdate, current_admin: dict = Depends(get_current_admin)):
    """Change a user's role (admin/user). Prevents removing the last admin."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, role FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user["role"] == "admin" and body.role != "admin":
            cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE role = 'admin'")
            if cursor.fetchone()["cnt"] <= 1:
                raise HTTPException(status_code=400, detail="Cannot remove the last admin")
        cursor.execute("UPDATE users SET role = %s WHERE id = %s", (body.role, user_id))
        conn.commit()
        invalidate_all_caches()
        cursor.execute("SELECT id, username, email, role, is_active FROM users WHERE id = %s", (user_id,))
        updated = cursor.fetchone()
    finally:
        conn.close()
    log_audit_action(current_admin, "change_role", "user", user_id, f"New role: {body.role}")
    return {"status": "success", "user": dict(updated)}


class StatusUpdate(BaseModel):
    is_active: bool


@router.patch("/api/admin/registered-users/{user_id}/status")
def update_user_status(user_id: int, body: StatusUpdate, current_admin: dict = Depends(get_current_admin)):
    """Activate or deactivate a user account."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="User not found")
        cursor.execute("UPDATE users SET is_active = %s WHERE id = %s", (1 if body.is_active else 0, user_id))
        conn.commit()
        invalidate_all_caches()
        cursor.execute("SELECT id, username, email, role, is_active FROM users WHERE id = %s", (user_id,))
        updated = cursor.fetchone()
    finally:
        conn.close()
    log_audit_action(current_admin, "toggle_status", "user", user_id, f"Active: {body.is_active}")
    return {"status": "success", "user": dict(updated)}


@router.delete("/api/admin/registered-users/{user_id}")
def delete_registered_user(user_id: int, current_admin: dict = Depends(get_current_admin)):
    """Delete (ban) a registered user and cascade-delete their data."""
    if user_id == current_admin.get("id"):
        raise HTTPException(status_code=400, detail="You cannot delete your own account")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Lock the row so the admin-count check can't race with a concurrent change
        cursor.execute("SELECT role FROM users WHERE id = %s FOR UPDATE", (user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user["role"] == "admin":
            cursor.execute("SELECT COUNT(*) as admin_count FROM users WHERE role = 'admin'")
            admin_count = cursor.fetchone()["admin_count"]
            if admin_count <= 1:
                raise HTTPException(status_code=400, detail="Cannot delete the last admin account")

        cursor.execute("DELETE FROM user_data WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM refresh_tokens WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM user_profiles WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM user_preferences WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM notifications WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM subscriptions WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM shared_reports WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM password_reset_tokens WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM login_attempts WHERE username = (SELECT username FROM users WHERE id = %s)", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        invalidate_all_caches()
    finally:
        conn.close()
    log_audit_action(current_admin, "delete_user", "user", user_id)
    return {"status": "success", "message": f"User {user_id} deleted."}


@router.get("/api/admin/courses")
def get_all_courses(current_admin: dict = Depends(get_current_admin)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""SELECT id, field, course_name, course_url, description,
            instructor, rating, duration, price, platform, enrollment_count,
            last_scraped, created_at FROM courses ORDER BY field, id DESC""")
        rows = cursor.fetchall()
    finally:
        conn.close()
    return {"courses": [dict(r) for r in rows]}


@router.post("/api/admin/courses")
def add_course(course: CourseInput, current_admin: dict = Depends(get_current_admin)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO courses (field, course_name, course_url) VALUES (%s, %s, %s)",
            (course.field, course.course_name, course.course_url)
        )
        conn.commit()
        invalidate_all_caches()
    finally:
        conn.close()
    return {"status": "success", "message": "Course added successfully."}


@router.delete("/api/admin/courses/{course_id}")
def delete_course(course_id: int, current_admin: dict = Depends(get_current_admin)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM courses WHERE id = %s", (course_id,))
        conn.commit()
        invalidate_all_caches()
    finally:
        conn.close()
    return {"status": "success", "message": "Course deleted."}


@router.patch("/api/admin/courses/{course_id}")
def update_course(course_id: int, course: CourseInput, current_admin: dict = Depends(get_current_admin)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM courses WHERE id = %s", (course_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Course not found")
        cursor.execute(
            "UPDATE courses SET field = %s, course_name = %s, course_url = %s WHERE id = %s",
            (course.field, course.course_name, course.course_url, course_id)
        )
        conn.commit()
        invalidate_all_caches()
        cursor.execute("SELECT id, field, course_name, course_url, created_at FROM courses WHERE id = %s", (course_id,))
        updated = cursor.fetchone()
    finally:
        conn.close()
    return {"status": "success", "course": dict(updated)}


class ScrapeRequest(BaseModel):
    fields: List[str] = Field(..., min_length=1, max_length=20)
    max_per_platform: int = Field(default=10, ge=1, le=50)


# In-memory scrape status tracking
_scrape_jobs = {}


@router.post("/api/admin/scrape-courses")
def scrape_courses(body: ScrapeRequest, current_admin: dict = Depends(get_current_admin)):
    """Trigger course scraping for specified fields."""
    job_id = f"scrape_{int(__import__('time').time())}"
    _scrape_jobs[job_id] = {"status": "running", "fields": body.fields, "results": {}}

    total_added = 0
    total_updated = 0
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        for field in body.fields:
            try:
                courses = scrape_courses_for_field(field, body.max_per_platform)
                added = 0
                updated = 0
                for course in courses:
                    # Check if course already exists by URL
                    cursor.execute("SELECT id FROM courses WHERE course_url = %s", (course["course_url"],))
                    existing = cursor.fetchone()

                    if existing:
                        # Update existing course
                        cursor.execute(
                            """UPDATE courses SET
                            course_name = %s, description = %s, instructor = %s,
                            rating = %s, duration = %s, price = %s, platform = %s,
                            enrollment_count = %s, last_scraped = CURRENT_TIMESTAMP
                            WHERE course_url = %s""",
                            (
                                course["course_name"], course["description"],
                                course["instructor"], course["rating"],
                                course["duration"], course["price"],
                                course["platform"], course["enrollment_count"],
                                course["course_url"],
                            )
                        )
                        updated += 1
                    else:
                        # Insert new course
                        cursor.execute(
                            """INSERT INTO courses
                            (field, course_name, course_url, description, instructor,
                            rating, duration, price, platform, enrollment_count, last_scraped)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)""",
                            (
                                field, course["course_name"], course["course_url"],
                                course["description"], course["instructor"],
                                course["rating"], course["duration"],
                                course["price"], course["platform"],
                                course["enrollment_count"],
                            )
                        )
                        added += 1

                conn.commit()
                total_added += added
                total_updated += updated
                _scrape_jobs[job_id]["results"][field] = {"added": added, "updated": updated}
                log_audit_action(current_admin, "scrape_courses", "field", field, f"Added: {added}, Updated: {updated}")
            except Exception as e:
                logger.error(f"Scraping failed for field '{field}': {e}")
                _scrape_jobs[job_id]["results"][field] = {"error": str(e)}
    finally:
        conn.close()

    invalidate_all_caches()
    _scrape_jobs[job_id]["status"] = "completed"
    _scrape_jobs[job_id]["summary"] = {"total_added": total_added, "total_updated": total_updated}

    return {
        "status": "success",
        "job_id": job_id,
        "total_added": total_added,
        "total_updated": total_updated,
        "results": _scrape_jobs[job_id]["results"],
    }


@router.get("/api/admin/scrape-status/{job_id}")
def get_scrape_status(job_id: str, current_admin: dict = Depends(get_current_admin)):
    """Get the status of a scraping job."""
    if job_id not in _scrape_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return _scrape_jobs[job_id]


@router.get("/api/admin/scrape-fields")
def get_scrape_fields(current_admin: dict = Depends(get_current_admin)):
    """Get list of fields that can be scraped."""
    return {"fields": list(FIELD_SEARCH_QUERIES.keys())}


@router.get("/api/admin/analytics")
def get_advanced_analytics(current_admin: dict = Depends(get_current_admin)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 1. Most Sought-After Role
        cursor.execute('''
            SELECT target_role, COUNT(*) as count 
            FROM user_data 
            WHERE target_role != 'Unknown' AND target_role != 'None' AND target_role != ''
            GROUP BY target_role 
            ORDER BY count DESC 
            LIMIT 1
        ''')
        top_role_row = cursor.fetchone()
        top_role = top_role_row['target_role'] if top_role_row else "Insufficient Data"
        
        # 2. Most Common Missing Skill
        cursor.execute("SELECT missing_skills FROM user_data WHERE COALESCE(missing_skills, '') != ''")
        all_missing_skills_rows = cursor.fetchall()
        skill_counts = {}
        for row in all_missing_skills_rows:
            skills = [s.strip() for s in (row['missing_skills'] or '').split(',') if s.strip()]
            for s in skills:
                skill_counts[s] = skill_counts.get(s, 0) + 1
                
        top_skill = "Insufficient Data"
        if skill_counts:
            top_skill = max(skill_counts, key=skill_counts.get)
    finally:
        conn.close()
    return {
        "most_sought_role": top_role,
        "most_common_missing_skill": top_skill
    }


@router.get("/api/admin/quality-metrics")
def quality_metrics(current_admin: dict = Depends(get_current_admin)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total_requests FROM request_logs")
        total_requests = cursor.fetchone()["total_requests"]
        cursor.execute("SELECT COUNT(*) as errors FROM request_logs WHERE status_code >= 500")
        errors = cursor.fetchone()["errors"]
        cursor.execute("SELECT AVG(elapsed_ms) as avg_latency FROM request_logs")
        avg_latency = cursor.fetchone()["avg_latency"] or 0
        cursor.execute("SELECT COUNT(*) as uploads FROM user_data")
        uploads = cursor.fetchone()["uploads"]
        cursor.execute("SELECT COUNT(*) as feedback_count FROM user_feedback")
        feedback_count = cursor.fetchone()["feedback_count"]
    finally:
        conn.close()
    return {
        "total_requests": total_requests,
        "server_errors": errors,
        "avg_latency_ms": round(float(avg_latency), 2),
        "resume_uploads": uploads,
        "feedback_events": feedback_count,
        "parse_failure_rate_pct": round((errors / total_requests) * 100, 2) if total_requests else 0.0,
    }


@router.get("/api/admin/analytics/uploads-over-time")
def uploads_over_time(current_admin: dict = Depends(get_current_admin)):
    """Resume uploads grouped by date for the last 30 days."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DATE("Timestamp") as date, COUNT(*) as count
            FROM user_data
            WHERE "Timestamp" IS NOT NULL AND "Timestamp" != ''
            GROUP BY DATE("Timestamp")
            ORDER BY date DESC
            LIMIT 30
        """)
        rows = cursor.fetchall()
    finally:
        conn.close()
    return {"data": [dict(r) for r in reversed(rows)]}


@router.get("/api/admin/analytics/skill-gaps")
def skill_gaps(current_admin: dict = Depends(get_current_admin)):
    """Top missing skills across all analyses."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT missing_skills FROM user_data WHERE COALESCE(missing_skills, '') != ''")
        rows = cursor.fetchall()
        skill_counts = {}
        for row in rows:
            skills = [s.strip() for s in (row["missing_skills"] or "").split(",") if s.strip()]
            for s in skills:
                skill_counts[s] = skill_counts.get(s, 0) + 1
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    finally:
        conn.close()
    return {"data": [{"skill": s, "count": c} for s, c in top_skills]}


@router.get("/api/admin/analytics/role-distribution")
def role_distribution(current_admin: dict = Depends(get_current_admin)):
    """Distribution of target roles chosen by users."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT target_role, COUNT(*) as count
            FROM user_data
            WHERE target_role != 'Unknown' AND target_role != 'None' AND target_role != ''
            GROUP BY target_role
            ORDER BY count DESC
            LIMIT 10
        """)
        rows = cursor.fetchall()
    finally:
        conn.close()
    return {"data": [dict(r) for r in rows]}


@router.get("/api/admin/analytics/user-growth")
def user_growth(current_admin: dict = Depends(get_current_admin)):
    """User registrations grouped by date."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM users
            WHERE created_at IS NOT NULL
            GROUP BY DATE(created_at)
            ORDER BY date DESC
            LIMIT 30
        """)
        rows = cursor.fetchall()
    finally:
        conn.close()
    return {"data": [dict(r) for r in reversed(rows)]}


@router.get("/api/admin/analysis-cache")
def get_analysis_cache(
    current_admin: dict = Depends(get_current_admin),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """List cached analysis results."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT content_hash, target_role, created_at, expires_at FROM analysis_cache ORDER BY created_at DESC LIMIT %s OFFSET %s",
            (limit, offset),
        )
        rows = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) as total FROM analysis_cache")
        total = cursor.fetchone()["total"]
    finally:
        conn.close()
    return {"cache": [dict(r) for r in rows], "total": total, "limit": limit, "offset": offset}


@router.delete("/api/admin/analysis-cache/{content_hash}/{target_role}")
def delete_analysis_cache(content_hash: str, target_role: str, current_admin: dict = Depends(get_current_admin)):
    """Delete a specific analysis cache entry."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analysis_cache WHERE content_hash = %s AND target_role = %s", (content_hash, target_role))
        conn.commit()
        invalidate_all_caches()
    finally:
        conn.close()
    return {"status": "success", "message": "Cache entry deleted."}


@router.get("/api/admin/api-usage")
def api_usage(current_admin: dict = Depends(get_current_admin)):
    """API usage statistics grouped by path."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT path, method, COUNT(*) as count, AVG(elapsed_ms) as avg_ms
            FROM request_logs
            GROUP BY path, method
            ORDER BY count DESC
            LIMIT 20
        """)
        rows = cursor.fetchall()
    finally:
        conn.close()
    return {"data": [dict(r) for r in rows]}


class JobRoleInput(BaseModel):
    title: str = Field(..., max_length=200)
    description: str = Field(default="")
    category: str = Field(default="")
    skills: list[str] = Field(default=[])


@router.get("/api/admin/job-roles")
def get_job_roles(current_admin: dict = Depends(get_current_admin)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description, category, is_active, created_at FROM job_roles ORDER BY title")
        roles = cursor.fetchall()
        result = []
        for role in roles:
            role_dict = dict(role)
            cursor.execute("SELECT id, skill_name, is_required FROM job_role_skills WHERE job_role_id = %s", (role["id"],))
            role_dict["skills"] = [dict(s) for s in cursor.fetchall()]
            cursor.execute("SELECT COUNT(*) as count FROM career_roadmaps WHERE job_role_id = %s", (role["id"],))
            role_dict["roadmap_count"] = cursor.fetchone()["count"]
            result.append(role_dict)
    finally:
        conn.close()
    return {"job_roles": result}


@router.post("/api/admin/job-roles")
def create_job_role(body: JobRoleInput, current_admin: dict = Depends(get_current_admin)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO job_roles (title, description, category) VALUES (%s, %s, %s) RETURNING id",
            (body.title, body.description, body.category)
        )
        role_id = cursor.fetchone()["id"]
        for skill in body.skills:
            cursor.execute(
                "INSERT INTO job_role_skills (job_role_id, skill_name, is_required) VALUES (%s, %s, 1)",
                (role_id, skill)
            )
        conn.commit()
        invalidate_all_caches()
        cursor.execute("SELECT id, title, description, category, is_active, created_at FROM job_roles WHERE id = %s", (role_id,))
        role = dict(cursor.fetchone())
        cursor.execute("SELECT id, skill_name, is_required FROM job_role_skills WHERE job_role_id = %s", (role_id,))
        role["skills"] = [dict(s) for s in cursor.fetchall()]
        role["roadmap_count"] = 0
    finally:
        conn.close()
    return {"status": "success", "job_role": role}


@router.patch("/api/admin/job-roles/{role_id}")
def update_job_role(role_id: int, body: JobRoleInput, current_admin: dict = Depends(get_current_admin)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM job_roles WHERE id = %s", (role_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Job role not found")
        cursor.execute(
            "UPDATE job_roles SET title = %s, description = %s, category = %s WHERE id = %s",
            (body.title, body.description, body.category, role_id)
        )
        cursor.execute("DELETE FROM job_role_skills WHERE job_role_id = %s", (role_id,))
        for skill in body.skills:
            cursor.execute(
                "INSERT INTO job_role_skills (job_role_id, skill_name, is_required) VALUES (%s, %s, 1)",
                (role_id, skill)
            )
        conn.commit()
        invalidate_all_caches()
        cursor.execute("SELECT id, title, description, category, is_active, created_at FROM job_roles WHERE id = %s", (role_id,))
        role = dict(cursor.fetchone())
        cursor.execute("SELECT id, skill_name, is_required FROM job_role_skills WHERE job_role_id = %s", (role_id,))
        role["skills"] = [dict(s) for s in cursor.fetchall()]
        cursor.execute("SELECT COUNT(*) as count FROM career_roadmaps WHERE job_role_id = %s", (role_id,))
        role["roadmap_count"] = cursor.fetchone()["count"]
    finally:
        conn.close()
    return {"status": "success", "job_role": role}


@router.patch("/api/admin/job-roles/{role_id}/status")
def toggle_job_role_status(role_id: int, current_admin: dict = Depends(get_current_admin)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, is_active FROM job_roles WHERE id = %s", (role_id,))
        role = cursor.fetchone()
        if not role:
            raise HTTPException(status_code=404, detail="Job role not found")
        new_status = 0 if role["is_active"] else 1
        cursor.execute("UPDATE job_roles SET is_active = %s WHERE id = %s", (new_status, role_id))
        conn.commit()
        invalidate_all_caches()
    finally:
        conn.close()
    return {"status": "success", "is_active": new_status}


@router.delete("/api/admin/job-roles/{role_id}")
def delete_job_role(role_id: int, current_admin: dict = Depends(get_current_admin)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM job_roles WHERE id = %s", (role_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Job role not found")
        cursor.execute("DELETE FROM job_roles WHERE id = %s", (role_id,))
        conn.commit()
        invalidate_all_caches()
    finally:
        conn.close()
    return {"status": "success", "message": "Job role deleted."}


class RoadmapInput(BaseModel):
    title: str = Field(..., max_length=200)
    description: str = Field(default="")
    duration_weeks: int = Field(default=12)
    steps: list[dict] = Field(default=[])


class BulkRoadmapImport(BaseModel):
    title: str = Field(default="Imported Roadmap", max_length=200)
    description: str = Field(default="", max_length=2000)
    duration_weeks: int = Field(default=12, ge=1, le=52)
    steps_text: str = Field(..., min_length=1, max_length=10000)


@router.get("/api/admin/job-roles/{role_id}/roadmaps")
def get_roadmaps(role_id: int, current_admin: dict = Depends(get_current_admin)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM job_roles WHERE id = %s", (role_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Job role not found")
        cursor.execute(
            "SELECT id, job_role_id, title, description, duration_weeks, sort_order, created_at FROM career_roadmaps WHERE job_role_id = %s ORDER BY sort_order",
            (role_id,)
        )
        roadmaps = []
        for rm in cursor.fetchall():
            rm_dict = dict(rm)
            cursor.execute(
                "SELECT id, step_number, title, description, duration_weeks, skills, resources FROM roadmap_steps WHERE roadmap_id = %s ORDER BY step_number",
                (rm["id"],)
            )
            rm_dict["steps"] = [dict(s) for s in cursor.fetchall()]
            roadmaps.append(rm_dict)
    finally:
        conn.close()
    return {"roadmaps": roadmaps}


@router.post("/api/admin/job-roles/{role_id}/roadmaps")
def create_roadmap(role_id: int, body: RoadmapInput, current_admin: dict = Depends(get_current_admin)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM job_roles WHERE id = %s", (role_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Job role not found")
        cursor.execute("SELECT COALESCE(MAX(sort_order), 0) + 1 AS next_order FROM career_roadmaps WHERE job_role_id = %s", (role_id,))
        _row = cursor.fetchone()
        next_order = _row["next_order"] if _row else 1
        cursor.execute(
            "INSERT INTO career_roadmaps (job_role_id, title, description, duration_weeks, sort_order) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (role_id, body.title, body.description, body.duration_weeks, next_order)
        )
        roadmap_id = cursor.fetchone()["id"]
        for i, step in enumerate(body.steps, 1):
            cursor.execute(
                "INSERT INTO roadmap_steps (roadmap_id, step_number, title, description, duration_weeks, skills, resources) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (roadmap_id, i, step.get("title", ""), step.get("description", ""), step.get("duration_weeks", 2), step.get("skills", ""), step.get("resources", ""))
            )
        conn.commit()
        invalidate_all_caches()
        cursor.execute("SELECT id, job_role_id, title, description, duration_weeks, sort_order, created_at FROM career_roadmaps WHERE id = %s", (roadmap_id,))
        rm = dict(cursor.fetchone())
        cursor.execute("SELECT id, step_number, title, description, duration_weeks, skills, resources FROM roadmap_steps WHERE roadmap_id = %s ORDER BY step_number", (roadmap_id,))
        rm["steps"] = [dict(s) for s in cursor.fetchall()]
    finally:
        conn.close()
    return {"status": "success", "roadmap": rm}


@router.delete("/api/admin/roadmaps/{roadmap_id}")
def delete_roadmap(roadmap_id: int, current_admin: dict = Depends(get_current_admin)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM career_roadmaps WHERE id = %s", (roadmap_id,))
        conn.commit()
        invalidate_all_caches()
    finally:
        conn.close()
    return {"status": "success", "message": "Roadmap deleted."}


ROADMAP_TEMPLATES = {
    "Software Engineering": [
        {
            "title": "Full SWE Career Path",
            "description": "Comprehensive path from fundamentals to system design",
            "duration_weeks": 24,
            "steps": [
                {"title": "Programming Fundamentals", "description": "Master core programming concepts", "duration_weeks": 4, "skills": "Python,OOP,Data Structures,Algorithms", "resources": "https://www.youtube.com/results%ssearch_query=python+programming+fundamentals"},
                {"title": "Version Control & Collaboration", "description": "Git workflows, branching strategies, code reviews", "duration_weeks": 2, "skills": "Git,GitHub,Pull Requests,Code Review", "resources": "https://www.youtube.com/results%ssearch_query=git+tutorial"},
                {"title": "Testing & Quality Assurance", "description": "Write reliable, tested code with TDD", "duration_weeks": 3, "skills": "Unit Testing,Integration Testing,TDD,Pytest", "resources": "https://www.youtube.com/results%ssearch_query=software+testing"},
                {"title": "APIs & Backend Basics", "description": "REST APIs, authentication, middleware", "duration_weeks": 4, "skills": "REST,HTTP,Authentication,JSON", "resources": "https://www.youtube.com/results%ssearch_query=rest+api+tutorial"},
                {"title": "Databases & SQL", "description": "Relational and NoSQL databases", "duration_weeks": 3, "skills": "SQL,PostgreSQL,MongoDB,ORM", "resources": "https://www.youtube.com/results%ssearch_query=sql+tutorial"},
                {"title": "System Design", "description": "Design scalable, distributed systems", "duration_weeks": 5, "skills": "Architecture,Microservices,Caching,Load Balancing", "resources": "https://www.youtube.com/results%ssearch_query=system+design"},
                {"title": "DevOps & Deployment", "description": "CI/CD, containers, cloud deployment", "duration_weeks": 3, "skills": "Docker,Kubernetes,CI/CD,AWS", "resources": "https://www.youtube.com/results%ssearch_query=devops+tutorial"},
            ]
        }
    ],
    "Frontend Development": [
        {
            "title": "Modern Frontend Developer",
            "description": "From HTML basics to React mastery",
            "duration_weeks": 20,
            "steps": [
                {"title": "HTML & CSS Foundations", "description": "Semantic HTML, CSS Grid, Flexbox", "duration_weeks": 3, "skills": "HTML5,CSS3,Flexbox,Grid,Responsive Design", "resources": "https://www.youtube.com/results%ssearch_query=html+css+tutorial"},
                {"title": "JavaScript Essentials", "description": "ES6+, DOM manipulation, async/await", "duration_weeks": 4, "skills": "JavaScript,ES6+,DOM,Async/Await,Promises", "resources": "https://www.youtube.com/results%ssearch_query=javascript+tutorial"},
                {"title": "React & Components", "description": "Component architecture, hooks, state management", "duration_weeks": 5, "skills": "React,Hooks,Context API,State Management", "resources": "https://www.youtube.com/results%ssearch_query=react+tutorial"},
                {"title": "TypeScript", "description": "Type-safe JavaScript development", "duration_weeks": 3, "skills": "TypeScript,Generics,Interfaces,Types", "resources": "https://www.youtube.com/results%ssearch_query=typescript+tutorial"},
                {"title": "Testing Frontend Apps", "description": "Unit and integration testing", "duration_weeks": 2, "skills": "Jest,React Testing Library,Cypress", "resources": "https://www.youtube.com/results%ssearch_query=frontend+testing"},
                {"title": "Performance Optimization", "description": "Core Web Vitals, lazy loading, code splitting", "duration_weeks": 3, "skills": "Lighthouse,Webpack,Code Splitting,Optimization", "resources": "https://www.youtube.com/results%ssearch_query=web+performance"},
            ]
        }
    ],
    "Backend Development": [
        {
            "title": "Backend Developer Mastery",
            "description": "Build robust, scalable server-side applications",
            "duration_weeks": 22,
            "steps": [
                {"title": "Language & Framework", "description": "Master a backend language (Python/Node.js/Go)", "duration_weeks": 4, "skills": "Python,Node.js,FastAPI,Express", "resources": "https://www.youtube.com/results%ssearch_query=backend+programming"},
                {"title": "Database Design", "description": "Schema design, indexing, query optimization", "duration_weeks": 4, "skills": "SQL,PostgreSQL,MongoDB,Indexing,ORM", "resources": "https://www.youtube.com/results%ssearch_query=database+design"},
                {"title": "RESTful API Design", "description": "API standards, versioning, documentation", "duration_weeks": 3, "skills": "REST,OpenAPI,GraphQL,Versioning", "resources": "https://www.youtube.com/results%ssearch_query=rest+api+design"},
                {"title": "Authentication & Security", "description": "JWT, OAuth, input validation, rate limiting", "duration_weeks": 3, "skills": "JWT,OAuth,Encryption,Rate Limiting", "resources": "https://www.youtube.com/results%ssearch_query=api+security"},
                {"title": "Caching & Performance", "description": "Redis, CDN, query optimization", "duration_weeks": 3, "skills": "Redis,CDN,Query Optimization,Connection Pooling", "resources": "https://www.youtube.com/results%ssearch_query=caching+tutorial"},
                {"title": "Containerization & Deployment", "description": "Docker, cloud services, monitoring", "duration_weeks": 5, "skills": "Docker,AWS,GCP,Monitoring,Logging", "resources": "https://www.youtube.com/results%ssearch_query=docker+deployment"},
            ]
        }
    ],
    "Data Science": [
        {
            "title": "Data Scientist Path",
            "description": "From data analysis to machine learning",
            "duration_weeks": 26,
            "steps": [
                {"title": "Python for Data", "description": "NumPy, Pandas, data manipulation", "duration_weeks": 4, "skills": "Python,NumPy,Pandas,Data Cleaning", "resources": "https://www.youtube.com/results%ssearch_query=python+data+science"},
                {"title": "Statistics & Probability", "description": "Statistical concepts for analysis", "duration_weeks": 4, "skills": "Statistics,Probability,Hypothesis Testing,Distributions", "resources": "https://www.youtube.com/results%ssearch_query=statistics+data+science"},
                {"title": "Data Visualization", "description": "Matplotlib, Seaborn, Plotly", "duration_weeks": 3, "skills": "Matplotlib,Seaborn,Plotly,Tableau", "resources": "https://www.youtube.com/results%ssearch_query=data+visualization"},
                {"title": "Machine Learning", "description": "Supervised and unsupervised learning", "duration_weeks": 6, "skills": "Scikit-learn,Regression,Classification,Clustering", "resources": "https://www.youtube.com/results%ssearch_query=machine+learning+tutorial"},
                {"title": "Deep Learning", "description": "Neural networks, CNNs, RNNs", "duration_weeks": 5, "skills": "TensorFlow,PyTorch,Neural Networks,CNN", "resources": "https://www.youtube.com/results%ssearch_query=deep+learning+tutorial"},
                {"title": "MLOps & Deployment", "description": "Model deployment, monitoring, A/B testing", "duration_weeks": 4, "skills": "MLflow,Docker,API Integration,Monitoring", "resources": "https://www.youtube.com/results%ssearch_query=mlops+tutorial"},
            ]
        }
    ],
    "DevOps": [
        {
            "title": "DevOps Engineer Path",
            "description": "Master infrastructure automation and deployment",
            "duration_weeks": 24,
            "steps": [
                {"title": "Linux & Networking", "description": "OS fundamentals, networking protocols", "duration_weeks": 4, "skills": "Linux,Bash,TCP/IP,DNS,HTTP", "resources": "https://www.youtube.com/results%ssearch_query=linux+tutorial"},
                {"title": "Scripting & Automation", "description": "Python/Bash scripting for automation", "duration_weeks": 3, "skills": "Python,Bash,Ansible,Automation", "resources": "https://www.youtube.com/results%ssearch_query=devops+scripting"},
                {"title": "Containers", "description": "Docker, container orchestration", "duration_weeks": 4, "skills": "Docker,Docker Compose,Containerization", "resources": "https://www.youtube.com/results%ssearch_query=docker+tutorial"},
                {"title": "Kubernetes", "description": "Container orchestration at scale", "duration_weeks": 5, "skills": "Kubernetes,Helm,Pods,Services,Ingress", "resources": "https://www.youtube.com/results%ssearch_query=kubernetes+tutorial"},
                {"title": "CI/CD Pipelines", "description": "Automated testing and deployment", "duration_weeks": 4, "skills": "GitHub Actions,Jenkins,GitLab CI,Pipelines", "resources": "https://www.youtube.com/results%ssearch_query=ci+cd+tutorial"},
                {"title": "Cloud Platforms", "description": "AWS/Azure/GCP services and architecture", "duration_weeks": 4, "skills": "AWS,Azure,GCP,Terraform,IaC", "resources": "https://www.youtube.com/results%ssearch_query=aws+cloud+tutorial"},
            ]
        }
    ],
    "Mobile Development": [
        {
            "title": "Mobile Developer Path",
            "description": "Build cross-platform mobile applications",
            "duration_weeks": 22,
            "steps": [
                {"title": "Mobile Fundamentals", "description": "App architecture, lifecycle, UI principles", "duration_weeks": 3, "skills": "Mobile UX,App Architecture,State Management", "resources": "https://www.youtube.com/results%ssearch_query=mobile+development+basics"},
                {"title": "Cross-Platform Framework", "description": "React Native or Flutter", "duration_weeks": 6, "skills": "React Native,Flutter,Dart,Components", "resources": "https://www.youtube.com/results%ssearch_query=react+native+tutorial"},
                {"title": "Backend Integration", "description": "APIs, authentication, local storage", "duration_weeks": 4, "skills": "REST APIs,Firebase,JWT,AsyncStorage", "resources": "https://www.youtube.com/results%ssearch_query=mobile+backend+integration"},
                {"title": "UI/UX & Navigation", "description": "Polished interfaces and navigation patterns", "duration_weeks": 3, "skills": "React Navigation,Animations,Gestures", "resources": "https://www.youtube.com/results%ssearch_query=mobile+ui+design"},
                {"title": "Testing & Debugging", "description": "Unit tests, integration tests, debugging tools", "duration_weeks": 3, "skills": "Jest,Detox,Flipper,Debugging", "resources": "https://www.youtube.com/results%ssearch_query=mobile+testing"},
                {"title": "Publishing & Maintenance", "description": "App Store, Play Store, analytics", "duration_weeks": 3, "skills": "App Store,Play Store,Analytics,Beta Testing", "resources": "https://www.youtube.com/results%ssearch_query=app+store+publishing"},
            ]
        }
    ],
    "Full Stack Development": [
        {
            "title": "Full Stack Developer Path",
            "description": "Master both frontend and backend development",
            "duration_weeks": 28,
            "steps": [
                {"title": "Frontend Foundations", "description": "HTML, CSS, JavaScript, React", "duration_weeks": 5, "skills": "HTML,CSS,JavaScript,React,Responsive Design", "resources": "https://www.youtube.com/results%ssearch_query=frontend+web+development"},
                {"title": "Backend Foundations", "description": "Node.js, Express, server-side logic", "duration_weeks": 4, "skills": "Node.js,Express,REST APIs,Middleware", "resources": "https://www.youtube.com/results%ssearch_query=nodejs+backend+tutorial"},
                {"title": "Database Design", "description": "SQL, MongoDB, data modeling", "duration_weeks": 4, "skills": "SQL,MongoDB,Schema Design,Queries", "resources": "https://www.youtube.com/results%ssearch_query=database+tutorial"},
                {"title": "Authentication & Security", "description": "JWT, sessions, security best practices", "duration_weeks": 3, "skills": "JWT,Sessions,OAuth,Security", "resources": "https://www.youtube.com/results%ssearch_query=authentication+tutorial"},
                {"title": "Full Stack Integration", "description": "Connect frontend and backend", "duration_weeks": 5, "skills": "API Integration,State Management,Error Handling", "resources": "https://www.youtube.com/results%ssearch_query=full+stack+integration"},
                {"title": "Testing & Deployment", "description": "End-to-end testing, CI/CD, hosting", "duration_weeks": 4, "skills": "Jest,Cypress,Docker,Deployment", "resources": "https://www.youtube.com/results%ssearch_query=full+stack+deployment"},
                {"title": "Advanced Topics", "description": "WebSockets, real-time, performance", "duration_weeks": 3, "skills": "WebSockets,Real-time,Caching,Performance", "resources": "https://www.youtube.com/results%ssearch_query=advanced+web+development"},
            ]
        }
    ],
    "Cybersecurity": [
        {
            "title": "Cybersecurity Analyst Path",
            "description": "Protect systems from security threats",
            "duration_weeks": 26,
            "steps": [
                {"title": "Networking Fundamentals", "description": "TCP/IP, protocols, network security", "duration_weeks": 4, "skills": "TCP/IP,HTTP,DNS,Firewalls,VPN", "resources": "https://www.youtube.com/results%ssearch_query=network+security+tutorial"},
                {"title": "Operating Systems Security", "description": "Linux and Windows hardening", "duration_weeks": 4, "skills": "Linux,Windows,Hardening,Permissions", "resources": "https://www.youtube.com/results%ssearch_query=linux+security"},
                {"title": "Security Tools", "description": "SIEM, vulnerability scanners, packet analyzers", "duration_weeks": 4, "skills": "SIEM,Nmap,Wireshark,MetaSploit", "resources": "https://www.youtube.com/results%ssearch_query=security+tools"},
                {"title": "Ethical Hacking", "description": "Penetration testing methodologies", "duration_weeks": 5, "skills": "Kali Linux,Penetration Testing,Exploits,Recon", "resources": "https://www.youtube.com/results%ssearch_query=ethical+hacking+tutorial"},
                {"title": "Cryptography", "description": "Encryption, hashing, PKI", "duration_weeks": 4, "skills": "Encryption,Hashing,SSL/TLS,PKI", "resources": "https://www.youtube.com/results%ssearch_query=cryptography+tutorial"},
                {"title": "Incident Response", "description": "Detection, containment, recovery", "duration_weeks": 5, "skills": "Incident Response,Forensics,Compliance,Reporting", "resources": "https://www.youtube.com/results%ssearch_query=incident+response"},
            ]
        }
    ],
}


@router.get("/api/admin/roadmap-templates")
def get_roadmap_templates(current_admin: dict = Depends(get_current_admin)):
    return {"templates": ROADMAP_TEMPLATES}


@router.post("/api/admin/job-roles/{role_id}/roadmaps/bulk")
def bulk_import_roadmap(role_id: int, body: BulkRoadmapImport, current_admin: dict = Depends(get_current_admin)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM job_roles WHERE id = %s", (role_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Job role not found")

        title = body.title
        description = body.description
        duration_weeks = body.duration_weeks
        raw_text = body.steps_text

        steps = []
        for line in raw_text.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            step = {
                "title": parts[0] if len(parts) > 0 else "",
                "description": parts[1] if len(parts) > 1 else "",
                "duration_weeks": int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 2,
                "skills": parts[3] if len(parts) > 3 else "",
                "resources": parts[4] if len(parts) > 4 else "",
            }
            if step["title"]:
                steps.append(step)

        if not steps:
            raise HTTPException(status_code=400, detail="No valid steps found. Use format: Title | Description | Weeks | Skills | Resources")

        cursor.execute("SELECT COALESCE(MAX(sort_order), 0) + 1 AS next_order FROM career_roadmaps WHERE job_role_id = %s", (role_id,))
        _row = cursor.fetchone()
        next_order = _row["next_order"] if _row else 1
        cursor.execute(
            "INSERT INTO career_roadmaps (job_role_id, title, description, duration_weeks, sort_order) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (role_id, title, description, duration_weeks, next_order)
        )
        roadmap_id = cursor.fetchone()["id"]
        for i, step in enumerate(steps, 1):
            cursor.execute(
                "INSERT INTO roadmap_steps (roadmap_id, step_number, title, description, duration_weeks, skills, resources) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (roadmap_id, i, step["title"], step["description"], step["duration_weeks"], step["skills"], step["resources"])
            )
        conn.commit()
        invalidate_all_caches()
        cursor.execute("SELECT id, job_role_id, title, description, duration_weeks, sort_order, created_at FROM career_roadmaps WHERE id = %s", (roadmap_id,))
        rm = dict(cursor.fetchone())
        cursor.execute("SELECT id, step_number, title, description, duration_weeks, skills, resources FROM roadmap_steps WHERE roadmap_id = %s ORDER BY step_number", (roadmap_id,))
        rm["steps"] = [dict(s) for s in cursor.fetchall()]
    finally:
        conn.close()
    return {"status": "success", "roadmap": rm, "steps_imported": len(steps)}


@router.post("/api/admin/job-roles/{role_id}/roadmaps/ai-generate")
def ai_generate_roadmap(role_id: int, current_admin: dict = Depends(get_current_admin)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description FROM job_roles WHERE id = %s", (role_id,))
        role = cursor.fetchone()
        if not role:
            raise HTTPException(status_code=404, detail="Job role not found")

        cursor.execute("SELECT skill_name FROM job_role_skills WHERE job_role_id = %s", (role_id,))
        skills = [row['skill_name'] for row in cursor.fetchall()]

        role_title = role['title']
        role_desc = role['description'] or ''
    finally:
        conn.close()

    try:
        from api.main import generate_roadmap_with_ai
        roadmap_data = generate_roadmap_with_ai(role_title, role_desc, skills)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(MAX(sort_order), 0) + 1 AS next_order FROM career_roadmaps WHERE job_role_id = %s", (role_id,))
        _row = cursor.fetchone()
        next_order = _row["next_order"] if _row else 1
        cursor.execute(
            "INSERT INTO career_roadmaps (job_role_id, title, description, duration_weeks, sort_order) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (role_id, roadmap_data.get("title", f"{role_title} Roadmap"), roadmap_data.get("description", ""), roadmap_data.get("duration_weeks", 16), next_order)
        )
        roadmap_id = cursor.fetchone()["id"]
        for i, step in enumerate(roadmap_data.get("steps", []), 1):
            cursor.execute(
                "INSERT INTO roadmap_steps (roadmap_id, step_number, title, description, duration_weeks, skills, resources) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (roadmap_id, i, step.get("title", ""), step.get("description", ""), step.get("duration_weeks", 2), step.get("skills", ""), step.get("resources", ""))
            )
        conn.commit()
        invalidate_all_caches()
        cursor.execute("SELECT id, job_role_id, title, description, duration_weeks, sort_order, created_at FROM career_roadmaps WHERE id = %s", (roadmap_id,))
        rm = dict(cursor.fetchone())
        cursor.execute("SELECT id, step_number, title, description, duration_weeks, skills, resources FROM roadmap_steps WHERE roadmap_id = %s ORDER BY step_number", (roadmap_id,))
        rm["steps"] = [dict(s) for s in cursor.fetchall()]
    finally:
        conn.close()
    return {"status": "success", "roadmap": rm}


@router.get("/api/admin/audit-logs")
def get_audit_logs(
    current_admin: dict = Depends(get_current_admin),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """List audit logs of admin actions."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, admin_username, action, target_type, target_id, details, ip_address, created_at FROM audit_logs ORDER BY id DESC LIMIT %s OFFSET %s",
            (limit, offset),
        )
        rows = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) as total FROM audit_logs")
        total = cursor.fetchone()["total"]
    finally:
        conn.close()
    return {"logs": [dict(r) for r in rows], "total": total, "limit": limit, "offset": offset}


class PasswordResetInput(BaseModel):
    user_id: int
    new_password: str = Field(..., min_length=8)


@router.post("/api/admin/reset-password")
def admin_reset_password(body: PasswordResetInput, current_admin: dict = Depends(get_current_admin)):
    """Admin reset a user's password."""
    from api.security import get_password_hash
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM users WHERE id = %s", (body.user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        hashed = get_password_hash(body.new_password)
        cursor.execute("UPDATE users SET hashed_password = %s WHERE id = %s", (hashed, body.user_id))
        cursor.execute("DELETE FROM refresh_tokens WHERE user_id = %s", (body.user_id,))
        conn.commit()
    finally:
        conn.close()
    log_audit_action(current_admin, "reset_password", "user", body.user_id)
    return {"status": "success", "message": f"Password reset for {user['username']}."}


@router.get("/api/admin/export/{table_name}")
def export_table(table_name: str, current_admin: dict = Depends(get_current_admin)):
    """Export a table as JSON."""
    allowed_tables = [
        "users", "user_data", "courses", "user_feedback", "job_roles", "audit_logs",
        "skill_categories", "skills", "role_synonyms", "skill_aliases",
        "field_keywords", "industry_trends", "market_role_aliases",
        "skill_recommendations", "roadmap_templates", "learning_actions",
        "learning_resources", "skill_difficulty", "skill_clusters",
        "video_resources", "role_configs", "job_role_skills",
        "career_roadmaps", "roadmap_steps", "user_profiles",
        "user_preferences", "user_roadmap_progress", "notifications",
        "subscriptions", "shared_reports", "request_logs",
    ]
    if table_name not in allowed_tables:
        raise HTTPException(status_code=400, detail=f"Cannot export table: {table_name}")
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            sql.SQL("SELECT * FROM {} LIMIT 1000").format(sql.Identifier(table_name))
        )
        rows = cursor.fetchall()
    finally:
        conn.close()
    return {"table": table_name, "count": len(rows), "data": [dict(r) for r in rows]}


# ============================================================
# Taxonomy data view endpoints
# ============================================================

@router.get("/api/admin/taxonomy/overview")
def get_taxonomy_overview(current_admin: dict = Depends(get_current_admin)):
    """Get overview of all taxonomy tables."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        tables = {
            "skill_categories": "SELECT COUNT(*) as count FROM skill_categories",
            "skills": "SELECT COUNT(*) as count FROM skills",
            "role_synonyms": "SELECT COUNT(*) as count FROM role_synonyms",
            "skill_aliases": "SELECT COUNT(*) as count FROM skill_aliases",
            "field_keywords": "SELECT COUNT(*) as count FROM field_keywords",
            "industry_trends": "SELECT COUNT(*) as count FROM industry_trends",
            "market_role_aliases": "SELECT COUNT(*) as count FROM market_role_aliases",
            "skill_recommendations": "SELECT COUNT(*) as count FROM skill_recommendations",
            "roadmap_templates": "SELECT COUNT(*) as count FROM roadmap_templates",
            "learning_actions": "SELECT COUNT(*) as count FROM learning_actions",
            "learning_resources": "SELECT COUNT(*) as count FROM learning_resources",
            "skill_difficulty": "SELECT COUNT(*) as count FROM skill_difficulty",
            "skill_clusters": "SELECT COUNT(*) as count FROM skill_clusters",
            "video_resources": "SELECT COUNT(*) as count FROM video_resources",
            "role_configs": "SELECT COUNT(*) as count FROM role_configs",
        }
        result = {}
        for table, query in tables.items():
            cursor.execute(query)
            result[table] = cursor.fetchone()["count"]
        return result
    finally:
        conn.close()


@router.get("/api/admin/taxonomy/skills")
def get_taxonomy_skills(current_admin: dict = Depends(get_current_admin)):
    """Get all skills organized by category."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sc.name as category, s.name as skill
            FROM skill_categories sc
            JOIN skills s ON sc.id = s.category_id
            ORDER BY sc.sort_order, s.sort_order
        """)
        result = {}
        for row in cursor.fetchall():
            if row["category"] not in result:
                result[row["category"]] = []
            result[row["category"]].append(row["skill"])
        return result
    finally:
        conn.close()


@router.get("/api/admin/taxonomy/roadmaps")
def get_taxonomy_roadmaps(current_admin: dict = Depends(get_current_admin)):
    """Get all roadmap templates."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT field_name, step_number, title, duration, skills
            FROM roadmap_templates
            ORDER BY field_name, step_number
        """)
        result = {}
        for row in cursor.fetchall():
            if row["field_name"] not in result:
                result[row["field_name"]] = []
            result[row["field_name"]].append({
                "step": row["step_number"],
                "title": row["title"],
                "duration": row["duration"],
                "skills": json.loads(row["skills"]),
            })
        return result
    finally:
        conn.close()


@router.get("/api/admin/taxonomy/role-configs")
def get_taxonomy_role_configs(current_admin: dict = Depends(get_current_admin)):
    """Get all role configurations."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM role_configs ORDER BY role_key")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


@router.get("/api/admin/taxonomy/video-resources")
def get_taxonomy_video_resources(
    video_type: Optional[str] = Query(None),
    current_admin: dict = Depends(get_current_admin)
):
    """Get video resources, optionally filtered by type."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if video_type:
            cursor.execute(
                "SELECT * FROM video_resources WHERE video_type = %s ORDER BY field_name, sort_order",
                (video_type,)
            )
        else:
            cursor.execute("SELECT * FROM video_resources ORDER BY field_name, video_type, sort_order")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()
