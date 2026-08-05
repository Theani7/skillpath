"""Initial schema — all 38 tables and indexes.

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-08-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_data",
        sa.Column("ID", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("sec_token", sa.String(20), nullable=False),
        sa.Column("ip_add", sa.String(50), nullable=True),
        sa.Column("host_name", sa.String(50), nullable=True),
        sa.Column("dev_user", sa.String(50), nullable=True),
        sa.Column("os_name_ver", sa.String(50), nullable=True),
        sa.Column("latlong", sa.String(50), nullable=True),
        sa.Column("city", sa.String(50), nullable=True),
        sa.Column("state", sa.String(50), nullable=True),
        sa.Column("country", sa.String(50), nullable=True),
        sa.Column("act_name", sa.String(255), nullable=False, server_default=""),
        sa.Column("act_mail", sa.String(255), nullable=False, server_default=""),
        sa.Column("act_mob", sa.String(50), nullable=False, server_default=""),
        sa.Column("Name", sa.String(500), nullable=False),
        sa.Column("Email_ID", sa.String(500), nullable=False),
        sa.Column("resume_score", sa.String(8), nullable=False),
        sa.Column("Timestamp", sa.String(50), nullable=False),
        sa.Column("Page_no", sa.String(5), nullable=False),
        sa.Column("Predicted_Field", sa.Text(), nullable=False, server_default=""),
        sa.Column("User_level", sa.Text(), nullable=False, server_default=""),
        sa.Column("Actual_skills", sa.Text(), nullable=False, server_default=""),
        sa.Column("Recommended_skills", sa.Text(), nullable=False, server_default=""),
        sa.Column("Recommended_courses", sa.Text(), nullable=False, server_default=""),
        sa.Column("pdf_name", sa.String(255), nullable=False),
        sa.Column("target_role", sa.String(200), server_default="Unknown"),
        sa.Column("missing_skills", sa.Text(), server_default=""),
        sa.Column("user_id", sa.Integer(), server_default="-1"),
        sa.Column("analysis_data", sa.Text(), nullable=True, server_default=None),
        sa.Column("content_hash", sa.String(64), nullable=True, server_default=None),
    )

    op.create_table(
        "user_feedback",
        sa.Column("ID", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("feed_name", sa.String(50), nullable=False),
        sa.Column("feed_email", sa.String(120), nullable=False),
        sa.Column("feed_score", sa.Integer(), nullable=False),
        sa.Column("comments", sa.String(2000), nullable=True),
        sa.Column("Timestamp", sa.String(50), nullable=False),
        sa.CheckConstraint("feed_score BETWEEN 1 AND 5", name="ck_feed_score"),
    )

    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("field", sa.String(100), nullable=False),
        sa.Column("course_name", sa.String(300), nullable=False),
        sa.Column("course_url", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("instructor", sa.String(200), server_default=""),
        sa.Column("rating", sa.Float(), server_default="0"),
        sa.Column("duration", sa.String(50), server_default=""),
        sa.Column("price", sa.String(50), server_default=""),
        sa.Column("platform", sa.String(50), server_default=""),
        sa.Column("enrollment_count", sa.Integer(), server_default="0"),
        sa.Column("last_scraped", sa.TIMESTAMP(), nullable=True, server_default=None),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(50), unique=True, nullable=False),
        sa.Column("email", sa.String(120), unique=True, nullable=False),
        sa.Column("full_name", sa.String(100), server_default="User"),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Integer(), server_default="1"),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("email_verified", sa.Integer(), server_default="1"),
        sa.CheckConstraint("role IN ('admin', 'user')", name="ck_user_role"),
    )

    op.create_table(
        "otp_codes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(120), nullable=False),
        sa.Column("purpose", sa.String(30), nullable=False),
        sa.Column("code_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.Integer(), nullable=False),
        sa.Column("attempts", sa.Integer(), server_default="0"),
        sa.Column("used", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("idx_otp_codes_email", "otp_codes", ["email", "purpose"])

    op.create_table(
        "market_trends_cache",
        sa.Column("field", sa.String(200), primary_key=True),
        sa.Column("source", sa.String(40), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("fetched_at", sa.Integer(), nullable=False),
    )

    op.create_table(
        "refresh_tokens",
        sa.Column("token", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "password_reset_tokens",
        sa.Column("token", sa.String(128), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.Integer(), nullable=False),
        sa.Column("used", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "user_profiles",
        sa.Column("user_id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(200), server_default=""),
        sa.Column("phone", sa.String(50), server_default=""),
        sa.Column("location", sa.String(200), server_default=""),
        sa.Column("bio", sa.Text(), server_default=""),
        sa.Column("current_role", sa.String(100), server_default=""),
        sa.Column("experience_years", sa.String(10), server_default=""),
        sa.Column("linkedin_url", sa.String(500), server_default=""),
        sa.Column("github_url", sa.String(500), server_default=""),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "user_preferences",
        sa.Column("user_id", sa.Integer(), primary_key=True),
        sa.Column("target_role", sa.String(200), server_default=""),
        sa.Column("timeline_months", sa.Integer(), server_default="6"),
        sa.Column("preferred_location", sa.String(200), server_default=""),
        sa.Column("salary_target", sa.Integer(), server_default="0"),
        sa.Column("locale", sa.String(20), server_default="en"),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "shared_reports",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("token", sa.String(80), unique=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("analysis_id", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.Integer(), nullable=False),
        sa.Column("is_public", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("channel", sa.String(30), nullable=False, server_default="email"),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("send_at", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "subscriptions",
        sa.Column("user_id", sa.Integer(), primary_key=True),
        sa.Column("plan", sa.String(40), nullable=False, server_default="free"),
        sa.Column("status", sa.String(30), nullable=False, server_default="active"),
        sa.Column("renews_at", sa.Integer(), server_default="0"),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "request_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("request_id", sa.String(80), nullable=False),
        sa.Column("method", sa.String(10), nullable=False),
        sa.Column("path", sa.String(300), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("elapsed_ms", sa.Float(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "analysis_cache",
        sa.Column("content_hash", sa.String(64), primary_key=True, nullable=False),
        sa.Column("target_role", sa.String(200), primary_key=True, nullable=False, server_default=""),
        sa.Column("result_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("expires_at", sa.Integer(), nullable=True),
    )

    op.create_table(
        "rate_limits",
        sa.Column("key", sa.String(100), primary_key=True),
        sa.Column("count", sa.Integer(), server_default="0"),
        sa.Column("updated_at", sa.Integer(), nullable=False),
    )
    op.create_index("idx_rate_limits_updated", "rate_limits", ["updated_at"])

    op.create_table(
        "job_roles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("category", sa.String(100), server_default=""),
        sa.Column("is_active", sa.Integer(), server_default="1"),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "job_role_skills",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("job_role_id", sa.Integer(), nullable=False),
        sa.Column("skill_name", sa.String(100), nullable=False),
        sa.Column("is_required", sa.Integer(), server_default="1"),
        sa.ForeignKeyConstraint(["job_role_id"], ["job_roles.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "career_roadmaps",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("job_role_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("duration_weeks", sa.Integer(), server_default="12"),
        sa.Column("sort_order", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["job_role_id"], ["job_roles.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "roadmap_steps",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("roadmap_id", sa.Integer(), nullable=False),
        sa.Column("step_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("duration_weeks", sa.Integer(), server_default="2"),
        sa.Column("skills", sa.Text(), server_default=""),
        sa.Column("resources", sa.Text(), server_default=""),
        sa.ForeignKeyConstraint(["roadmap_id"], ["career_roadmaps.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("admin_user_id", sa.Integer(), nullable=False),
        sa.Column("admin_username", sa.String(50), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("target_type", sa.String(50), nullable=False),
        sa.Column("target_id", sa.String(100), nullable=True),
        sa.Column("details", sa.Text(), server_default=""),
        sa.Column("ip_address", sa.String(50), server_default=""),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "user_roadmap_progress",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("analysis_id", sa.Integer(), nullable=True),
        sa.Column("phase_index", sa.Integer(), nullable=False),
        sa.Column("task_index", sa.Integer(), nullable=False),
        sa.Column("completed", sa.Integer(), server_default="0"),
        sa.Column("completed_at", sa.TIMESTAMP(), nullable=True),
        sa.UniqueConstraint("user_id", "analysis_id", "phase_index", "task_index"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "login_attempts",
        sa.Column("username", sa.String(100), primary_key=True),
        sa.Column("attempts", sa.Integer(), server_default="0"),
        sa.Column("first_attempt", sa.Integer(), nullable=False),
        sa.Column("locked_until", sa.Integer(), server_default="0"),
    )

    op.create_table(
        "skill_categories",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["category_id"], ["skill_categories.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("category_id", "name"),
    )

    op.create_table(
        "role_synonyms",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("role_key", sa.String(100), unique=True, nullable=False),
        sa.Column("categories", sa.Text(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "skill_aliases",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("alias", sa.String(100), unique=True, nullable=False),
        sa.Column("canonical_skill", sa.String(100), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "field_keywords",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("field_name", sa.String(100), nullable=False),
        sa.Column("keyword", sa.String(100), nullable=False),
        sa.Column("weight", sa.Integer(), server_default="1"),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("field_name", "keyword"),
    )

    op.create_table(
        "industry_trends",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("field_name", sa.String(100), nullable=False),
        sa.Column("trend_type", sa.String(50), nullable=False),
        sa.Column("data", sa.Text(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("field_name", "trend_type"),
    )

    op.create_table(
        "market_role_aliases",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("alias", sa.String(100), unique=True, nullable=False),
        sa.Column("target_field", sa.String(100), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "skill_recommendations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("field_name", sa.String(100), nullable=False),
        sa.Column("skill_name", sa.String(100), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("field_name", "skill_name"),
    )

    op.create_table(
        "roadmap_templates",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("field_name", sa.String(100), nullable=False),
        sa.Column("step_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("duration", sa.String(50), nullable=False),
        sa.Column("skills", sa.Text(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("field_name", "step_number"),
    )

    op.create_table(
        "learning_actions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("skill_name", sa.String(100), nullable=False),
        sa.Column("difficulty", sa.Integer(), nullable=False),
        sa.Column("action_text", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("skill_name", "action_text"),
    )

    op.create_table(
        "learning_resources",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("skill_name", sa.String(100), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("skill_name", "title"),
    )

    op.create_table(
        "skill_difficulty",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("skill_name", sa.String(100), unique=True, nullable=False),
        sa.Column("difficulty_level", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "skill_clusters",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("cluster_name", sa.String(100), nullable=False),
        sa.Column("skill_name", sa.String(100), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("cluster_name", "skill_name"),
    )

    op.create_table(
        "video_resources",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("field_name", sa.String(100), nullable=False),
        sa.Column("video_type", sa.String(50), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("field_name", "video_type", "url"),
    )

    op.create_table(
        "role_configs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("role_key", sa.String(100), unique=True, nullable=False),
        sa.Column("project_types", sa.Text(), nullable=False),
        sa.Column("interview_focus", sa.Text(), nullable=False),
        sa.Column("portfolio_emphasis", sa.Text(), nullable=False),
        sa.Column("key_tools", sa.Text(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_index("idx_user_data_user_id", "user_data", ["user_id"])
    op.create_index("idx_user_data_timestamp", "user_data", ["Timestamp"])
    op.create_index("idx_user_data_predicted_field", "user_data", ["Predicted_Field"])
    op.create_index("idx_users_username", "users", ["username"])
    op.create_index("idx_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index("idx_shared_reports_token", "shared_reports", ["token"])
    op.execute("CREATE UNIQUE INDEX idx_single_admin ON users(role) WHERE role = 'admin'")


def downgrade() -> None:
    op.drop_index("idx_shared_reports_token", table_name="shared_reports")
    op.drop_index("idx_refresh_tokens_user_id", table_name="refresh_tokens")
    op.drop_index("idx_users_username", table_name="users")
    op.drop_index("idx_user_data_predicted_field", table_name="user_data")
    op.drop_index("idx_user_data_timestamp", table_name="user_data")
    op.drop_index("idx_user_data_user_id", table_name="user_data")

    op.execute("DROP INDEX IF EXISTS idx_single_admin")

    op.drop_table("role_configs")
    op.drop_table("video_resources")
    op.drop_table("skill_clusters")
    op.drop_table("skill_difficulty")
    op.drop_table("learning_resources")
    op.drop_table("learning_actions")
    op.drop_table("roadmap_templates")
    op.drop_table("skill_recommendations")
    op.drop_table("market_role_aliases")
    op.drop_table("industry_trends")
    op.drop_table("field_keywords")
    op.drop_table("skill_aliases")
    op.drop_table("role_synonyms")
    op.drop_table("skills")
    op.drop_table("skill_categories")
    op.drop_table("login_attempts")
    op.drop_table("user_roadmap_progress")
    op.drop_table("audit_logs")
    op.drop_table("roadmap_steps")
    op.drop_table("career_roadmaps")
    op.drop_table("job_role_skills")
    op.drop_table("job_roles")
    op.drop_index("idx_rate_limits_updated", table_name="rate_limits")
    op.drop_table("rate_limits")
    op.drop_table("analysis_cache")
    op.drop_table("request_logs")
    op.drop_table("subscriptions")
    op.drop_table("notifications")
    op.drop_table("shared_reports")
    op.drop_table("user_preferences")
    op.drop_table("user_profiles")
    op.drop_table("password_reset_tokens")
    op.drop_table("refresh_tokens")
    op.drop_table("market_trends_cache")
    op.drop_index("idx_otp_codes_email", table_name="otp_codes")
    op.drop_table("otp_codes")
    op.drop_table("users")
    op.drop_table("courses")
    op.drop_table("user_feedback")
    op.drop_table("user_data")
