from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import time
import uuid
import logging

from api.database import get_db_connection, get_db
from api.auth import client_ip
from api.exceptions import SkillPathException
from api.mock_interview import router as mock_interview_router
from api.mock_interview_ai import router as mock_interview_ai_router
from api.routes.auth import router as auth_router
from api.routes.analysis import router as analysis_router
from api.routes.admin import router as admin_router
from api.routes.health import router as health_router
from api.routes.user import router as user_router
from api.routes.sharing import router as sharing_router
from api.routes.jobs import router as jobs_router
from api.routes.misc import router as misc_router
import json

# ---------------------------------------------------------------------------
# Startup env validation – fail fast with clear messages
# ---------------------------------------------------------------------------
def _validate_env():
    errors = []

    env = os.getenv("ENV", "development").lower()
    is_prod = env in ("production", "prod")

    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if not gemini_key or gemini_key == "test-key":
        if is_prod:
            errors.append("GEMINI_API_KEY is required in production.")
        else:
            logger.warning("GEMINI_API_KEY is missing or dummy – Gemini analysis will be unavailable.")

    jwt_secret = os.getenv("JWT_SECRET_KEY", "")
    if not jwt_secret or len(jwt_secret) < 32:
        if is_prod:
            errors.append("JWT_SECRET_KEY must be >= 32 characters in production.")
        else:
            logger.warning("JWT_SECRET_KEY is missing or short – using random key (sessions reset on restart).")

    db_file = os.getenv("DB_FILE") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "cv.db"
    )
    db_dir = os.path.dirname(db_file) or "."
    if not os.access(db_dir, os.W_OK):
        errors.append(f"DB_FILE directory is not writable: {db_dir}")

    cors_raw = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    if is_prod and "*" in cors_raw:
        errors.append("CORS_ORIGINS must not include '*' in production.")

    if errors:
        msg = "Startup validation failed:\n  - " + "\n  - ".join(errors)
        logger.error(msg)
        raise RuntimeError(msg)

# ---------------------------------------------------------------------------

app = FastAPI(title="AI Resume Analyzer API")

@app.exception_handler(SkillPathException)
async def skillpath_exception_handler(request: Request, exc: SkillPathException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "code": exc.code,
            "status": "error"
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "code": f"HTTP_{exc.status_code}",
            "status": "error"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "An unexpected error occurred. Our engineers have been notified.",
            "code": "INTERNAL_SERVER_ERROR",
            "status": "error"
        }
    )


def generate_roadmap_with_ai(role_title: str, role_description: str, skills: list) -> dict:
    """Generate a career roadmap using the configured AI provider chain."""
    import json
    from api.ai_provider import generate_json
    skills_str = ", ".join(skills[:10]) if skills else "general skills"
    prompt = f"""Generate a detailed career roadmap for a {role_title} position.

Role Description: {role_description}
Key Skills: {skills_str}

Return ONLY a JSON object (no markdown, no code fences) with this exact structure:
{{
    "title": "Career Roadmap for {role_title}",
    "description": "A structured path to master {role_title}",
    "duration_weeks": <total_weeks>,
    "steps": [
        {{
            "title": "Step title",
            "description": "What to learn in this step",
            "duration_weeks": <weeks>,
            "skills": "Skill1,Skill2,Skill3",
            "resources": "https://www.youtube.com/results?search_query=<topic>+tutorial"
        }}
    ]
}}

Create 5-8 progressive steps from fundamentals to advanced topics. Each step should build on the previous one.
Include relevant YouTube search URLs as resources.
Be specific to {role_title} - don't use generic advice."""

    try:
        data = generate_json(prompt, temperature=0.7)
        if data:
            return data
    except Exception as e:
        logger.error(f"AI roadmap generation failed: {e}")
    return {
            "title": f"{role_title} Roadmap",
            "description": role_description or f"Career path for {role_title}",
            "duration_weeks": 16,
            "steps": [
                {"title": "Fundamentals", "description": "Learn core concepts", "duration_weeks": 4, "skills": skills_str if skills else "Fundamentals", "resources": f"https://www.youtube.com/results?search_query={role_title.replace(' ', '+')}+fundamentals"},
                {"title": "Intermediate", "description": "Build practical skills", "duration_weeks": 4, "skills": "Intermediate Skills", "resources": f"https://www.youtube.com/results?search_query={role_title.replace(' ', '+')}+intermediate"},
                {"title": "Advanced", "description": "Master advanced topics", "duration_weeks": 4, "skills": "Advanced Skills", "resources": f"https://www.youtube.com/results?search_query={role_title.replace(' ', '+')}+advanced"},
                {"title": "Projects", "description": "Build real-world projects", "duration_weeks": 4, "skills": "Project Building,Portfolio", "resources": f"https://www.youtube.com/results?search_query={role_title.replace(' ', '+')}+projects"},
            ]
        }


app.include_router(mock_interview_ai_router)
app.include_router(mock_interview_router)
app.include_router(auth_router)
app.include_router(analysis_router)
app.include_router(admin_router)
app.include_router(health_router)
app.include_router(user_router)
app.include_router(sharing_router)
app.include_router(jobs_router)
app.include_router(misc_router)

logger = logging.getLogger("resume-analyzer")
logging.basicConfig(level=logging.INFO)

# Seed skills taxonomy and load cache
from api.seeders import (
    seed_skills_taxonomy, seed_market_data, seed_skill_recommendations,
    seed_roadmap_templates, seed_learning_actions, seed_learning_resources,
    seed_skill_difficulty, seed_skill_clusters, seed_video_resources,
    seed_role_configs, seed_courses,
)
from api.seed_data import (
    load_skills_cache, load_market_cache, load_skill_recs_cache,
    load_roadmaps_cache, load_actions_cache, load_resources_cache,
    load_difficulty_cache, load_clusters_cache, load_videos_cache,
    load_role_configs_cache,
)
seed_skills_taxonomy()
load_skills_cache()
seed_market_data()
load_market_cache()
seed_skill_recommendations()
load_skill_recs_cache()
seed_roadmap_templates()
load_roadmaps_cache()
seed_learning_actions()
load_actions_cache()
seed_learning_resources()
load_resources_cache()
seed_skill_difficulty()
load_difficulty_cache()
seed_skill_clusters()
load_clusters_cache()
seed_video_resources()
load_videos_cache()
seed_role_configs()
load_role_configs_cache()
seed_courses()

_validate_env()

RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))
_last_rate_limit_cleanup = 0
RATE_LIMIT_CLEANUP_INTERVAL = 300  # 5 minutes
ENV = os.getenv("ENV", "development").lower()
IS_PROD = ENV in ("production", "prod")

_raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
CORS_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip() and o.strip() != "*"]
if IS_PROD and "*" in _raw_origins:
    raise RuntimeError("CORS_ORIGINS must not include '*' in production.")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Cookie", "X-Requested-With"],
    max_age=600,
)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' https:; "
        "frame-ancestors 'none'; "
        "base-uri 'self';"
    )
    return response




@app.middleware("http")
async def request_logging_and_rate_limit(request: Request, call_next):
    global _last_rate_limit_cleanup
    if request.method == "OPTIONS":
        return await call_next(request)

    request_ip = client_ip(request)
    now_minute = int(time.time() // 60)
    bucket_key = f"{request_ip}:{now_minute}"

    try:
        with get_db() as conn:
            cursor = conn.cursor()
            # Periodic cleanup instead of per-request
            now = int(time.time())
            if now - _last_rate_limit_cleanup > RATE_LIMIT_CLEANUP_INTERVAL:
                cursor.execute("DELETE FROM rate_limits WHERE updated_at < ?", (now_minute - 2,))
                _last_rate_limit_cleanup = now
            cursor.execute(
                "INSERT INTO rate_limits (key, count, updated_at) VALUES (?, 1, ?) "
                "ON CONFLICT(key) DO UPDATE SET count = count + 1, updated_at = ?",
                (bucket_key, now_minute, now_minute),
            )
            cursor.execute("SELECT count FROM rate_limits WHERE key = ?", (bucket_key,))
            row = cursor.fetchone()
            count = row["count"] if row else 1
            conn.commit()
            if count > RATE_LIMIT_PER_MINUTE:
                raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again in a minute.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rate limit error: {e}")

    start = time.perf_counter()
    request_id = str(uuid.uuid4())
    response = await call_next(request)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        json.dumps(
            {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "elapsed_ms": elapsed_ms,
            }
        )
    )
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO request_logs(request_id, method, path, status_code, elapsed_ms) VALUES (?, ?, ?, ?, ?)",
                (request_id, request.method, request.url.path, response.status_code, elapsed_ms),
            )
            conn.commit()
    except Exception as log_err:
        logger.warning(f"Failed to log request: {log_err}")
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
    return response






