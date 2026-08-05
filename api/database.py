import os
import time
import json
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, event

from api.db_compat import (
    get_db_type,
    get_engine_url,
    get_connect_args,
    get_row_factory,
    get_table_columns,
    CompatConnection,
    ph,
)
from api.seed_defaults import (
    CORE_SKILLS_BY_ROLE,
    DEFAULT_ROLES,
    DEFAULT_ROLE_SKILLS,
    DEFAULT_ROADMAPS,
)

logger = logging.getLogger("resume-analyzer")

IS_POSTGRES = get_db_type() == "postgresql"

ALLOWED_TABLES = frozenset({
    "user_data", "user_feedback", "users", "courses",
    "refresh_tokens", "analysis_cache", "login_attempts",
    "password_reset_tokens", "user_profiles", "user_preferences",
    "shared_reports", "notifications", "subscriptions",
    "request_logs", "rate_limits", "skill_categories", "skills",
    "role_synonyms", "skill_aliases", "job_roles", "career_roadmaps",
    "roadmap_steps", "field_keywords", "industry_trends",
    "market_role_aliases", "skill_recommendations", "learning_actions",
    "learning_resources", "skill_difficulty", "skill_clusters",
    "video_resources", "role_configs", "market_trends_cache",
    "job_role_skills", "audit_logs", "user_roadmap_progress",
    "roadmap_templates", "otp_codes",
})

engine = create_engine(
    get_engine_url(),
    connect_args=get_connect_args(),
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if get_db_type() == "sqlite":
        import sqlite3
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()
        dbapi_connection.row_factory = sqlite3.Row


def get_db_connection():
    raw = engine.raw_connection()
    if get_db_type() == "postgresql":
        import psycopg2.extras
        raw.cursor_factory = psycopg2.extras.RealDictCursor
    return CompatConnection(raw)


@contextmanager
def get_db():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


def _ensure_column(cursor, table: str, col: str, typedef: str, default=None) -> None:
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Table '{table}' is not in the allowed tables whitelist")
    existing = get_table_columns(cursor, table)
    if col not in existing:
        if default is not None:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typedef} DEFAULT {default}")
        else:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typedef}")


def run_migrations():
    """Run Alembic migrations programmatically."""
    from alembic.config import Config
    from alembic import command

    alembic_cfg = Config(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "alembic.ini"))
    command.upgrade(alembic_cfg, "head")


def init_db():
    conn = None
    try:
        run_migrations()

        conn = get_db_connection()
        cursor = conn.cursor()

        admin_user = os.getenv("ADMIN_USERNAME", "")
        admin_pass = os.getenv("ADMIN_PASSWORD", "")
        if admin_user and admin_pass:
            from api.security import get_password_hash
            hashed = get_password_hash(admin_pass)

            cursor.execute("SELECT id, role FROM users WHERE username = ?", (admin_user,))
            existing = cursor.fetchone()

            cursor.execute("SELECT id, username FROM users WHERE role = 'admin' LIMIT 1")
            any_admin = cursor.fetchone()

            if existing:
                cursor.execute('''
                    UPDATE users SET email = ?, full_name = ?, hashed_password = ?, role = ?
                    WHERE username = ?
                ''', (f"{admin_user}@skillpath.ai", "System Admin", hashed, "admin", admin_user))
            elif not any_admin:
                cursor.execute('''
                    INSERT INTO users (username, email, full_name, hashed_password, role)
                    VALUES (?, ?, ?, ?, ?)
                ''', (admin_user, f"{admin_user}@skillpath.ai", "System Admin", hashed, "admin"))
            else:
                logger.warning(
                    f"Admin account already exists as '{any_admin['username']}'. "
                    f"Configured admin '{admin_user}' was not created to avoid duplicates."
                )

        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_single_admin ON users(role) WHERE role = 'admin'")

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_data_user_id ON user_data(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_data_timestamp ON user_data(Timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_data_predicted_field ON user_data(Predicted_Field)")

        # Add content_hash column to user_data if missing (for cache cleanup on delete)
        ud_cols = get_table_columns(cursor, "user_data")
        if 'content_hash' not in ud_cols:
            cursor.execute("ALTER TABLE user_data ADD COLUMN content_hash VARCHAR(64) DEFAULT NULL")

        # Fix is_required flags: mark core skills as required, others as nice-to-have
        cursor.execute("SELECT jr.id, jr.title, js.skill_name FROM job_role_skills js JOIN job_roles jr ON js.job_role_id = jr.id")
        role_skill_rows = cursor.fetchall()
        for row in role_skill_rows:
            role_id = row["id"] if isinstance(row, dict) else row[0]
            role_title = row["title"] if isinstance(row, dict) else row[1]
            skill_name = row["skill_name"] if isinstance(row, dict) else row[2]
            core = CORE_SKILLS_BY_ROLE.get(role_title, set())
            desired = 1 if skill_name in core else 0
            cursor.execute(
                f"UPDATE job_role_skills SET is_required = {ph()} WHERE job_role_id = {ph()} AND skill_name = {ph()}",
                (desired, role_id, skill_name)
            )

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shared_reports_token ON shared_reports(token)")

        cursor.execute("DELETE FROM analysis_cache WHERE expires_at IS NOT NULL AND expires_at < ?",
                       (int(time.time()),))
        cursor.execute("DELETE FROM rate_limits WHERE updated_at < ?", (int(time.time() // 60) - 5,))

        # Seed default job roles if empty
        cursor.execute("SELECT COUNT(*) as cnt FROM job_roles")
        row = cursor.fetchone()
        count = row["cnt"] if isinstance(row, dict) else row[0]
        if count == 0:
            for title, desc, category in DEFAULT_ROLES:
                cursor.execute(
                    "INSERT INTO job_roles (title, description, category) VALUES (?, ?, ?)",
                    (title, desc, category)
                )
                role_id = cursor.lastrowid
                # Add default skills for each role
                skills_for_role = DEFAULT_ROLE_SKILLS.get(title, {})
                for skill in skills_for_role.get("required", []):
                    cursor.execute(
                        "INSERT INTO job_role_skills (job_role_id, skill_name, is_required) VALUES (?, ?, 1)",
                        (role_id, skill)
                    )
                for skill in skills_for_role.get("nice_to_have", []):
                    cursor.execute(
                        "INSERT INTO job_role_skills (job_role_id, skill_name, is_required) VALUES (?, ?, 0)",
                        (role_id, skill)
                    )
                # Add default roadmap for each role
                roadmap = DEFAULT_ROADMAPS.get(title)
                if roadmap:
                    cursor.execute(
                        "INSERT INTO career_roadmaps (job_role_id, title, description, duration_weeks, sort_order) VALUES (?, ?, ?, ?, 1)",
                        (role_id, roadmap['title'], roadmap['description'], roadmap['duration_weeks'])
                    )
                    roadmap_id = cursor.lastrowid
                    for step in roadmap['steps']:
                        cursor.execute(
                            "INSERT INTO roadmap_steps (roadmap_id, step_number, title, description, duration_weeks, skills, resources) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (roadmap_id, step['step'], step['title'], step['description'], step['duration_weeks'], step['skills'], step['resources'])
                        )

        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()




init_db()
