import sqlite3
import os
import time
import json
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, event

logger = logging.getLogger("resume-analyzer")

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
        _core_skills_by_role = {
            "Software Engineering": {"Python", "Java", "Git", "Data Structures", "Algorithms", "SQL"},
            "Frontend Development": {"JavaScript", "React", "HTML", "CSS", "TypeScript", "Git"},
            "Backend Development": {"Python", "Node.js", "SQL", "REST APIs", "Docker", "Git"},
            "Data Science": {"Python", "SQL", "Machine Learning", "Pandas", "NumPy", "Statistics"},
            "DevOps": {"Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Git"},
            "Mobile Development": {"React Native", "Flutter", "Swift", "Kotlin", "Git", "REST APIs"},
            "Full Stack Development": {"JavaScript", "React", "Node.js", "Python", "SQL", "Git"},
            "Cybersecurity": {"Networking", "Linux", "Python", "SIEM", "Penetration Testing", "Encryption"},
        }
        cursor.execute("SELECT jr.id, jr.title, jrs.skill_name FROM job_role_skills jrs JOIN job_roles jr ON jrs.job_role_id = jr.id")
        for role_id, role_title, skill_name in cursor.fetchall():
            core = _core_skills_by_role.get(role_title, set())
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
            default_roles = [
                ("Software Engineering", "Design, develop, and maintain software systems", "Engineering"),
                ("Frontend Development", "Build user interfaces and client-side applications", "Engineering"),
                ("Backend Development", "Develop server-side logic and APIs", "Engineering"),
                ("Data Science", "Analyze data and build machine learning models", "Data"),
                ("DevOps", "Manage infrastructure, CI/CD, and deployment", "Engineering"),
                ("Mobile Development", "Build mobile applications for iOS and Android", "Engineering"),
                ("Full Stack Development", "Develop both frontend and backend applications", "Engineering"),
                ("Cybersecurity", "Protect systems and networks from security threats", "Security"),
                ("Product Management", "Define product vision, strategy, and roadmap", "Product"),
                ("Business Analysis", "Analyze business needs and translate to technical requirements", "Business"),
                ("Technical Writing", "Create clear documentation for technical audiences", "Content"),
                ("IT Support", "Provide technical assistance and maintain IT systems", "Operations"),
                ("Network Administration", "Manage and maintain network infrastructure", "Operations"),
                ("Cloud Engineering", "Design and manage cloud-based infrastructure", "Engineering"),
                ("Data Engineering", "Build and maintain data pipelines and infrastructure", "Data"),
                ("Machine Learning", "Develop and deploy machine learning models", "Data"),
                ("Cloud Architecture", "Design scalable cloud solutions and architectures", "Engineering"),
                ("Web Development", "Build and maintain web applications", "Engineering"),
                ("UI/UX Design", "Design user interfaces and experiences", "Design"),
                ("Android Development", "Build applications for the Android platform", "Engineering"),
                ("iOS Development", "Build applications for the Apple ecosystem", "Engineering"),
                ("Quality Assurance", "Ensure software quality through testing", "Engineering"),
            ]
            default_role_skills = {
                "Software Engineering": {
                    "required": ["Python", "Java", "Git", "Data Structures", "Algorithms", "SQL"],
                    "nice_to_have": ["OOP", "Testing", "CI/CD", "Docker", "REST APIs", "Linux", "Design Patterns", "Debugging", "Agile"],
                },
                "Frontend Development": {
                    "required": ["JavaScript", "React", "HTML", "CSS", "TypeScript", "Git"],
                    "nice_to_have": ["REST APIs", "Responsive Design", "Vue.js", "Next.js", "Redux", "Webpack", "Accessibility", "Figma", "Jest"],
                },
                "Backend Development": {
                    "required": ["Python", "Node.js", "SQL", "REST APIs", "Docker", "Git"],
                    "nice_to_have": ["PostgreSQL", "Linux", "Redis", "MongoDB", "FastAPI", "Flask", "Microservices", "Authentication", "Caching"],
                },
                "Data Science": {
                    "required": ["Python", "SQL", "Machine Learning", "Pandas", "NumPy", "Statistics"],
                    "nice_to_have": ["R", "TensorFlow", "PyTorch", "Scikit-learn", "Data Visualization", "NLP", "Jupyter", "Feature Engineering", "A/B Testing"],
                },
                "DevOps": {
                    "required": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Git"],
                    "nice_to_have": ["Terraform", "Ansible", "Jenkins", "Prometheus", "Grafana", "Nginx", "Bash", "Monitoring", "Load Balancing"],
                },
                "Mobile Development": {
                    "required": ["React Native", "Flutter", "Swift", "Kotlin", "Git", "REST APIs"],
                    "nice_to_have": ["Firebase", "UI/UX", "iOS", "Android", "State Management", "Testing", "Push Notifications", "App Store", "Performance"],
                },
                "Full Stack Development": {
                    "required": ["JavaScript", "React", "Node.js", "Python", "SQL", "Git"],
                    "nice_to_have": ["Docker", "REST APIs", "PostgreSQL", "MongoDB", "Redis", "TypeScript", "Express", "Authentication", "Deployment"],
                },
                "Cybersecurity": {
                    "required": ["Networking", "Linux", "Python", "SIEM", "Penetration Testing", "Encryption"],
                    "nice_to_have": ["Firewalls", "Compliance", "Incident Response", "Vulnerability Assessment", "Nmap", "Wireshark", "Cryptography", "Forensics", "Active Directory"],
                },
                "Product Management": {
                    "required": ["Product Strategy", "Agile", "User Research", "Roadmapping", "Stakeholder Management", "Data Analysis"],
                    "nice_to_have": ["SQL", "A/B Testing", "Jira", "Figma", "Market Research", "OKRs", "Go-to-Market", "Metrics", "Wireframing"],
                },
                "Business Analysis": {
                    "required": ["Requirements Gathering", "SQL", "Process Modeling", "Stakeholder Management", "Data Analysis", "Documentation"],
                    "nice_to_have": ["UML", "BPMN", "Jira", "Confluence", "Wireframing", "Agile", "Visio", "Python", "ETL"],
                },
                "Technical Writing": {
                    "required": ["Documentation", "Markdown", "API Documentation", "Content Strategy", "Editing", "Grammar"],
                    "nice_to_have": ["Git", "HTML", "DITA", "MadCap Flare", "Screenshots", "Video Tutorials", "Style Guides", "Information Architecture", "Localization"],
                },
                "IT Support": {
                    "required": ["Windows", "Linux", "Networking", "Active Directory", "Troubleshooting", "Hardware"],
                    "nice_to_have": ["Azure", "Office 365", "Scripting", "Virtualization", "Ticketing Systems", "Security", "CompTIA A+", "Remote Support", "Backup"],
                },
                "Network Administration": {
                    "required": ["TCP/IP", "DNS", "DHCP", "Firewalls", "Linux", "Routing"],
                    "nice_to_have": ["Cisco", "VLANs", "VPN", "Network Monitoring", "Cloud Networking", "Security", "Load Balancing", "Wireshark", "CompTIA Network+"],
                },
                "Cloud Engineering": {
                    "required": ["AWS", "Docker", "Kubernetes", "Terraform", "CI/CD", "Linux"],
                    "nice_to_have": ["Azure", "GCP", "Ansible", "Monitoring", "Security", "Networking", "Serverless", "Infrastructure as Code", "Cost Optimization"],
                },
                "Data Engineering": {
                    "required": ["Python", "SQL", "Apache Spark", "ETL", "Data Modeling", "AWS"],
                    "nice_to_have": ["Airflow", "Kafka", "Redshift", "Snowflake", "dbt", "Hadoop", "Data Lake", "Delta Lake", "Data Quality"],
                },
                "Machine Learning": {
                    "required": ["Python", "Machine Learning", "TensorFlow", "PyTorch", "SQL", "Statistics"],
                    "nice_to_have": ["Scikit-learn", "NLP", "Computer Vision", "MLOps", "Feature Engineering", "Deep Learning", "AWS SageMaker", "MLflow", "Docker"],
                },
                "Cloud Architecture": {
                    "required": ["AWS", "Azure", "System Design", "Networking", "Security", "Terraform"],
                    "nice_to_have": ["Microservices", "Serverless", "Containers", "Cost Optimization", "Disaster Recovery", "Compliance", "Load Balancing", "CDN", "Multi-Cloud"],
                },
                "Web Development": {
                    "required": ["JavaScript", "HTML", "CSS", "React", "Node.js", "Git"],
                    "nice_to_have": ["TypeScript", "Next.js", "PostgreSQL", "MongoDB", "Docker", "REST APIs", "Testing", "CI/CD", "Performance"],
                },
                "UI/UX Design": {
                    "required": ["Figma", "User Research", "Wireframing", "Prototyping", "Interaction Design", "Usability Testing"],
                    "nice_to_have": ["Adobe XD", "Sketch", "Design Systems", "HTML/CSS", "Accessibility", "Information Architecture", "User Personas", "Journey Mapping", "Motion Design"],
                },
                "Android Development": {
                    "required": ["Kotlin", "Android Studio", "Jetpack Compose", "REST APIs", "Git", "Material Design"],
                    "nice_to_have": ["Java", "Room DB", "Coroutines", "Retrofit", "MVVM", "Firebase", "Testing", "Play Store", "Push Notifications"],
                },
                "iOS Development": {
                    "required": ["Swift", "SwiftUI", "UIKit", "REST APIs", "Git", "Xcode"],
                    "nice_to_have": ["CoreData", "Combine", "ARKit", "Core ML", "App Store", "AutoLayout", "Networking", "Testing", "Performance"],
                },
                "Quality Assurance": {
                    "required": ["Test Automation", "Selenium", "API Testing", "SQL", "Bug Tracking", "Agile"],
                    "nice_to_have": ["Cypress", "Jest", "Postman", "CI/CD", "Performance Testing", "Security Testing", "Test Plans", "Regression Testing", "Jira"],
                },
            }
            default_roadmaps = {
                "Software Engineering": {
                    "title": "Software Engineering Career Path",
                    "description": "Master the fundamentals of software engineering",
                    "duration_weeks": 24,
                    "steps": [
                        {"step": 1, "title": "Programming Fundamentals", "description": "Learn core programming concepts", "duration_weeks": 4, "skills": "Python,OOP,Data Structures", "resources": "https://www.youtube.com/results?search_query=python+programming+fundamentals"},
                        {"step": 2, "title": "Version Control", "description": "Master Git and collaboration workflows", "duration_weeks": 2, "skills": "Git,GitHub,Branching", "resources": "https://www.youtube.com/results?search_query=git+tutorial"},
                        {"step": 3, "title": "Testing & Quality", "description": "Write reliable, tested code", "duration_weeks": 3, "skills": "Unit Testing,TDD,Debugging", "resources": "https://www.youtube.com/results?search_query=software+testing"},
                        {"step": 4, "title": "System Design", "description": "Design scalable software systems", "duration_weeks": 5, "skills": "Architecture,Design Patterns,APIs", "resources": "https://www.youtube.com/results?search_query=system+design"},
                    ]
                },
                "Frontend Development": {
                    "title": "Frontend Developer Roadmap",
                    "description": "Build modern, responsive web interfaces",
                    "duration_weeks": 20,
                    "steps": [
                        {"step": 1, "title": "HTML & CSS", "description": "Master web fundamentals", "duration_weeks": 3, "skills": "HTML5,CSS3,Flexbox,Grid", "resources": "https://www.youtube.com/results?search_query=html+css+tutorial"},
                        {"step": 2, "title": "JavaScript", "description": "Learn modern JavaScript", "duration_weeks": 4, "skills": "JavaScript,ES6+,DOM", "resources": "https://www.youtube.com/results?search_query=javascript+tutorial"},
                        {"step": 3, "title": "React", "description": "Build component-based UIs", "duration_weeks": 5, "skills": "React,Hooks,State Management", "resources": "https://www.youtube.com/results?search_query=react+tutorial"},
                        {"step": 4, "title": "Performance", "description": "Optimize web applications", "duration_weeks": 3, "skills": "Lighthouse,Webpack,Optimization", "resources": "https://www.youtube.com/results?search_query=web+performance"},
                    ]
                },
                "Backend Development": {
                    "title": "Backend Developer Roadmap",
                    "description": "Build robust server-side applications",
                    "duration_weeks": 22,
                    "steps": [
                        {"step": 1, "title": "Programming Basics", "description": "Learn a backend language", "duration_weeks": 4, "skills": "Python,Node.js,Go", "resources": "https://www.youtube.com/results?search_query=backend+programming"},
                        {"step": 2, "title": "Databases", "description": "Master data persistence", "duration_weeks": 4, "skills": "SQL,PostgreSQL,MongoDB", "resources": "https://www.youtube.com/results?search_query=database+tutorial"},
                        {"step": 3, "title": "APIs", "description": "Design and build APIs", "duration_weeks": 4, "skills": "REST,GraphQL,Authentication", "resources": "https://www.youtube.com/results?search_query=rest+api+tutorial"},
                        {"step": 4, "title": "DevOps Basics", "description": "Deploy and scale applications", "duration_weeks": 4, "skills": "Docker,Linux,CI/CD", "resources": "https://www.youtube.com/results?search_query=devops+tutorial"},
                    ]
                },
                "Data Science": {
                    "title": "Data Science Career Path",
                    "description": "Analyze data and build ML models",
                    "duration_weeks": 26,
                    "steps": [
                        {"step": 1, "title": "Python for Data", "description": "Learn data manipulation", "duration_weeks": 4, "skills": "Python,Pandas,NumPy", "resources": "https://www.youtube.com/results?search_query=python+data+science"},
                        {"step": 2, "title": "Statistics", "description": "Master statistical concepts", "duration_weeks": 4, "skills": "Statistics,Probability,Hypothesis Testing", "resources": "https://www.youtube.com/results?search_query=statistics+for+data+science"},
                        {"step": 3, "title": "Machine Learning", "description": "Build predictive models", "duration_weeks": 6, "skills": "Scikit-learn,ML Algorithms,Model Evaluation", "resources": "https://www.youtube.com/results?search_query=machine+learning+tutorial"},
                        {"step": 4, "title": "Deep Learning", "description": "Neural networks and advanced ML", "duration_weeks": 6, "skills": "TensorFlow,PyTorch,Neural Networks", "resources": "https://www.youtube.com/results?search_query=deep+learning+tutorial"},
                    ]
                },
                "DevOps": {
                    "title": "DevOps Engineer Roadmap",
                    "description": "Master infrastructure and deployment",
                    "duration_weeks": 24,
                    "steps": [
                        {"step": 1, "title": "Linux & Networking", "description": "Master OS fundamentals", "duration_weeks": 4, "skills": "Linux,Bash,Networking", "resources": "https://www.youtube.com/results?search_query=linux+tutorial"},
                        {"step": 2, "title": "Containers", "description": "Learn containerization", "duration_weeks": 4, "skills": "Docker,Kubernetes,Container Orchestration", "resources": "https://www.youtube.com/results?search_query=docker+kubernetes+tutorial"},
                        {"step": 3, "title": "CI/CD", "description": "Automate deployments", "duration_weeks": 4, "skills": "GitHub Actions,Jenkins,Pipelines", "resources": "https://www.youtube.com/results?search_query=ci+cd+tutorial"},
                        {"step": 4, "title": "Cloud", "description": "Master cloud platforms", "duration_weeks": 5, "skills": "AWS,Azure,GCP,Terraform", "resources": "https://www.youtube.com/results?search_query=aws+cloud+tutorial"},
                    ]
                },
                "Mobile Development": {
                    "title": "Mobile Developer Roadmap",
                    "description": "Build cross-platform mobile apps",
                    "duration_weeks": 22,
                    "steps": [
                        {"step": 1, "title": "Mobile Fundamentals", "description": "Learn mobile development concepts", "duration_weeks": 3, "skills": "Mobile UX,App Architecture,State", "resources": "https://www.youtube.com/results?search_query=mobile+development+basics"},
                        {"step": 2, "title": "React Native / Flutter", "description": "Build cross-platform apps", "duration_weeks": 6, "skills": "React Native,Flutter,Dart", "resources": "https://www.youtube.com/results?search_query=react+native+tutorial"},
                        {"step": 3, "title": "Backend Integration", "description": "Connect to APIs and services", "duration_weeks": 4, "skills": "REST APIs,Firebase,Authentication", "resources": "https://www.youtube.com/results?search_query=mobile+backend+integration"},
                        {"step": 4, "title": "Publishing", "description": "Deploy to app stores", "duration_weeks": 3, "skills": "App Store,Play Store,App Optimization", "resources": "https://www.youtube.com/results?search_query=app+store+publishing"},
                    ]
                },
                "Full Stack Development": {
                    "title": "Full Stack Developer Roadmap",
                    "description": "Master both frontend and backend",
                    "duration_weeks": 28,
                    "steps": [
                        {"step": 1, "title": "Frontend Basics", "description": "Learn HTML, CSS, JavaScript", "duration_weeks": 4, "skills": "HTML,CSS,JavaScript,React", "resources": "https://www.youtube.com/results?search_query=frontend+web+development"},
                        {"step": 2, "title": "Backend Basics", "description": "Learn server-side programming", "duration_weeks": 4, "skills": "Node.js,Express,REST APIs", "resources": "https://www.youtube.com/results?search_query=nodejs+backend+tutorial"},
                        {"step": 3, "title": "Databases", "description": "Master data storage", "duration_weeks": 4, "skills": "SQL,MongoDB,Redis", "resources": "https://www.youtube.com/results?search_query=database+tutorial"},
                        {"step": 4, "title": "Full Stack Projects", "description": "Build complete applications", "duration_weeks": 6, "skills": "Authentication,Deployment,Testing", "resources": "https://www.youtube.com/results?search_query=full+stack+project"},
                    ]
                },
                "Cybersecurity": {
                    "title": "Cybersecurity Career Path",
                    "description": "Protect systems from security threats",
                    "duration_weeks": 26,
                    "steps": [
                        {"step": 1, "title": "Networking Security", "description": "Master network fundamentals", "duration_weeks": 4, "skills": "TCP/IP,Firewalls,VPNs", "resources": "https://www.youtube.com/results?search_query=network+security+tutorial"},
                        {"step": 2, "title": "Operating Systems", "description": "Secure Linux and Windows", "duration_weeks": 4, "skills": "Linux,Windows,Hardening", "resources": "https://www.youtube.com/results?search_query=linux+security"},
                        {"step": 3, "title": "Ethical Hacking", "description": "Learn penetration testing", "duration_weeks": 6, "skills": "Kali Linux,Metasploit,Nmap", "resources": "https://www.youtube.com/results?search_query=ethical+hacking+tutorial"},
                        {"step": 4, "title": "Security Operations", "description": "Implement security frameworks", "duration_weeks": 5, "skills": "SIEM,Incident Response,Compliance", "resources": "https://www.youtube.com/results?search_query=security+operations"},
                    ]
                },
                "Product Management": {
                    "title": "Product Management Career Path",
                    "description": "Lead product strategy and execution",
                    "duration_weeks": 20,
                    "steps": [
                        {"step": 1, "title": "Product Fundamentals", "description": "Learn core PM concepts", "duration_weeks": 3, "skills": "Product Strategy,Market Research,User Personas", "resources": "https://www.youtube.com/results?search_query=product+management+basics"},
                        {"step": 2, "title": "Discovery & Research", "description": "Master user research methods", "duration_weeks": 4, "skills": "User Interviews,A/B Testing,Data Analysis", "resources": "https://www.youtube.com/results?search_query=user+research+product"},
                        {"step": 3, "title": "Execution & Delivery", "description": "Ship products effectively", "duration_weeks": 4, "skills": "Agile,Scrum,Jira,Roadmapping", "resources": "https://www.youtube.com/results?search_query=agile+product+management"},
                        {"step": 4, "title": "Growth & Strategy", "description": "Drive product growth", "duration_weeks": 5, "skills": "OKRs,Go-to-Market,Metrics,Stakeholder Management", "resources": "https://www.youtube.com/results?search_query=product+growth+strategy"},
                    ]
                },
                "Business Analysis": {
                    "title": "Business Analysis Career Path",
                    "description": "Bridge business needs and technical solutions",
                    "duration_weeks": 18,
                    "steps": [
                        {"step": 1, "title": "BA Fundamentals", "description": "Learn requirements engineering", "duration_weeks": 3, "skills": "Requirements Gathering,Documentation,Stakeholder Analysis", "resources": "https://www.youtube.com/results?search_query=business+analysis+basics"},
                        {"step": 2, "title": "Process Modeling", "description": "Map business processes", "duration_weeks": 3, "skills": "UML,BPMN,Flowcharts,Process Mapping", "resources": "https://www.youtube.com/results?search_query=process+modeling+business"},
                        {"step": 3, "title": "Data & Analysis", "description": "Use data for decision making", "duration_weeks": 4, "skills": "SQL,Data Analysis,Excel,Wireframing", "resources": "https://www.youtube.com/results?search_query=data+analysis+business"},
                        {"step": 4, "title": "Advanced BA", "description": "Master strategic analysis", "duration_weeks": 4, "skills": "ETL,Confluence,Jira,Agile", "resources": "https://www.youtube.com/results?search_query=advanced+business+analysis"},
                    ]
                },
                "Technical Writing": {
                    "title": "Technical Writing Career Path",
                    "description": "Create clear, effective technical documentation",
                    "duration_weeks": 16,
                    "steps": [
                        {"step": 1, "title": "Writing Fundamentals", "description": "Master technical writing basics", "duration_weeks": 3, "skills": "Documentation,Markdown,Editing,Grammar", "resources": "https://www.youtube.com/results?search_query=technical+writing+basics"},
                        {"step": 2, "title": "API Documentation", "description": "Write API references and guides", "duration_weeks": 3, "skills": "API Documentation,OpenAPI,Swagger,Code Samples", "resources": "https://www.youtube.com/results?search_query=api+documentation"},
                        {"step": 3, "title": "Content Strategy", "description": "Plan and organize documentation", "duration_weeks": 4, "skills": "Content Strategy,Information Architecture,Style Guides", "resources": "https://www.youtube.com/results?search_query=content+strategy+technical"},
                        {"step": 4, "title": "Advanced Topics", "description": "Specialize in advanced documentation", "duration_weeks": 4, "skills": "DITA,Localization,Video Tutorials,Screenshots", "resources": "https://www.youtube.com/results?search_query=advanced+technical+writing"},
                    ]
                },
                "IT Support": {
                    "title": "IT Support Career Path",
                    "description": "Provide technical assistance and maintain systems",
                    "duration_weeks": 18,
                    "steps": [
                        {"step": 1, "title": "Hardware & OS", "description": "Master computer fundamentals", "duration_weeks": 3, "skills": "Hardware,Windows,Linux,CompTIA A+", "resources": "https://www.youtube.com/results?search_query=it+support+hardware"},
                        {"step": 2, "title": "Networking", "description": "Learn network basics", "duration_weeks": 3, "skills": "Networking,TCP/IP,DNS,DHCP", "resources": "https://www.youtube.com/results?search_query=it+networking+basics"},
                        {"step": 3, "title": "Active Directory & Cloud", "description": "Manage users and cloud services", "duration_weeks": 4, "skills": "Active Directory,Office 365,Azure,Remote Support", "resources": "https://www.youtube.com/results?search_query=active+directory+tutorial"},
                        {"step": 4, "title": "Security & Scripting", "description": "Automate and secure IT", "duration_weeks": 4, "skills": "Security,Scripting,Backup,Ticketing Systems", "resources": "https://www.youtube.com/results?search_query=it+security+scripting"},
                    ]
                },
                "Network Administration": {
                    "title": "Network Administration Career Path",
                    "description": "Manage and secure network infrastructure",
                    "duration_weeks": 22,
                    "steps": [
                        {"step": 1, "title": "Networking Fundamentals", "description": "Master network protocols and concepts", "duration_weeks": 4, "skills": "TCP/IP,OSI Model,Subnetting,DNS", "resources": "https://www.youtube.com/results?search_query=networking+fundamentals"},
                        {"step": 2, "title": "Routers & Switches", "description": "Configure network devices", "duration_weeks": 4, "skills": "Cisco,Routing,Switching,VLANs", "resources": "https://www.youtube.com/results?search_query=cisco+routing+switching"},
                        {"step": 3, "title": "Security", "description": "Secure network infrastructure", "duration_weeks": 4, "skills": "Firewalls,VPN,Network Monitoring,Wireshark", "resources": "https://www.youtube.com/results?search_query=network+security+firewall"},
                        {"step": 4, "title": "Cloud & Advanced", "description": "Modern network management", "duration_weeks": 5, "skills": "Cloud Networking,Load Balancing,CompTIA Network+", "resources": "https://www.youtube.com/results?search_query=cloud+networking"},
                    ]
                },
                "Cloud Engineering": {
                    "title": "Cloud Engineering Career Path",
                    "description": "Build and manage cloud infrastructure",
                    "duration_weeks": 24,
                    "steps": [
                        {"step": 1, "title": "Cloud Fundamentals", "description": "Learn cloud computing concepts", "duration_weeks": 3, "skills": "AWS,Azure,GCP,Cloud Concepts", "resources": "https://www.youtube.com/results?search_query=cloud+computing+basics"},
                        {"step": 2, "title": "Containers & Orchestration", "description": "Master containerization", "duration_weeks": 4, "skills": "Docker,Kubernetes,Container Registry", "resources": "https://www.youtube.com/results?search_query=docker+kubernetes+tutorial"},
                        {"step": 3, "title": "Infrastructure as Code", "description": "Automate infrastructure", "duration_weeks": 4, "skills": "Terraform,Ansible,CloudFormation", "resources": "https://www.youtube.com/results?search_query=terraform+iac"},
                        {"step": 4, "title": "Monitoring & Security", "description": "Secure and monitor cloud", "duration_weeks": 5, "skills": "Monitoring,Security,CI/CD,Cost Optimization", "resources": "https://www.youtube.com/results?search_query=cloud+monitoring+security"},
                    ]
                },
                "Data Engineering": {
                    "title": "Data Engineering Career Path",
                    "description": "Build robust data pipelines and infrastructure",
                    "duration_weeks": 24,
                    "steps": [
                        {"step": 1, "title": "Programming & SQL", "description": "Master data fundamentals", "duration_weeks": 4, "skills": "Python,SQL,Data Modeling,ETL", "resources": "https://www.youtube.com/results?search_query=data+engineering+basics"},
                        {"step": 2, "title": "Big Data Technologies", "description": "Learn distributed processing", "duration_weeks": 5, "skills": "Apache Spark,Hadoop,Data Lake", "resources": "https://www.youtube.com/results?search_query=apache+spark+big+data"},
                        {"step": 3, "title": "Pipeline Orchestration", "description": "Build automated pipelines", "duration_weeks": 4, "skills": "Airflow,Kafka,Delta Lake", "resources": "https://www.youtube.com/results?search_query=apache+airflow+tutorial"},
                        {"step": 4, "title": "Cloud & Warehousing", "description": "Deploy to cloud data platforms", "duration_weeks": 5, "skills": "Snowflake,Redshift,dbt,Data Quality", "resources": "https://www.youtube.com/results?search_query=snowflake+data+warehouse"},
                    ]
                },
                "Machine Learning": {
                    "title": "Machine Learning Career Path",
                    "description": "Develop and deploy intelligent systems",
                    "duration_weeks": 26,
                    "steps": [
                        {"step": 1, "title": "ML Foundations", "description": "Learn core ML concepts", "duration_weeks": 4, "skills": "Python,Statistics,Linear Algebra,ML Algorithms", "resources": "https://www.youtube.com/results?search_query=machine+learning+fundamentals"},
                        {"step": 2, "title": "Deep Learning", "description": "Master neural networks", "duration_weeks": 5, "skills": "TensorFlow,PyTorch,Neural Networks,CNN", "resources": "https://www.youtube.com/results?search_query=deep+learning+tutorial"},
                        {"step": 3, "title": "Specializations", "description": "Specialize in NLP or CV", "duration_weeks": 5, "skills": "NLP,Computer Vision,Transformers,Feature Engineering", "resources": "https://www.youtube.com/results?search_query=nlp+computer+vision"},
                        {"step": 4, "title": "MLOps & Deployment", "description": "Deploy models to production", "duration_weeks": 5, "skills": "MLOps,MLflow,Docker,AWS SageMaker", "resources": "https://www.youtube.com/results?search_query=mlops+deployment"},
                    ]
                },
                "Cloud Architecture": {
                    "title": "Cloud Architecture Career Path",
                    "description": "Design scalable, resilient cloud solutions",
                    "duration_weeks": 26,
                    "steps": [
                        {"step": 1, "title": "Architecture Fundamentals", "description": "Learn system design principles", "duration_weeks": 4, "skills": "System Design,Networking,Security,Architecture Patterns", "resources": "https://www.youtube.com/results?search_query=cloud+architecture+fundamentals"},
                        {"step": 2, "title": "Multi-Cloud Mastery", "description": "Master AWS, Azure, and GCP", "duration_weeks": 5, "skills": "AWS,Azure,GCP,Multi-Cloud", "resources": "https://www.youtube.com/results?search_query=multi+cloud+architecture"},
                        {"step": 3, "title": "Advanced Patterns", "description": "Implement advanced architectures", "duration_weeks": 5, "skills": "Microservices,Serverless,Containers,CDN", "resources": "https://www.youtube.com/results?search_query=microservices+serverless+architecture"},
                        {"step": 4, "title": "Governance & Optimization", "description": "Optimize cost and compliance", "duration_weeks": 5, "skills": "Cost Optimization,Compliance,Disaster Recovery,Load Balancing", "resources": "https://www.youtube.com/results?search_query=cloud+cost+optimization"},
                    ]
                },
                "Web Development": {
                    "title": "Web Development Career Path",
                    "description": "Build modern, responsive web applications",
                    "duration_weeks": 22,
                    "steps": [
                        {"step": 1, "title": "Web Fundamentals", "description": "Master HTML, CSS, and JavaScript", "duration_weeks": 3, "skills": "HTML,CSS,JavaScript,Responsive Design", "resources": "https://www.youtube.com/results?search_query=web+development+basics"},
                        {"step": 2, "title": "Frontend Frameworks", "description": "Learn React and modern tools", "duration_weeks": 4, "skills": "React,TypeScript,Next.js,State Management", "resources": "https://www.youtube.com/results?search_query=react+web+development"},
                        {"step": 3, "title": "Backend & Databases", "description": "Add server-side capabilities", "duration_weeks": 4, "skills": "Node.js,PostgreSQL,MongoDB,REST APIs", "resources": "https://www.youtube.com/results?search_query=nodejs+backend+tutorial"},
                        {"step": 4, "title": "Deployment & Testing", "description": "Ship production applications", "duration_weeks": 3, "skills": "Docker,CI/CD,Testing,Performance", "resources": "https://www.youtube.com/results?search_query=web+app+deployment"},
                    ]
                },
                "UI/UX Design": {
                    "title": "UI/UX Design Career Path",
                    "description": "Create intuitive, beautiful user experiences",
                    "duration_weeks": 20,
                    "steps": [
                        {"step": 1, "title": "Design Fundamentals", "description": "Learn core design principles", "duration_weeks": 3, "skills": "Color Theory,Typography,Layout,Design Principles", "resources": "https://www.youtube.com/results?search_query=ui+ux+design+fundamentals"},
                        {"step": 2, "title": "UX Research", "description": "Understand your users", "duration_weeks": 3, "skills": "User Research,User Personas,Journey Mapping,Usability Testing", "resources": "https://www.youtube.com/results?search_query=ux+research+methods"},
                        {"step": 3, "title": "Prototyping Tools", "description": "Master design tools", "duration_weeks": 4, "skills": "Figma,Adobe XD,Prototyping,Wireframing", "resources": "https://www.youtube.com/results?search_query=figma+tutorial"},
                        {"step": 4, "title": "Design Systems", "description": "Build scalable design systems", "duration_weeks": 4, "skills": "Design Systems,Component Libraries,Accessibility,Interaction Design", "resources": "https://www.youtube.com/results?search_query=design+systems"},
                    ]
                },
                "Android Development": {
                    "title": "Android Development Career Path",
                    "description": "Build native Android applications",
                    "duration_weeks": 22,
                    "steps": [
                        {"step": 1, "title": "Kotlin Basics", "description": "Learn the Android language", "duration_weeks": 3, "skills": "Kotlin,OOP,Data Types,Functions", "resources": "https://www.youtube.com/results?search_query=kotlin+android+tutorial"},
                        {"step": 2, "title": "Android UI", "description": "Build beautiful interfaces", "duration_weeks": 4, "skills": "Android Studio,Jetpack Compose,Material Design,XML", "resources": "https://www.youtube.com/results?search_query=jetpack+compose+tutorial"},
                        {"step": 3, "title": "Architecture & Data", "description": "Build robust apps", "duration_weeks": 5, "skills": "MVVM,Room DB,Retrofit,Coroutines", "resources": "https://www.youtube.com/results?search_query=android+architecture+mvvm"},
                        {"step": 4, "title": "Publishing & Polish", "description": "Ship to Play Store", "duration_weeks": 3, "skills": "Play Store,Testing,Push Notifications,Firebase", "resources": "https://www.youtube.com/results?search_query=google+play+store+publishing"},
                    ]
                },
                "iOS Development": {
                    "title": "iOS Development Career Path",
                    "description": "Build apps for the Apple ecosystem",
                    "duration_weeks": 22,
                    "steps": [
                        {"step": 1, "title": "Swift Fundamentals", "description": "Learn iOS development language", "duration_weeks": 3, "skills": "Swift,Optionals,Protocols,Generics", "resources": "https://www.youtube.com/results?search_query=swift+ios+tutorial"},
                        {"step": 2, "title": "SwiftUI & UIKit", "description": "Build iOS interfaces", "duration_weeks": 4, "skills": "SwiftUI,UIKit,AutoLayout,Navigation", "resources": "https://www.youtube.com/results?search_query=swiftui+tutorial"},
                        {"step": 3, "title": "Data & Networking", "description": "Connect to services", "duration_weeks": 4, "skills": "CoreData,URLSession,JSON Parsing,Combine", "resources": "https://www.youtube.com/results?search_query=ios+networking+coredata"},
                        {"step": 4, "title": "App Store & Polish", "description": "Ship to the App Store", "duration_weeks": 3, "skills": "App Store,Performance,Testing,ARKit", "resources": "https://www.youtube.com/results?search_query=ios+app+store+publishing"},
                    ]
                },
                "Quality Assurance": {
                    "title": "Quality Assurance Career Path",
                    "description": "Ensure software quality through testing",
                    "duration_weeks": 20,
                    "steps": [
                        {"step": 1, "title": "Testing Fundamentals", "description": "Learn testing concepts", "duration_weeks": 3, "skills": "Test Cases,Bug Tracking,Agile,Test Plans", "resources": "https://www.youtube.com/results?search_query=software+testing+basics"},
                        {"step": 2, "title": "Manual Testing", "description": "Master manual QA techniques", "duration_weeks": 3, "skills": "Regression Testing,Exploratory Testing,Documentation", "resources": "https://www.youtube.com/results?search_query=manual+testing+tutorial"},
                        {"step": 3, "title": "Test Automation", "description": "Automate test suites", "duration_weeks": 5, "skills": "Selenium,Cypress,Jest,API Testing", "resources": "https://www.youtube.com/results?search_query=selenium+test+automation"},
                        {"step": 4, "title": "Advanced Testing", "description": "Performance and security testing", "duration_weeks": 4, "skills": "Performance Testing,Security Testing,CI/CD,Postman", "resources": "https://www.youtube.com/results?search_query=performance+testing+jmeter"},
                    ]
                },
            }
            for title, desc, category in default_roles:
                cursor.execute(
                    "INSERT INTO job_roles (title, description, category) VALUES (?, ?, ?)",
                    (title, desc, category)
                )
                role_id = cursor.lastrowid
                # Add default skills for each role
                skills_for_role = default_role_skills.get(title, {})
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
                roadmap = default_roadmaps.get(title)
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
