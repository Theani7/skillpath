from sqlalchemy import (
    Column, Integer, String, Text, Real, ForeignKey, UniqueConstraint,
    CheckConstraint
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class UserData(Base):
    __tablename__ = "user_data"
    ID = Column(Integer, primary_key=True, autoincrement=True)
    sec_token = Column("sec_token", String(20), nullable=False)
    ip_add = Column("ip_add", String(50))
    host_name = Column("host_name", String(50))
    dev_user = Column("dev_user", String(50))
    os_name_ver = Column("os_name_ver", String(50))
    latlong = Column("latlong", String(50))
    city = Column("city", String(50))
    state = Column("state", String(50))
    country = Column("country", String(50))
    act_name = Column("act_name", String(255), nullable=False, server_default='')
    act_mail = Column("act_mail", String(255), nullable=False, server_default='')
    act_mob = Column("act_mob", String(50), nullable=False, server_default='')
    Name = Column("Name", String(500), nullable=False)
    Email_ID = Column("Email_ID", String(500), nullable=False)
    resume_score = Column("resume_score", String(8), nullable=False)
    Timestamp = Column("Timestamp", String(50), nullable=False)
    Page_no = Column("Page_no", String(5), nullable=False)
    Predicted_Field = Column("Predicted_Field", Text, nullable=False, server_default='')
    User_level = Column("User_level", Text, nullable=False, server_default='')
    Actual_skills = Column("Actual_skills", Text, nullable=False, server_default='')
    Recommended_skills = Column("Recommended_skills", Text, nullable=False, server_default='')
    Recommended_courses = Column("Recommended_courses", Text, nullable=False, server_default='')
    pdf_name = Column("pdf_name", String(255), nullable=False)
    target_role = Column("target_role", String(200), server_default='Unknown')
    missing_skills = Column("missing_skills", Text, server_default='')
    user_id = Column("user_id", Integer, server_default='-1')
    analysis_data = Column("analysis_data", Text, server_default=None)
    content_hash = Column("content_hash", String(64), server_default=None)


class UserFeedback(Base):
    __tablename__ = "user_feedback"
    ID = Column(Integer, primary_key=True, autoincrement=True)
    feed_name = Column("feed_name", String(50), nullable=False)
    feed_email = Column("feed_email", String(120), nullable=False)
    feed_score = Column("feed_score", Integer, nullable=False)
    comments = Column("comments", String(2000))
    Timestamp = Column("Timestamp", String(50), nullable=False)
    __table_args__ = (
        CheckConstraint("feed_score BETWEEN 1 AND 5", name="ck_feed_score"),
    )


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    field = Column("field", String(100), nullable=False)
    course_name = Column("course_name", String(300), nullable=False)
    course_url = Column("course_url", String(500), nullable=False)
    description = Column("description", Text, server_default='')
    instructor = Column("instructor", String(200), server_default='')
    rating = Column("rating", Real, server_default='0')
    duration = Column("duration", String(50), server_default='')
    price = Column("price", String(50), server_default='')
    platform = Column("platform", String(50), server_default='')
    enrollment_count = Column("enrollment_count", Integer, server_default='0')
    last_scraped = Column("last_scraped", Text, server_default=None)
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column("username", String(50), unique=True, nullable=False)
    email = Column("email", String(120), unique=True, nullable=False)
    full_name = Column("full_name", String(100), server_default='User')
    hashed_password = Column("hashed_password", String(255), nullable=False)
    role = Column("role", Text, nullable=False)
    is_active = Column("is_active", Integer, server_default='1')
    email_verified = Column("email_verified", Integer, server_default='1')
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")
    __table_args__ = (
        CheckConstraint("role IN ('admin', 'user')", name="ck_user_role"),
    )


class OtpCode(Base):
    __tablename__ = "otp_codes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column("email", String(120), nullable=False)
    purpose = Column("purpose", String(30), nullable=False)
    code_hash = Column("code_hash", String(64), nullable=False)
    expires_at = Column("expires_at", Integer, nullable=False)
    attempts = Column("attempts", Integer, server_default='0')
    used = Column("used", Integer, server_default='0')
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")


class MarketTrendsCache(Base):
    __tablename__ = "market_trends_cache"
    field = Column("field", String(200), primary_key=True)
    source = Column("source", String(40), nullable=False)
    payload = Column("payload", Text, nullable=False)
    fetched_at = Column("fetched_at", Integer, nullable=False)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    token = Column("token", String(64), primary_key=True)
    user_id = Column("user_id", Integer, nullable=False)
    expires_at = Column("expires_at", Integer, nullable=False)
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    token = Column("token", String(128), primary_key=True)
    user_id = Column("user_id", Integer, nullable=False)
    expires_at = Column("expires_at", Integer, nullable=False)
    used = Column("used", Integer, server_default='0')
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")


class UserProfile(Base):
    __tablename__ = "user_profiles"
    user_id = Column("user_id", Integer, primary_key=True)
    full_name = Column("full_name", String(200), server_default='')
    phone = Column("phone", String(50), server_default='')
    location = Column("location", String(200), server_default='')
    bio = Column("bio", Text, server_default='')
    current_role = Column("current_role", String(100), server_default='')
    experience_years = Column("experience_years", String(10), server_default='')
    linkedin_url = Column("linkedin_url", String(500), server_default='')
    github_url = Column("github_url", String(500), server_default='')
    updated_at = Column("updated_at", Text, server_default="CURRENT_TIMESTAMP")


class UserPreference(Base):
    __tablename__ = "user_preferences"
    user_id = Column("user_id", Integer, primary_key=True)
    target_role = Column("target_role", String(200), server_default='')
    timeline_months = Column("timeline_months", Integer, server_default='6')
    preferred_location = Column("preferred_location", String(200), server_default='')
    salary_target = Column("salary_target", Integer, server_default='0')
    locale = Column("locale", String(20), server_default='en')
    updated_at = Column("updated_at", Text, server_default="CURRENT_TIMESTAMP")


class SharedReport(Base):
    __tablename__ = "shared_reports"
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column("token", String(80), unique=True, nullable=False)
    user_id = Column("user_id", Integer, nullable=False)
    analysis_id = Column("analysis_id", Integer, nullable=False)
    expires_at = Column("expires_at", Integer, nullable=False)
    is_public = Column("is_public", Integer, server_default='0')
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column("user_id", Integer, nullable=False)
    channel = Column("channel", String(30), nullable=False, server_default='email')
    message = Column("message", Text, nullable=False)
    status = Column("status", String(30), nullable=False, server_default='pending')
    send_at = Column("send_at", Integer, server_default='0')
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")


class Subscription(Base):
    __tablename__ = "subscriptions"
    user_id = Column("user_id", Integer, primary_key=True)
    plan = Column("plan", String(40), nullable=False, server_default='free')
    status = Column("status", String(30), nullable=False, server_default='active')
    renews_at = Column("renews_at", Integer, server_default='0')
    updated_at = Column("updated_at", Text, server_default="CURRENT_TIMESTAMP")


class RequestLog(Base):
    __tablename__ = "request_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column("request_id", String(80), nullable=False)
    method = Column("method", String(10), nullable=False)
    path = Column("path", String(300), nullable=False)
    status_code = Column("status_code", Integer, nullable=False)
    elapsed_ms = Column("elapsed_ms", Real, nullable=False)
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")


class AnalysisCache(Base):
    __tablename__ = "analysis_cache"
    content_hash = Column("content_hash", String(64), primary_key=True, nullable=False)
    target_role = Column("target_role", String(200), primary_key=True, nullable=False, server_default='')
    result_json = Column("result_json", Text, nullable=False)
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")
    expires_at = Column("expires_at", Integer)


class RateLimit(Base):
    __tablename__ = "rate_limits"
    key = Column("key", String(100), primary_key=True)
    count = Column("count", Integer, server_default='0')
    updated_at = Column("updated_at", Integer, nullable=False)


class JobRole(Base):
    __tablename__ = "job_roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column("title", String(200), nullable=False)
    description = Column("description", Text, server_default='')
    category = Column("category", String(100), server_default='')
    is_active = Column("is_active", Integer, server_default='1')
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")


class JobRoleSkill(Base):
    __tablename__ = "job_role_skills"
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_role_id = Column("job_role_id", Integer, ForeignKey("job_roles.id", ondelete="CASCADE"), nullable=False)
    skill_name = Column("skill_name", String(100), nullable=False)
    is_required = Column("is_required", Integer, server_default='1')


class CareerRoadmap(Base):
    __tablename__ = "career_roadmaps"
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_role_id = Column("job_role_id", Integer, ForeignKey("job_roles.id", ondelete="CASCADE"), nullable=False)
    title = Column("title", String(200), nullable=False)
    description = Column("description", Text, server_default='')
    duration_weeks = Column("duration_weeks", Integer, server_default='12')
    sort_order = Column("sort_order", Integer, server_default='0')
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")


class RoadmapStep(Base):
    __tablename__ = "roadmap_steps"
    id = Column(Integer, primary_key=True, autoincrement=True)
    roadmap_id = Column("roadmap_id", Integer, ForeignKey("career_roadmaps.id", ondelete="CASCADE"), nullable=False)
    step_number = Column("step_number", Integer, nullable=False)
    title = Column("title", String(200), nullable=False)
    description = Column("description", Text, server_default='')
    duration_weeks = Column("duration_weeks", Integer, server_default='2')
    skills = Column("skills", Text, server_default='')
    resources = Column("resources", Text, server_default='')


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_user_id = Column("admin_user_id", Integer, nullable=False)
    admin_username = Column("admin_username", String(50), nullable=False)
    action = Column("action", String(100), nullable=False)
    target_type = Column("target_type", String(50), nullable=False)
    target_id = Column("target_id", String(100))
    details = Column("details", Text, server_default='')
    ip_address = Column("ip_address", String(50), server_default='')
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")


class UserRoadmapProgress(Base):
    __tablename__ = "user_roadmap_progress"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    analysis_id = Column("analysis_id", Integer)
    phase_index = Column("phase_index", Integer, nullable=False)
    task_index = Column("task_index", Integer, nullable=False)
    completed = Column("completed", Integer, server_default='0')
    completed_at = Column("completed_at", Text)
    __table_args__ = (
        UniqueConstraint("user_id", "analysis_id", "phase_index", "task_index",
                         name="uq_user_roadmap_progress"),
    )


class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    username = Column("username", String(100), primary_key=True)
    attempts = Column("attempts", Integer, server_default='0')
    first_attempt = Column("first_attempt", Integer, nullable=False)
    locked_until = Column("locked_until", Integer, server_default='0')


class SkillCategory(Base):
    __tablename__ = "skill_categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column("name", String(100), unique=True, nullable=False)
    sort_order = Column("sort_order", Integer, server_default='0')
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")


class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column("category_id", Integer, ForeignKey("skill_categories.id", ondelete="CASCADE"), nullable=False)
    name = Column("name", String(100), nullable=False)
    sort_order = Column("sort_order", Integer, server_default='0')
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")
    __table_args__ = (
        UniqueConstraint("category_id", "name", name="uq_skills_category_name"),
    )


class RoleSynonym(Base):
    __tablename__ = "role_synonyms"
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_key = Column("role_key", String(100), unique=True, nullable=False)
    categories = Column("categories", Text, nullable=False)
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")


class SkillAlias(Base):
    __tablename__ = "skill_aliases"
    id = Column(Integer, primary_key=True, autoincrement=True)
    alias = Column("alias", String(100), unique=True, nullable=False)
    canonical_skill = Column("canonical_skill", String(100), nullable=False)
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")


class FieldKeyword(Base):
    __tablename__ = "field_keywords"
    id = Column(Integer, primary_key=True, autoincrement=True)
    field_name = Column("field_name", String(100), nullable=False)
    keyword = Column("keyword", String(100), nullable=False)
    weight = Column("weight", Integer, server_default='1')
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")
    __table_args__ = (
        UniqueConstraint("field_name", "keyword", name="uq_field_keywords"),
    )


class IndustryTrend(Base):
    __tablename__ = "industry_trends"
    id = Column(Integer, primary_key=True, autoincrement=True)
    field_name = Column("field_name", String(100), nullable=False)
    trend_type = Column("trend_type", String(50), nullable=False)
    data = Column("data", Text, nullable=False)
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")
    __table_args__ = (
        UniqueConstraint("field_name", "trend_type", name="uq_industry_trends"),
    )


class MarketRoleAlias(Base):
    __tablename__ = "market_role_aliases"
    id = Column(Integer, primary_key=True, autoincrement=True)
    alias = Column("alias", String(100), unique=True, nullable=False)
    target_field = Column("target_field", String(100), nullable=False)
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")


class SkillRecommendation(Base):
    __tablename__ = "skill_recommendations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    field_name = Column("field_name", String(100), nullable=False)
    skill_name = Column("skill_name", String(100), nullable=False)
    sort_order = Column("sort_order", Integer, server_default='0')
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")
    __table_args__ = (
        UniqueConstraint("field_name", "skill_name", name="uq_skill_recommendations"),
    )


class RoadmapTemplate(Base):
    __tablename__ = "roadmap_templates"
    id = Column(Integer, primary_key=True, autoincrement=True)
    field_name = Column("field_name", String(100), nullable=False)
    step_number = Column("step_number", Integer, nullable=False)
    title = Column("title", String(200), nullable=False)
    duration = Column("duration", String(50), nullable=False)
    skills = Column("skills", Text, nullable=False)
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")
    __table_args__ = (
        UniqueConstraint("field_name", "step_number", name="uq_roadmap_templates"),
    )


class LearningAction(Base):
    __tablename__ = "learning_actions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    skill_name = Column("skill_name", String(100), nullable=False)
    difficulty = Column("difficulty", Integer, nullable=False)
    action_text = Column("action_text", Text, nullable=False)
    sort_order = Column("sort_order", Integer, server_default='0')
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")
    __table_args__ = (
        UniqueConstraint("skill_name", "action_text", name="uq_learning_actions"),
    )


class LearningResource(Base):
    __tablename__ = "learning_resources"
    id = Column(Integer, primary_key=True, autoincrement=True)
    skill_name = Column("skill_name", String(100), nullable=False)
    title = Column("title", String(300), nullable=False)
    url = Column("url", Text, nullable=False)
    resource_type = Column("resource_type", String(50), nullable=False)
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")
    __table_args__ = (
        UniqueConstraint("skill_name", "title", name="uq_learning_resources"),
    )


class SkillDifficulty(Base):
    __tablename__ = "skill_difficulty"
    id = Column(Integer, primary_key=True, autoincrement=True)
    skill_name = Column("skill_name", String(100), unique=True, nullable=False)
    difficulty_level = Column("difficulty_level", Integer, nullable=False)
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")


class SkillCluster(Base):
    __tablename__ = "skill_clusters"
    id = Column(Integer, primary_key=True, autoincrement=True)
    cluster_name = Column("cluster_name", String(100), nullable=False)
    skill_name = Column("skill_name", String(100), nullable=False)
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")
    __table_args__ = (
        UniqueConstraint("cluster_name", "skill_name", name="uq_skill_clusters"),
    )


class VideoResource(Base):
    __tablename__ = "video_resources"
    id = Column(Integer, primary_key=True, autoincrement=True)
    field_name = Column("field_name", String(100), nullable=False)
    video_type = Column("video_type", String(50), nullable=False)
    url = Column("url", Text, nullable=False)
    sort_order = Column("sort_order", Integer, server_default='0')
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")
    __table_args__ = (
        UniqueConstraint("field_name", "video_type", "url", name="uq_video_resources"),
    )


class RoleConfig(Base):
    __tablename__ = "role_configs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_key = Column("role_key", String(100), unique=True, nullable=False)
    project_types = Column("project_types", Text, nullable=False)
    interview_focus = Column("interview_focus", Text, nullable=False)
    portfolio_emphasis = Column("portfolio_emphasis", Text, nullable=False)
    key_tools = Column("key_tools", Text, nullable=False)
    created_at = Column("created_at", Text, server_default="CURRENT_TIMESTAMP")
