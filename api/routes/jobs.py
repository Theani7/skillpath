import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.auth import get_current_optional_user, get_current_user
from api.career_services import generate_interview_questions, generate_job_matches, rank_candidates
from api.cover_letter import generate_cover_letter
from api.database import get_db_connection
from api.extractor import rewrite_resume_with_gemini, simulate_interview_turn
from api.skill_matching import compare_resume_to_jd
from api.roadmap_services import recommend_projects
from api.resume_parser import rewrite_resume_fallback
from api.career_services import rewrite_resume_bullets_fallback

logger = logging.getLogger("resume-analyzer")

router = APIRouter(tags=["jobs"])


class JobMatchRequest(BaseModel):
    target_role: str = Field(..., max_length=200)
    skills: list[str] = Field(default_factory=list, max_length=200)
    missing_skills: list[str] = Field(default_factory=list, max_length=200)


class InterviewRequest(BaseModel):
    target_role: str = Field(..., max_length=200)
    skills: list[str] = Field(default_factory=list, max_length=200)
    missing_skills: list[str] = Field(default_factory=list, max_length=200)


class InterviewSimulatorRequest(BaseModel):
    resume_data: dict
    target_role: str = Field(..., max_length=200)
    chat_history: list[dict] = Field(default_factory=list, max_length=50)


class RewriteRequest(BaseModel):
    target_role: Optional[str] = Field(default=None, max_length=200)
    resume_data: dict


class CandidateRankRequest(BaseModel):
    target_role: str = Field(..., max_length=200)
    candidates: list[dict] = Field(..., max_length=200)


class JDCompareRequest(BaseModel):
    resume_skills: list[str] = Field(default_factory=list, max_length=200)
    job_description: str = Field(..., max_length=20000)


class ProjectRecommendationRequest(BaseModel):
    target_role: str = Field(..., max_length=200)
    missing_skills: list[str] = Field(default_factory=list, max_length=200)


class CoverLetterRequest(BaseModel):
    resume_data: dict = Field(..., description="Parsed resume data from analysis")
    target_role: str = Field(..., max_length=200)
    company_name: str = Field(default="", max_length=200)
    job_description: str = Field(default="", max_length=20000)
    hiring_manager: str = Field(default="", max_length=200)


@router.post("/api/jobs/matches")
def get_job_matches(payload: JobMatchRequest, current_user: dict = Depends(get_current_optional_user)):
    jobs = generate_job_matches(payload.target_role, payload.skills, payload.missing_skills)
    return {"target_role": payload.target_role, "jobs": jobs}


@router.post("/api/interview/copilot")
def interview_copilot(payload: InterviewRequest, current_user: dict = Depends(get_current_optional_user)):
    questions = generate_interview_questions(payload.target_role, payload.missing_skills, payload.skills)
    return {"target_role": payload.target_role, "questions": questions}


@router.post("/api/interview/simulate")
def interview_simulator(payload: InterviewSimulatorRequest, current_user: dict = Depends(get_current_optional_user)):
    result = simulate_interview_turn(payload.resume_data, payload.target_role, payload.chat_history)
    return result


@router.post("/api/rewrite-resume")
def rewrite_resume(payload: RewriteRequest, current_user: dict = Depends(get_current_optional_user)):
    try:
        rewritten = rewrite_resume_with_gemini(payload.resume_data, payload.target_role)
    except Exception as e:
        logger.warning(f"Gemini rewrite failed, using fallback: {e}")
        rewritten = rewrite_resume_fallback(payload.resume_data, payload.target_role)
    if not rewritten:
        rewritten = rewrite_resume_bullets_fallback(payload.resume_data, payload.target_role or "General")
    return rewritten


@router.post("/api/team/rank-candidates")
def team_rank_candidates(payload: CandidateRankRequest, current_user: dict = Depends(get_current_user)):
    ranked = rank_candidates(payload.candidates, payload.target_role)
    return {"target_role": payload.target_role, "ranked_candidates": ranked}


@router.post("/api/jd/compare")
def compare_jd(payload: JDCompareRequest, current_user: dict = Depends(get_current_optional_user)):
    result = compare_resume_to_jd(payload.resume_skills, payload.job_description)
    return result


@router.post("/api/projects/recommend")
def project_recommendations(payload: ProjectRecommendationRequest, current_user: dict = Depends(get_current_optional_user)):
    projects = recommend_projects(payload.target_role, payload.missing_skills)
    return {"target_role": payload.target_role, "projects": projects}


@router.post("/api/cover-letter/generate")
def cover_letter_generate(payload: CoverLetterRequest, current_user: dict = Depends(get_current_optional_user)):
    user_info = _fetch_authenticated_user_info(current_user)

    result = generate_cover_letter(
        resume_data=payload.resume_data,
        target_role=payload.target_role,
        company_name=payload.company_name,
        job_description=payload.job_description,
        hiring_manager=payload.hiring_manager,
        user_info=user_info,
    )
    return result


def _fetch_authenticated_user_info(current_user: Optional[dict]) -> dict:
    """Fetch the authenticated user's real info from DB.

    Always prioritizes the logged-in user's data over resume data.
    Resume is only used for skills/experience, never for personal info.
    """
    info = {
        "name": "",
        "email": "",
        "phone": "",
        "location": "",
        "bio": "",
        "current_role": "",
        "experience_years": "",
        "linkedin_url": "",
        "github_url": "",
    }
    if not current_user:
        return info

    user_id = current_user.get("id")

    info["name"] = current_user.get("full_name", "")
    info["email"] = current_user.get("email", "")

    if user_id:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT full_name, phone, location, bio,
                       current_job_role, experience_years,
                       linkedin_url, github_url
                FROM user_profiles WHERE user_id = %s
                """,
                (user_id,),
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                profile = dict(row)
                if profile.get("full_name"):
                    info["name"] = profile["full_name"]
                if profile.get("phone"):
                    info["phone"] = profile["phone"]
                if profile.get("location"):
                    info["location"] = profile["location"]
                if profile.get("bio"):
                    info["bio"] = profile["bio"]
                if profile.get("current_job_role"):
                    info["current_role"] = profile["current_job_role"]
                if profile.get("experience_years"):
                    info["experience_years"] = profile["experience_years"]
                if profile.get("linkedin_url"):
                    info["linkedin_url"] = profile["linkedin_url"]
                if profile.get("github_url"):
                    info["github_url"] = profile["github_url"]
        except Exception as e:
            logger.warning(f"Failed to fetch user profile: {e}")

    return info



