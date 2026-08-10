import os
import time
import json
import logging
from contextlib import contextmanager

import psycopg2
import psycopg2.extras
import psycopg2.pool
from psycopg2 import sql

from api.seed_defaults import (
    CORE_SKILLS_BY_ROLE,
    DEFAULT_ROLES,
    DEFAULT_ROLE_SKILLS,
    DEFAULT_ROADMAPS,
)

logger = logging.getLogger("resume-analyzer")

ALLOWED_TABLES = {
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
}

_pool = None


class _PooledConnection:
    """Wrapper around a psycopg2 connection that returns to the pool on close().

    This lets existing code use the familiar `conn.close()` pattern
    while still benefiting from connection pooling.
    """

    def __init__(self, conn, pool):
        self._conn = conn
        self._pool = pool

    def cursor(self):
        return self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._pool.putconn(self._conn)

    def __getattr__(self, name):
        return getattr(self._conn, name)


def _get_pool():
    global _pool
    if _pool is None:
        database_url = os.getenv("DATABASE_URL", "")
        if not database_url:
            raise RuntimeError(
                "DATABASE_URL is required. "
                "Example: postgresql://user:pass@localhost:5432/skillpath"
            )
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        # Sync endpoints and the middleware run in Starlette's threadpool, so
        # the pool must be at least as large as that threadpool or concurrent
        # requests exhaust it and raise PoolError. Keep DB_POOL_MAX >=
        # threadpool size (Starlette default 40).
        _pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=int(os.getenv("DB_POOL_MIN", "1")),
            maxconn=int(os.getenv("DB_POOL_MAX", "50")),
            dsn=database_url,
        )
    return _pool


POOL_ACQUIRE_TIMEOUT = float(os.getenv("DB_POOL_ACQUIRE_TIMEOUT", "5"))


def get_db_connection():
    """Check out a pooled connection, waiting briefly if the pool is saturated.

    psycopg2 pools raise immediately when exhausted. Under a burst that turns a
    transient spike into a 500, so wait for a connection to be returned before
    giving up.
    """
    pool = _get_pool()
    deadline = time.monotonic() + POOL_ACQUIRE_TIMEOUT
    delay = 0.005
    while True:
        try:
            raw = pool.getconn()
            break
        except psycopg2.pool.PoolError:
            if time.monotonic() >= deadline:
                logger.error("DB pool exhausted; raise DB_POOL_MAX or reduce concurrency")
                raise
            time.sleep(delay)
            delay = min(delay * 2, 0.1)
    raw.autocommit = False
    return _PooledConnection(raw, pool)


def _release_connection(conn):
    if isinstance(conn, _PooledConnection):
        conn.close()
    else:
        _get_pool().putconn(conn)


@contextmanager
def get_db():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        _release_connection(conn)


def _ensure_column(cursor, table: str, col: str, typedef: str, default=None) -> None:
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Table '{table}' is not in the allowed tables whitelist")
    cursor.execute(
        "SELECT column_name FROM information_schema.columns WHERE table_name = %s",
        (table,),
    )
    # Callers may pass a plain cursor or a RealDictCursor, so handle both
    # rather than assuming dict-style rows.
    existing = {
        (row["column_name"] if isinstance(row, dict) else row[0])
        for row in cursor.fetchall()
    }
    if col in existing:
        return
    stmt = sql.SQL("ALTER TABLE {} ADD COLUMN {} ").format(
        sql.Identifier(table), sql.Identifier(col)
    ) + sql.SQL(typedef)
    if default is not None:
        stmt = stmt + sql.SQL(" DEFAULT ") + sql.Literal(default)
    cursor.execute(stmt)


def init_db():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id BIGSERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                full_name VARCHAR(100) DEFAULT 'User',
                hashed_password VARCHAR(255) NOT NULL,
                role TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                email_verified INTEGER DEFAULT 1,
                google_id VARCHAR(100) DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT ck_user_role CHECK (role IN ('admin', 'user'))
            )
        """)

        cursor.execute("""
            ALTER TABLE users ADD COLUMN IF NOT EXISTS google_id VARCHAR(100) DEFAULT NULL
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                ID BIGSERIAL PRIMARY KEY,
                sec_token VARCHAR(20) NOT NULL,
                ip_add VARCHAR(50),
                host_name VARCHAR(50),
                dev_user VARCHAR(50),
                os_name_ver VARCHAR(50),
                latlong VARCHAR(50),
                city VARCHAR(50),
                state VARCHAR(50),
                country VARCHAR(50),
                act_name VARCHAR(255) NOT NULL DEFAULT '',
                act_mail VARCHAR(255) NOT NULL DEFAULT '',
                act_mob VARCHAR(50) NOT NULL DEFAULT '',
                "Name" VARCHAR(500) NOT NULL,
                "Email_ID" VARCHAR(500) NOT NULL,
                resume_score VARCHAR(8) NOT NULL,
                "Timestamp" VARCHAR(50) NOT NULL,
                "Page_no" VARCHAR(5) NOT NULL,
                "Predicted_Field" TEXT NOT NULL DEFAULT '',
                "User_level" TEXT NOT NULL DEFAULT '',
                "Actual_skills" TEXT NOT NULL DEFAULT '',
                "Recommended_skills" TEXT NOT NULL DEFAULT '',
                "Recommended_courses" TEXT NOT NULL DEFAULT '',
                pdf_name VARCHAR(255) NOT NULL,
                target_role VARCHAR(200) DEFAULT 'Unknown',
                missing_skills TEXT DEFAULT '',
                user_id INTEGER DEFAULT -1,
                analysis_data TEXT,
                content_hash VARCHAR(64)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                ID BIGSERIAL PRIMARY KEY,
                feed_name VARCHAR(50) NOT NULL,
                feed_email VARCHAR(120) NOT NULL,
                feed_score INTEGER NOT NULL,
                comments VARCHAR(2000),
                "Timestamp" VARCHAR(50) NOT NULL,
                CONSTRAINT ck_feed_score CHECK (feed_score BETWEEN 1 AND 5)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id BIGSERIAL PRIMARY KEY,
                field VARCHAR(100) NOT NULL,
                course_name VARCHAR(300) NOT NULL,
                course_url VARCHAR(500) NOT NULL,
                description TEXT DEFAULT '',
                instructor VARCHAR(200) DEFAULT '',
                rating REAL DEFAULT 0,
                duration VARCHAR(50) DEFAULT '',
                price VARCHAR(50) DEFAULT '',
                platform VARCHAR(50) DEFAULT '',
                enrollment_count INTEGER DEFAULT 0,
                last_scraped TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS otp_codes (
                id BIGSERIAL PRIMARY KEY,
                email VARCHAR(120) NOT NULL,
                purpose VARCHAR(30) NOT NULL,
                code_hash VARCHAR(64) NOT NULL,
                expires_at INTEGER NOT NULL,
                attempts INTEGER DEFAULT 0,
                used INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_trends_cache (
                field VARCHAR(200) PRIMARY KEY,
                source VARCHAR(40) NOT NULL,
                payload TEXT NOT NULL,
                fetched_at INTEGER NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                token VARCHAR(64) PRIMARY KEY,
                user_id INTEGER NOT NULL,
                expires_at INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS oauth_link_tokens (
                token VARCHAR(128) PRIMARY KEY,
                user_id INTEGER NOT NULL,
                google_id VARCHAR(100) NOT NULL,
                expires_at INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                token VARCHAR(128) PRIMARY KEY,
                user_id INTEGER NOT NULL,
                expires_at INTEGER NOT NULL,
                used INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                full_name VARCHAR(200) DEFAULT '',
                phone VARCHAR(50) DEFAULT '',
                location VARCHAR(200) DEFAULT '',
                bio TEXT DEFAULT '',
                current_job_role VARCHAR(100) DEFAULT '',
                experience_years VARCHAR(10) DEFAULT '',
                linkedin_url VARCHAR(500) DEFAULT '',
                github_url VARCHAR(500) DEFAULT '',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                target_role VARCHAR(200) DEFAULT '',
                timeline_months INTEGER DEFAULT 6,
                preferred_location VARCHAR(200) DEFAULT '',
                salary_target INTEGER DEFAULT 0,
                locale VARCHAR(20) DEFAULT 'en',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shared_reports (
                id BIGSERIAL PRIMARY KEY,
                token VARCHAR(80) UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                analysis_id INTEGER NOT NULL,
                expires_at INTEGER NOT NULL,
                is_public INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id BIGSERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                channel VARCHAR(30) NOT NULL DEFAULT 'email',
                message TEXT NOT NULL,
                status VARCHAR(30) NOT NULL DEFAULT 'pending',
                send_at INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                plan VARCHAR(40) NOT NULL DEFAULT 'free',
                status VARCHAR(30) NOT NULL DEFAULT 'active',
                renews_at INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS request_logs (
                id BIGSERIAL PRIMARY KEY,
                request_id VARCHAR(80) NOT NULL,
                method VARCHAR(10) NOT NULL,
                path VARCHAR(300) NOT NULL,
                status_code INTEGER NOT NULL,
                elapsed_ms REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_cache (
                content_hash VARCHAR(64) NOT NULL,
                target_role VARCHAR(200) NOT NULL DEFAULT '',
                result_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at INTEGER,
                PRIMARY KEY (content_hash, target_role)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rate_limits (
                key VARCHAR(100) PRIMARY KEY,
                count INTEGER DEFAULT 0,
                updated_at INTEGER NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_roles (
                id BIGSERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT DEFAULT '',
                category VARCHAR(100) DEFAULT '',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_role_skills (
                id BIGSERIAL PRIMARY KEY,
                job_role_id INTEGER NOT NULL REFERENCES job_roles(id) ON DELETE CASCADE,
                skill_name VARCHAR(100) NOT NULL,
                is_required INTEGER DEFAULT 1
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS career_roadmaps (
                id BIGSERIAL PRIMARY KEY,
                job_role_id INTEGER NOT NULL REFERENCES job_roles(id) ON DELETE CASCADE,
                title VARCHAR(200) NOT NULL,
                description TEXT DEFAULT '',
                duration_weeks INTEGER DEFAULT 12,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roadmap_steps (
                id BIGSERIAL PRIMARY KEY,
                roadmap_id INTEGER NOT NULL REFERENCES career_roadmaps(id) ON DELETE CASCADE,
                step_number INTEGER NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT DEFAULT '',
                duration_weeks INTEGER DEFAULT 2,
                skills TEXT DEFAULT '',
                resources TEXT DEFAULT ''
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id BIGSERIAL PRIMARY KEY,
                admin_user_id INTEGER NOT NULL,
                admin_username VARCHAR(50) NOT NULL,
                action VARCHAR(100) NOT NULL,
                target_type VARCHAR(50) NOT NULL,
                target_id VARCHAR(100),
                details TEXT DEFAULT '',
                ip_address VARCHAR(50) DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_roadmap_progress (
                id BIGSERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                analysis_id INTEGER,
                phase_index INTEGER NOT NULL,
                task_index INTEGER NOT NULL,
                completed INTEGER DEFAULT 0,
                completed_at TIMESTAMP,
                CONSTRAINT uq_user_roadmap_progress UNIQUE (user_id, analysis_id, phase_index, task_index)
            )
        """)
        cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_roadmap_progress_unique "
            "ON user_roadmap_progress (user_id, COALESCE(analysis_id, -1), phase_index, task_index)"
        )

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_attempts (
                username VARCHAR(100) PRIMARY KEY,
                attempts INTEGER DEFAULT 0,
                first_attempt INTEGER NOT NULL,
                locked_until INTEGER DEFAULT 0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_categories (
                id BIGSERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skills (
                id BIGSERIAL PRIMARY KEY,
                category_id INTEGER NOT NULL REFERENCES skill_categories(id) ON DELETE CASCADE,
                name VARCHAR(100) NOT NULL,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uq_skills_category_name UNIQUE (category_id, name)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS role_synonyms (
                id BIGSERIAL PRIMARY KEY,
                role_key VARCHAR(100) UNIQUE NOT NULL,
                categories TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_aliases (
                id BIGSERIAL PRIMARY KEY,
                alias VARCHAR(100) UNIQUE NOT NULL,
                canonical_skill VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS field_keywords (
                id BIGSERIAL PRIMARY KEY,
                field_name VARCHAR(100) NOT NULL,
                keyword VARCHAR(100) NOT NULL,
                weight INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uq_field_keywords UNIQUE (field_name, keyword)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS industry_trends (
                id BIGSERIAL PRIMARY KEY,
                field_name VARCHAR(100) NOT NULL,
                trend_type VARCHAR(50) NOT NULL,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uq_industry_trends UNIQUE (field_name, trend_type)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_role_aliases (
                id BIGSERIAL PRIMARY KEY,
                alias VARCHAR(100) UNIQUE NOT NULL,
                target_field VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_recommendations (
                id BIGSERIAL PRIMARY KEY,
                field_name VARCHAR(100) NOT NULL,
                skill_name VARCHAR(100) NOT NULL,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uq_skill_recommendations UNIQUE (field_name, skill_name)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roadmap_templates (
                id BIGSERIAL PRIMARY KEY,
                field_name VARCHAR(100) NOT NULL,
                step_number INTEGER NOT NULL,
                title VARCHAR(200) NOT NULL,
                duration VARCHAR(50) NOT NULL,
                skills TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uq_roadmap_templates UNIQUE (field_name, step_number)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_actions (
                id BIGSERIAL PRIMARY KEY,
                skill_name VARCHAR(100) NOT NULL,
                difficulty INTEGER NOT NULL,
                action_text TEXT NOT NULL,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uq_learning_actions UNIQUE (skill_name, action_text)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_resources (
                id BIGSERIAL PRIMARY KEY,
                skill_name VARCHAR(100) NOT NULL,
                title VARCHAR(300) NOT NULL,
                url TEXT NOT NULL,
                resource_type VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uq_learning_resources UNIQUE (skill_name, title)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_difficulty (
                id BIGSERIAL PRIMARY KEY,
                skill_name VARCHAR(100) UNIQUE NOT NULL,
                difficulty_level INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_clusters (
                id BIGSERIAL PRIMARY KEY,
                cluster_name VARCHAR(100) NOT NULL,
                skill_name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uq_skill_clusters UNIQUE (cluster_name, skill_name)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS video_resources (
                id BIGSERIAL PRIMARY KEY,
                field_name VARCHAR(100) NOT NULL,
                video_type VARCHAR(50) NOT NULL,
                url TEXT NOT NULL,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uq_video_resources UNIQUE (field_name, video_type, url)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS role_configs (
                id BIGSERIAL PRIMARY KEY,
                role_key VARCHAR(100) UNIQUE NOT NULL,
                project_types TEXT NOT NULL,
                interview_focus TEXT NOT NULL,
                portfolio_emphasis TEXT NOT NULL,
                key_tools TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # --- Guard: never allow the last admin to be removed/demoted ---
        # Application code checks this too, but that guard has been bypassed
        # before. This is the database-level backstop.
        cursor.execute("""
            CREATE OR REPLACE FUNCTION ensure_admin_remains() RETURNS TRIGGER AS $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM users WHERE role = 'admin') THEN
                    RAISE EXCEPTION 'Refusing to leave the system with no admin account';
                END IF;
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql
        """)
        cursor.execute("DROP TRIGGER IF EXISTS trg_ensure_admin_remains ON users")
        cursor.execute("""
            CREATE CONSTRAINT TRIGGER trg_ensure_admin_remains
            AFTER DELETE OR UPDATE OF role ON users
            DEFERRABLE INITIALLY DEFERRED
            FOR EACH ROW EXECUTE FUNCTION ensure_admin_remains()
        """)

        # --- Indexes ---
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_data_user_id ON user_data(user_id)")
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_data_timestamp ON user_data("Timestamp")')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_data_predicted_field ON user_data("Predicted_Field")')
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_otp_codes_email ON otp_codes(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shared_reports_token ON shared_reports(token)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rate_limits_updated ON rate_limits(updated_at)")

        # --- Admin account ---
        admin_user = os.getenv("ADMIN_USERNAME", "")
        admin_pass = os.getenv("ADMIN_PASSWORD", "")
        if admin_user and admin_pass:
            from api.security import get_password_hash
            hashed = get_password_hash(admin_pass)

            cursor.execute("SELECT id, role FROM users WHERE username = %s", (admin_user,))
            existing = cursor.fetchone()

            cursor.execute("SELECT id, username FROM users WHERE role = 'admin' LIMIT 1")
            any_admin = cursor.fetchone()

            if existing:
                cursor.execute('''
                    UPDATE users SET email = %s, full_name = %s, hashed_password = %s, role = %s
                    WHERE username = %s
                ''', (f"{admin_user}@skillpath.ai", "System Admin", hashed, "admin", admin_user))
            elif not any_admin:
                cursor.execute('''
                    INSERT INTO users (username, email, full_name, hashed_password, role)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (admin_user, f"{admin_user}@skillpath.ai", "System Admin", hashed, "admin"))
            else:
                logger.warning(
                    f"Admin account already exists as '{any_admin['username']}'. "
                    f"Configured admin '{admin_user}' was not created to avoid duplicates."
                )

        # --- Fix is_required flags on job_role_skills ---
        # Single round-trip: build the desired state in Python, then apply it
        # with one UPDATE ... FROM (VALUES ...) instead of one query per row.
        cursor.execute("SELECT jr.id, jr.title, js.skill_name FROM job_role_skills js JOIN job_roles jr ON js.job_role_id = jr.id")
        desired_flags = [
            (row["id"], row["skill_name"],
             1 if row["skill_name"] in CORE_SKILLS_BY_ROLE.get(row["title"], set()) else 0)
            for row in cursor.fetchall()
        ]
        if desired_flags:
            psycopg2.extras.execute_values(
                cursor,
                """
                UPDATE job_role_skills AS js
                SET is_required = v.is_required
                FROM (VALUES %s) AS v(job_role_id, skill_name, is_required)
                WHERE js.job_role_id = v.job_role_id
                  AND js.skill_name = v.skill_name
                  AND js.is_required IS DISTINCT FROM v.is_required
                """,
                desired_flags,
                template="(%s::int, %s::varchar, %s::int)",
            )

        # --- Cleanup expired entries ---
        cursor.execute("DELETE FROM analysis_cache WHERE expires_at IS NOT NULL AND expires_at < %s",
                       (int(time.time()),))
        cursor.execute("DELETE FROM rate_limits WHERE updated_at < %s", (int(time.time() // 60) - 5,))

        # --- Seed default job roles if empty ---
        cursor.execute("SELECT COUNT(*) as cnt FROM job_roles")
        row = cursor.fetchone()
        count = row["cnt"]
        if count == 0:
            for title, desc, category in DEFAULT_ROLES:
                cursor.execute(
                    "INSERT INTO job_roles (title, description, category) VALUES (%s, %s, %s) RETURNING id",
                    (title, desc, category)
                )
                role_id = cursor.fetchone()["id"]
                skills_for_role = DEFAULT_ROLE_SKILLS.get(title, {})
                for skill in skills_for_role.get("required", []):
                    cursor.execute(
                        "INSERT INTO job_role_skills (job_role_id, skill_name, is_required) VALUES (%s, %s, 1)",
                        (role_id, skill)
                    )
                for skill in skills_for_role.get("nice_to_have", []):
                    cursor.execute(
                        "INSERT INTO job_role_skills (job_role_id, skill_name, is_required) VALUES (%s, %s, 0)",
                        (role_id, skill)
                    )
                roadmap = DEFAULT_ROADMAPS.get(title)
                if roadmap:
                    cursor.execute(
                        "INSERT INTO career_roadmaps (job_role_id, title, description, duration_weeks, sort_order) VALUES (%s, %s, %s, %s, 1) RETURNING id",
                        (role_id, roadmap['title'], roadmap['description'], roadmap['duration_weeks'])
                    )
                    roadmap_id = cursor.fetchone()["id"]
                    for step in roadmap['steps']:
                        cursor.execute(
                            "INSERT INTO roadmap_steps (roadmap_id, step_number, title, description, duration_weeks, skills, resources) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                            (roadmap_id, step['step'], step['title'], step['description'], step['duration_weeks'], step['skills'], step['resources'])
                        )

        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            _release_connection(conn)


init_db()
