import sqlite3
import os
import time
import json
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, event

logger = logging.getLogger("resume-analyzer")

from api.seed_defaults import (
    CORE_SKILLS_BY_ROLE,
    DEFAULT_ROLES,
    DEFAULT_ROLE_SKILLS,
    DEFAULT_ROADMAPS,
)


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

DB_FILE = os.getenv("DB_FILE") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "cv.db"
)

engine = create_engine(
    f"sqlite:///{DB_FILE}",
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()
    dbapi_connection.row_factory = sqlite3.Row


def get_db_connection():
    return engine.raw_connection()


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
    cursor.execute(f"PRAGMA table_info({table})")
    existing = {row[1] for row in cursor.fetchall()}
    if col not in existing:
        if default is not None:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typedef} DEFAULT {default}")
        else:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typedef}")


def init_db():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_data (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                sec_token varchar(20) NOT NULL,
                ip_add varchar(50) NULL,
                host_name varchar(50) NULL,
                dev_user varchar(50) NULL,
                os_name_ver varchar(50) NULL,
                latlong varchar(50) NULL,
                city varchar(50) NULL,
                state varchar(50) NULL,
                country varchar(50) NULL,
                act_name varchar(255) NOT NULL DEFAULT '',
                act_mail varchar(255) NOT NULL DEFAULT '',
                act_mob varchar(50) NOT NULL DEFAULT '',
                Name varchar(500) NOT NULL,
                Email_ID VARCHAR(500) NOT NULL,
                resume_score VARCHAR(8) NOT NULL,
                Timestamp VARCHAR(50) NOT NULL,
                Page_no VARCHAR(5) NOT NULL,
                Predicted_Field TEXT NOT NULL DEFAULT '',
                User_level TEXT NOT NULL DEFAULT '',
                Actual_skills TEXT NOT NULL DEFAULT '',
                Recommended_skills TEXT NOT NULL DEFAULT '',
                Recommended_courses TEXT NOT NULL DEFAULT '',
                pdf_name varchar(255) NOT NULL,
                target_role VARCHAR(200) DEFAULT 'Unknown',
                missing_skills TEXT DEFAULT '',
                user_id INTEGER DEFAULT -1,
                analysis_data TEXT DEFAULT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_feedback (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                feed_name varchar(50) NOT NULL,
                feed_email VARCHAR(120) NOT NULL,
                feed_score INTEGER NOT NULL CHECK(feed_score BETWEEN 1 AND 5),
                comments VARCHAR(2000) NULL,
                Timestamp VARCHAR(50) NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                last_scraped TIMESTAMP DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        _ensure_column(cursor, 'courses', 'description', 'TEXT DEFAULT ""')
        _ensure_column(cursor, 'courses', 'instructor', 'VARCHAR(200) DEFAULT ""')
        _ensure_column(cursor, 'courses', 'rating', 'REAL DEFAULT 0')
        _ensure_column(cursor, 'courses', 'duration', 'VARCHAR(50) DEFAULT ""')
        _ensure_column(cursor, 'courses', 'price', 'VARCHAR(50) DEFAULT ""')
        _ensure_column(cursor, 'courses', 'platform', 'VARCHAR(50) DEFAULT ""')
        _ensure_column(cursor, 'courses', 'enrollment_count', 'INTEGER DEFAULT 0')
        _ensure_column(cursor, 'courses', 'last_scraped', 'TIMESTAMP DEFAULT NULL')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                full_name VARCHAR(100) DEFAULT 'User',
                hashed_password VARCHAR(255) NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'user')),
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        _ensure_column(cursor, 'users', 'is_active', 'INTEGER', '1')
        _ensure_column(cursor, 'users', 'email_verified', 'INTEGER', '1')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS otp_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(120) NOT NULL,
                purpose VARCHAR(30) NOT NULL,
                code_hash VARCHAR(64) NOT NULL,
                expires_at INTEGER NOT NULL,
                attempts INTEGER DEFAULT 0,
                used INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_otp_codes_email ON otp_codes(email, purpose)")

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_trends_cache (
                field VARCHAR(200) PRIMARY KEY,
                source VARCHAR(40) NOT NULL,
                payload TEXT NOT NULL,
                fetched_at INTEGER NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                token VARCHAR(64) PRIMARY KEY,
                user_id INTEGER NOT NULL,
                expires_at INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                token VARCHAR(128) PRIMARY KEY,
                user_id INTEGER NOT NULL,
                expires_at INTEGER NOT NULL,
                used INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY,
                full_name VARCHAR(200) DEFAULT '',
                phone VARCHAR(50) DEFAULT '',
                location VARCHAR(200) DEFAULT '',
                bio TEXT DEFAULT '',
                current_role VARCHAR(100) DEFAULT '',
                experience_years VARCHAR(10) DEFAULT '',
                linkedin_url VARCHAR(500) DEFAULT '',
                github_url VARCHAR(500) DEFAULT '',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY,
                target_role VARCHAR(200) DEFAULT '',
                timeline_months INTEGER DEFAULT 6,
                preferred_location VARCHAR(200) DEFAULT '',
                salary_target INTEGER DEFAULT 0,
                locale VARCHAR(20) DEFAULT 'en',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shared_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token VARCHAR(80) UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                analysis_id INTEGER NOT NULL,
                expires_at INTEGER NOT NULL,
                is_public INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                channel VARCHAR(30) NOT NULL DEFAULT 'email',
                message TEXT NOT NULL,
                status VARCHAR(30) NOT NULL DEFAULT 'pending',
                send_at INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                user_id INTEGER PRIMARY KEY,
                plan VARCHAR(40) NOT NULL DEFAULT 'free',
                status VARCHAR(30) NOT NULL DEFAULT 'active',
                renews_at INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS request_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id VARCHAR(80) NOT NULL,
                method VARCHAR(10) NOT NULL,
                path VARCHAR(300) NOT NULL,
                status_code INTEGER NOT NULL,
                elapsed_ms REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_cache (
                content_hash VARCHAR(64) NOT NULL,
                target_role VARCHAR(200) NOT NULL DEFAULT '',
                result_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at INTEGER,
                PRIMARY KEY (content_hash, target_role)
            )
        ''')
        _ensure_column(cursor, 'analysis_cache', 'expires_at', 'INTEGER')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rate_limits (
                key VARCHAR(100) PRIMARY KEY,
                count INTEGER DEFAULT 0,
                updated_at INTEGER NOT NULL
            )
        ''')
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rate_limits_updated ON rate_limits(updated_at)")

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                description TEXT DEFAULT '',
                category VARCHAR(100) DEFAULT '',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_role_skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_role_id INTEGER NOT NULL,
                skill_name VARCHAR(100) NOT NULL,
                is_required INTEGER DEFAULT 1,
                FOREIGN KEY (job_role_id) REFERENCES job_roles(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS career_roadmaps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_role_id INTEGER NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT DEFAULT '',
                duration_weeks INTEGER DEFAULT 12,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_role_id) REFERENCES job_roles(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roadmap_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roadmap_id INTEGER NOT NULL,
                step_number INTEGER NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT DEFAULT '',
                duration_weeks INTEGER DEFAULT 2,
                skills TEXT DEFAULT '',
                resources TEXT DEFAULT '',
                FOREIGN KEY (roadmap_id) REFERENCES career_roadmaps(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_user_id INTEGER NOT NULL,
                admin_username VARCHAR(50) NOT NULL,
                action VARCHAR(100) NOT NULL,
                target_type VARCHAR(50) NOT NULL,
                target_id VARCHAR(100),
                details TEXT DEFAULT '',
                ip_address VARCHAR(50) DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_roadmap_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                analysis_id INTEGER,
                phase_index INTEGER NOT NULL,
                task_index INTEGER NOT NULL,
                completed INTEGER DEFAULT 0,
                completed_at TIMESTAMP,
                UNIQUE(user_id, analysis_id, phase_index, task_index),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_attempts (
                username VARCHAR(100) PRIMARY KEY,
                attempts INTEGER DEFAULT 0,
                first_attempt INTEGER NOT NULL,
                locked_until INTEGER DEFAULT 0
            )
        ''')

        # Skills taxonomy tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skill_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) UNIQUE NOT NULL,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                name VARCHAR(100) NOT NULL,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES skill_categories(id) ON DELETE CASCADE,
                UNIQUE(category_id, name)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS role_synonyms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_key VARCHAR(100) UNIQUE NOT NULL,
                categories TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skill_aliases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alias VARCHAR(100) UNIQUE NOT NULL,
                canonical_skill VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Field keywords table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS field_keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                field_name VARCHAR(100) NOT NULL,
                keyword VARCHAR(100) NOT NULL,
                weight INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(field_name, keyword)
            )
        ''')

        # Industry trends table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS industry_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                field_name VARCHAR(100) NOT NULL,
                trend_type VARCHAR(50) NOT NULL,
                data JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(field_name, trend_type)
            )
        ''')

        # Role aliases table (for market data normalization)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_role_aliases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alias VARCHAR(100) UNIQUE NOT NULL,
                target_field VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Skill recommendations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skill_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                field_name VARCHAR(100) NOT NULL,
                skill_name VARCHAR(100) NOT NULL,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(field_name, skill_name)
            )
        ''')

        # Roadmap templates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roadmap_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                field_name VARCHAR(100) NOT NULL,
                step_number INTEGER NOT NULL,
                title VARCHAR(200) NOT NULL,
                duration VARCHAR(50) NOT NULL,
                skills JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(field_name, step_number)
            )
        ''')

        # Learning actions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name VARCHAR(100) NOT NULL,
                difficulty INTEGER NOT NULL,
                action_text TEXT NOT NULL,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(skill_name, action_text)
            )
        ''')

        # Learning resources table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name VARCHAR(100) NOT NULL,
                title VARCHAR(300) NOT NULL,
                url TEXT NOT NULL,
                resource_type VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(skill_name, title)
            )
        ''')

        # Skill difficulty table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skill_difficulty (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name VARCHAR(100) UNIQUE NOT NULL,
                difficulty_level INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Skill clusters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skill_clusters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cluster_name VARCHAR(100) NOT NULL,
                skill_name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(cluster_name, skill_name)
            )
        ''')

        # Video resources table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                field_name VARCHAR(100) NOT NULL,
                video_type VARCHAR(50) NOT NULL,
                url TEXT NOT NULL,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(field_name, video_type, url)
            )
        ''')

        # Role configs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS role_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_key VARCHAR(100) UNIQUE NOT NULL,
                project_types JSON NOT NULL,
                interview_focus JSON NOT NULL,
                portfolio_emphasis TEXT NOT NULL,
                key_tools JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

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
        cursor.execute("PRAGMA table_info(user_data)")
        ud_cols = {r[1] for r in cursor.fetchall()}
        if 'content_hash' not in ud_cols:
            cursor.execute("ALTER TABLE user_data ADD COLUMN content_hash VARCHAR(64) DEFAULT NULL")

        # Fix is_required flags: mark core skills as required, others as nice-to-have
        for role_id, role_title, skill_name in cursor.fetchall():
            core = CORE_SKILLS_BY_ROLE.get(role_title, set())
            desired = 1 if skill_name in core else 0
            cursor.execute(
                "UPDATE job_role_skills SET is_required = ? WHERE job_role_id = ? AND skill_name = ?",
                (desired, role_id, skill_name)
            )

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shared_reports_token ON shared_reports(token)")

        cursor.execute("DELETE FROM analysis_cache WHERE expires_at IS NOT NULL AND expires_at < ?",
                       (int(time.time()),))
        cursor.execute("DELETE FROM rate_limits WHERE updated_at < ?", (int(time.time() // 60) - 5,))

        # Seed default job roles if empty
        cursor.execute("SELECT COUNT(*) FROM job_roles")
        if cursor.fetchone()[0] == 0:
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
