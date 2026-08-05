"""Seed data and in-memory cache management for reference tables.

Moved out of api/database.py so that database.py owns only connections
and schema. Seed functions write reference data (skills, market data,
roadmaps, courses); load_* functions build in-memory caches; get_* and
invalidate_all_caches expose those caches to the rest of the app.
"""
import json
import logging

from api.database import get_db_connection

logger = logging.getLogger("resume-analyzer")

def seed_skills_taxonomy():
    """Seed the skills taxonomy tables with default data."""
    from api.skills_taxonomy import SKILLS_TAXONOMY
    from api.skill_matching import ROLE_SYNONYMS, _SKILL_ALIASES

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Seed skill categories and skills
        cursor.execute("SELECT COUNT(*) FROM skill_categories")
        if cursor.fetchone()[0] == 0:
            for idx, (category, skills) in enumerate(SKILLS_TAXONOMY.items()):
                cursor.execute(
                    "INSERT INTO skill_categories (name, sort_order) VALUES (?, ?)",
                    (category, idx)
                )
                cat_id = cursor.lastrowid
                for skill_idx, skill in enumerate(skills):
                    cursor.execute(
                        "INSERT OR IGNORE INTO skills (category_id, name, sort_order) VALUES (?, ?, ?)",
                        (cat_id, skill.lower(), skill_idx)
                    )

        # Seed role synonyms
        cursor.execute("SELECT COUNT(*) FROM role_synonyms")
        if cursor.fetchone()[0] == 0:
            for role_key, categories in ROLE_SYNONYMS.items():
                cursor.execute(
                    "INSERT INTO role_synonyms (role_key, categories) VALUES (?, ?)",
                    (role_key.lower(), ",".join(categories))
                )

        # Seed skill aliases
        cursor.execute("SELECT COUNT(*) FROM skill_aliases")
        if cursor.fetchone()[0] == 0:
            for alias, canonical in _SKILL_ALIASES.items():
                cursor.execute(
                    "INSERT OR IGNORE INTO skill_aliases (alias, canonical_skill) VALUES (?, ?)",
                    (alias.lower(), canonical.lower())
                )

        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


# In-memory cache for skills taxonomy data
_SKILLS_CACHE = {
    "taxonomy": {},      # {category_name: [skill_names]}
    "all_skills": [],    # flat list of all skills
    "role_synonyms": {}, # {role_key: [category_names]}
    "skill_aliases": {}, # {alias: canonical_skill}
    "loaded": False,
}


def load_skills_cache():
    """Load skills taxonomy data from database into memory cache."""
    global _SKILLS_CACHE

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Load taxonomy
        cursor.execute("SELECT id, name FROM skill_categories ORDER BY sort_order")
        categories = cursor.fetchall()
        taxonomy = {}
        all_skills = []

        for cat in categories:
            cursor.execute(
                "SELECT name FROM skills WHERE category_id = ? ORDER BY sort_order",
                (cat["id"],)
            )
            skills = [row["name"] for row in cursor.fetchall()]
            taxonomy[cat["name"]] = skills
            all_skills.extend(skills)

        # Load role synonyms
        cursor.execute("SELECT role_key, categories FROM role_synonyms")
        role_synonyms = {}
        for row in cursor.fetchall():
            role_synonyms[row["role_key"]] = row["categories"].split(",")

        # Load skill aliases
        cursor.execute("SELECT alias, canonical_skill FROM skill_aliases")
        skill_aliases = {}
        for row in cursor.fetchall():
            skill_aliases[row["alias"]] = row["canonical_skill"]

        _SKILLS_CACHE = {
            "taxonomy": taxonomy,
            "all_skills": all_skills,
            "role_synonyms": role_synonyms,
            "skill_aliases": skill_aliases,
            "loaded": True,
        }
    except Exception as e:
        logger.error(f"Failed to load skills cache: {e}")
        _SKILLS_CACHE["loaded"] = False
    finally:
        if conn:
            conn.close()


def get_skills_taxonomy():
    """Get skills taxonomy from cache."""
    if not _SKILLS_CACHE["loaded"]:
        load_skills_cache()
    return _SKILLS_CACHE["taxonomy"]


def get_all_skills():
    """Get flat list of all skills from cache."""
    if not _SKILLS_CACHE["loaded"]:
        load_skills_cache()
    return _SKILLS_CACHE["all_skills"]


def get_role_synonyms():
    """Get role synonyms from cache."""
    if not _SKILLS_CACHE["loaded"]:
        load_skills_cache()
    return _SKILLS_CACHE["role_synonyms"]


def get_skill_aliases():
    """Get skill aliases from cache."""
    if not _SKILLS_CACHE["loaded"]:
        load_skills_cache()
    return _SKILLS_CACHE["skill_aliases"]


# In-memory cache for market data
_MARKET_CACHE = {
    "field_keywords": {},  # {field_name: {keyword: weight}}
    "industry_trends": {}, # {field_name: {trend_type: data}}
    "role_aliases": {},    # {alias: target_field}
    "loaded": False,
}


def seed_market_data():
    """Seed field keywords, industry trends, and role aliases."""
    import json
    from api.courses import FIELD_KEYWORDS
    from api.trends import INDUSTRY_TRENDS

    # Inline ROLE_ALIASES (was removed from market_data.py)
    ROLE_ALIASES = {
        "ios development": "IOS Development",
        "ui ux development": "UI-UX Development",
        "ui/ux development": "UI-UX Development",
        "ui/ux design": "UI-UX Development",
        "web developer": "Web Development",
        "web development": "Web Development",
        "data scientist": "Data Science",
        "data science": "Data Science",
        "data engineer": "Data Engineering",
        "data engineering": "Data Engineering",
        "machine learning engineer": "Machine Learning",
        "machine learning": "Machine Learning",
        "ml engineer": "Machine Learning",
        "cloud engineer": "Cloud Engineering",
        "cloud engineering": "Cloud Engineering",
        "cloud architect": "Cloud Architecture",
        "cloud architecture": "Cloud Architecture",
        "product manager": "Product Management",
        "product management": "Product Management",
        "business analyst": "Business Analysis",
        "business analysis": "Business Analysis",
        "technical writer": "Technical Writing",
        "technical writing": "Technical Writing",
        "it support specialist": "IT Support",
        "it support": "IT Support",
        "network administrator": "Network Administration",
        "network admin": "Network Administration",
        "devops engineer": "DevOps",
        "devops": "DevOps",
        "android developer": "Android Development",
        "android development": "Android Development",
        "ios developer": "IOS Development",
        "qa engineer": "Quality Assurance",
        "quality assurance": "Quality Assurance",
        "software engineer": "Software Engineering",
        "software engineering": "Software Engineering",
        "frontend developer": "Frontend Development",
        "frontend development": "Frontend Development",
        "backend developer": "Backend Development",
        "backend development": "Backend Development",
        "full stack developer": "Full Stack Development",
        "full stack development": "Full Stack Development",
        "cyber security": "Cybersecurity",
        "cybersecurity": "Cybersecurity",
        "information security": "Cybersecurity",
        "mobile developer": "Mobile Development",
        "mobile development": "Mobile Development",
    }

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Seed field keywords
        cursor.execute("SELECT COUNT(*) FROM field_keywords")
        if cursor.fetchone()[0] == 0:
            for field_name, keywords in FIELD_KEYWORDS.items():
                for keyword, weight in keywords.items():
                    cursor.execute(
                        "INSERT OR IGNORE INTO field_keywords (field_name, keyword, weight) VALUES (?, ?, ?)",
                        (field_name, keyword.lower(), weight)
                    )

        # Seed industry trends
        cursor.execute("SELECT COUNT(*) FROM industry_trends")
        if cursor.fetchone()[0] == 0:
            for field_name, trends in INDUSTRY_TRENDS.items():
                for trend_type, data in trends.items():
                    cursor.execute(
                        "INSERT OR IGNORE INTO industry_trends (field_name, trend_type, data) VALUES (?, ?, ?)",
                        (field_name, trend_type, json.dumps(data))
                    )

        # Seed market role aliases
        cursor.execute("SELECT COUNT(*) FROM market_role_aliases")
        if cursor.fetchone()[0] == 0:
            for alias, target in ROLE_ALIASES.items():
                cursor.execute(
                    "INSERT OR IGNORE INTO market_role_aliases (alias, target_field) VALUES (?, ?)",
                    (alias.lower(), target)
                )

        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def load_market_cache():
    """Load market data from database into memory cache."""
    global _MARKET_CACHE
    import json

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Load field keywords
        cursor.execute("SELECT field_name, keyword, weight FROM field_keywords")
        field_keywords = {}
        for row in cursor.fetchall():
            if row["field_name"] not in field_keywords:
                field_keywords[row["field_name"]] = {}
            field_keywords[row["field_name"]][row["keyword"]] = row["weight"]

        # Load industry trends
        cursor.execute("SELECT field_name, trend_type, data FROM industry_trends")
        industry_trends = {}
        for row in cursor.fetchall():
            if row["field_name"] not in industry_trends:
                industry_trends[row["field_name"]] = {}
            industry_trends[row["field_name"]][row["trend_type"]] = json.loads(row["data"])

        # Load market role aliases
        cursor.execute("SELECT alias, target_field FROM market_role_aliases")
        role_aliases = {}
        for row in cursor.fetchall():
            role_aliases[row["alias"]] = row["target_field"]

        _MARKET_CACHE = {
            "field_keywords": field_keywords,
            "industry_trends": industry_trends,
            "role_aliases": role_aliases,
            "loaded": True,
        }
    except Exception as e:
        logger.error(f"Failed to load market cache: {e}")
        _MARKET_CACHE["loaded"] = False
    finally:
        if conn:
            conn.close()


def get_field_keywords():
    """Get field keywords from cache."""
    if not _MARKET_CACHE["loaded"]:
        load_market_cache()
    return _MARKET_CACHE["field_keywords"]


def get_industry_trends():
    """Get industry trends from cache."""
    if not _MARKET_CACHE["loaded"]:
        load_market_cache()
    return _MARKET_CACHE["industry_trends"]


def get_market_role_aliases():
    """Get market role aliases from cache."""
    if not _MARKET_CACHE["loaded"]:
        load_market_cache()
    return _MARKET_CACHE["role_aliases"]


# In-memory cache for skill recommendations
_SKILL_RECS_CACHE = {
    "recommendations": {},  # {field_name: [skill_names]}
    "loaded": False,
}


def seed_skill_recommendations():
    """Seed skill recommendations table with default data."""
    from api.courses import SKILL_RECOMMENDATIONS

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM skill_recommendations")
        if cursor.fetchone()[0] == 0:
            for field_name, skills in SKILL_RECOMMENDATIONS.items():
                for idx, skill in enumerate(skills):
                    cursor.execute(
                        "INSERT OR IGNORE INTO skill_recommendations (field_name, skill_name, sort_order) VALUES (?, ?, ?)",
                        (field_name, skill, idx)
                    )

        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def load_skill_recs_cache():
    """Load skill recommendations from database into memory cache."""
    global _SKILL_RECS_CACHE

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT field_name, skill_name FROM skill_recommendations ORDER BY field_name, sort_order")
        recommendations = {}
        for row in cursor.fetchall():
            if row["field_name"] not in recommendations:
                recommendations[row["field_name"]] = []
            recommendations[row["field_name"]].append(row["skill_name"])

        _SKILL_RECS_CACHE = {
            "recommendations": recommendations,
            "loaded": True,
        }
    except Exception as e:
        logger.error(f"Failed to load skill recommendations cache: {e}")
        _SKILL_RECS_CACHE["loaded"] = False
    finally:
        if conn:
            conn.close()


def get_skill_recommendations():
    """Get skill recommendations from cache."""
    if not _SKILL_RECS_CACHE["loaded"]:
        load_skill_recs_cache()
    return _SKILL_RECS_CACHE["recommendations"]


# ============================================================
# Sprint 4: Roadmaps, Actions, Resources, Difficulty, Clusters
# ============================================================

def seed_roadmap_templates():
    """Seed roadmap_templates table with default data."""
    from api.courses import ROADMAPS

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM roadmap_templates")
        if cursor.fetchone()[0] == 0:
            for field_name, steps in ROADMAPS.items():
                for step in steps:
                    cursor.execute(
                        "INSERT OR IGNORE INTO roadmap_templates (field_name, step_number, title, duration, skills) VALUES (?, ?, ?, ?, ?)",
                        (field_name, step["step"], step["title"], step["duration"], json.dumps(step["skills"]))
                    )

        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def seed_learning_actions():
    """Seed learning_actions table with default data."""
    from api.skill_matching import _SKILL_DIFFICULTY
    # action_templates from skill_matching.py
    action_templates = {
        "react": [
            "Learn React fundamentals: components, props, state, and hooks",
            "Build a CRUD app with React (e.g., todo list, weather app)",
            "Practice React patterns: context, custom hooks, performance optimization",
        ],
        "typescript": [
            "Learn TypeScript basics: types, interfaces, generics",
            "Convert an existing JavaScript project to TypeScript",
            "Practice advanced types: unions, generics, utility types",
        ],
        "next.js": [
            "Learn Next.js basics: pages, routing, API routes",
            "Build a full-stack app with Next.js and a database",
            "Practice SSR/SSG and optimization techniques",
        ],
        "vue": [
            "Learn Vue fundamentals: components, reactivity, directives",
            "Build a single-page app with Vue Router and Pinia",
            "Practice Vue 3 Composition API patterns",
        ],
        "angular": [
            "Learn Angular fundamentals: components, services, modules",
            "Build a full Angular app with routing and HTTP client",
            "Practice RxJS and state management patterns",
        ],
        "python": [
            "Complete Python basics: data types, control flow, functions",
            "Build a Python project with classes and modules",
            "Practice Pythonic patterns: list comprehensions, decorators, context managers",
        ],
        "django": [
            "Set up Django project and create models",
            "Build views, templates, and URL routing",
            "Implement authentication and REST API endpoints",
        ],
        "flask": [
            "Create Flask app with routes and templates",
            "Add database integration with SQLAlchemy",
            "Build REST API with Flask-RESTful or Flask RESTX",
        ],
        "fastapi": [
            "Build a FastAPI app with path parameters and request bodies",
            "Add Pydantic models and validation",
            "Implement authentication, middleware, and background tasks",
        ],
        "node.js": [
            "Learn Node.js fundamentals: modules, events, file I/O",
            "Build an Express server with middleware",
            "Implement authentication and database integration",
        ],
        "express": [
            "Set up Express app with routing and middleware",
            "Build RESTful API endpoints",
            "Add authentication, validation, and error handling",
        ],
        "docker": [
            "Learn Docker basics: images, containers, volumes",
            "Create a Dockerfile for your application",
            "Use Docker Compose for multi-container apps",
        ],
        "kubernetes": [
            "Learn Kubernetes basics: pods, services, deployments",
            "Deploy an app to a Kubernetes cluster",
            "Configure scaling, health checks, and rolling updates",
        ],
        "aws": [
            "Explore AWS free tier: EC2, S3, RDS",
            "Deploy a web app on EC2 with RDS database",
            "Practice IAM, VPC, and CloudFront setup",
        ],
        "terraform": [
            "Learn Terraform basics: providers, resources, state",
            "Write Terraform for AWS infrastructure",
            "Manage state and use modules for reusability",
        ],
        "machine learning": [
            "Learn ML basics: supervised vs unsupervised learning",
            "Build a model with scikit-learn on a real dataset",
            "Practice model evaluation: cross-validation, metrics",
        ],
        "deep learning": [
            "Learn neural network fundamentals",
            "Build a deep learning model with TensorFlow or PyTorch",
            "Practice CNNs, RNNs, and transfer learning",
        ],
        "tensorflow": [
            "Complete TensorFlow 2.x tutorials",
            "Build a neural network with Keras Sequential API",
            "Practice model training, evaluation, and deployment",
        ],
        "pytorch": [
            "Learn PyTorch tensors and autograd",
            "Build a neural network with nn.Module",
            "Practice training loops and GPU acceleration",
        ],
        "pandas": [
            "Learn pandas: Series, DataFrame, indexing",
            "Practice data cleaning and transformation",
            "Build data analysis projects with real datasets",
        ],
        "sql": [
            "Learn SQL basics: SELECT, JOIN, WHERE, GROUP BY",
            "Practice complex queries with subqueries and CTEs",
            "Build a database schema and write optimization queries",
        ],
        "postgresql": [
            "Set up PostgreSQL and learn advanced SQL",
            "Practice indexing, partitioning, and query optimization",
            "Build a full app with psycopg2 or SQLAlchemy",
        ],
        "mongodb": [
            "Learn MongoDB basics: documents, collections, CRUD",
            "Practice aggregation pipelines",
            "Integrate with a backend framework",
        ],
        "react native": [
            "Set up React Native project and learn components",
            "Build a cross-platform mobile app",
            "Practice navigation, state, and native modules",
        ],
        "flutter": [
            "Learn Flutter/Dart basics: widgets, layouts, state",
            "Build a complete mobile app with navigation",
            "Practice animations, custom widgets, and platform integration",
        ],
        "swift": [
            "Learn Swift basics: types, optionals, protocols",
            "Build SwiftUI views and navigation",
            "Practice Core Data, networking, and async/await",
        ],
        "kotlin": [
            "Learn Kotlin basics: null safety, coroutines, extensions",
            "Build an Android app with Jetpack Compose",
            "Practice Retrofit, Room, and dependency injection",
        ],
    }

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM learning_actions")
        if cursor.fetchone()[0] == 0:
            for skill_name, actions in action_templates.items():
                difficulty = _SKILL_DIFFICULTY.get(skill_name, 2)
                for idx, action_text in enumerate(actions):
                    cursor.execute(
                        "INSERT OR IGNORE INTO learning_actions (skill_name, difficulty, action_text, sort_order) VALUES (?, ?, ?, ?)",
                        (skill_name, difficulty, action_text, idx)
                    )

        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def seed_learning_resources():
    """Seed learning_resources table with default data."""
    resource_map = {
        "react": [
            {"title": "React Official Tutorial", "url": "https://react.dev/learn", "type": "docs"},
            {"title": "React Crash Course (Free)", "url": "https://youtu.be/Dorf8i6lCuk", "type": "video"},
        ],
        "typescript": [
            {"title": "TypeScript Handbook", "url": "https://www.typescriptlang.org/docs/handbook/", "type": "docs"},
            {"title": "TypeScript Tutorial (Free)", "url": "https://youtu.be/BwuLxPH8IDs", "type": "video"},
        ],
        "next.js": [
            {"title": "Next.js Learn Course", "url": "https://nextjs.org/learn", "type": "docs"},
            {"title": "Next.js Crash Course", "url": "https://youtu.be/mTz0GXj8NN0", "type": "video"},
        ],
        "vue": [
            {"title": "Vue.js Official Guide", "url": "https://vuejs.org/guide/introduction.html", "type": "docs"},
            {"title": "Vue 3 Crash Course (Free)", "url": "https://youtu.be/FXpIoQ_rT_c", "type": "video"},
        ],
        "angular": [
            {"title": "Angular Official Tutorial", "url": "https://angular.dev/tutorial", "type": "docs"},
            {"title": "Angular Crash Course (Free)", "url": "https://youtu.be/3dHNOWTI7H8", "type": "video"},
        ],
        "python": [
            {"title": "Python Official Tutorial", "url": "https://docs.python.org/3/tutorial/", "type": "docs"},
            {"title": "Python for Everybody (Free)", "url": "https://www.py4e.com/", "type": "course"},
        ],
        "django": [
            {"title": "Django Official Tutorial", "url": "https://docs.djangoproject.com/en/stable/intro/tutorial01/", "type": "docs"},
            {"title": "Django Crash Course (Free)", "url": "https://youtu.be/e1IyzVyrLSU", "type": "video"},
        ],
        "flask": [
            {"title": "Flask Official Documentation", "url": "https://flask.palletsprojects.com/en/3.0.x/tutorial/", "type": "docs"},
            {"title": "Flask Crash Course (Free)", "url": "https://youtu.be/Z1RJmh_OqeA", "type": "video"},
        ],
        "fastapi": [
            {"title": "FastAPI Official Tutorial", "url": "https://fastapi.tiangolo.com/tutorial/", "type": "docs"},
            {"title": "FastAPI Course (Free)", "url": "https://youtu.be/0sOvCWFmrtA", "type": "video"},
        ],
        "node.js": [
            {"title": "Node.js Official Guides", "url": "https://nodejs.org/en/learn/getting-started/introduction-to-nodejs", "type": "docs"},
            {"title": "Node.js Crash Course", "url": "https://youtu.be/fBNz5xF-Kx4", "type": "video"},
        ],
        "express": [
            {"title": "Express.js Official Guide", "url": "https://expressjs.com/en/guide/routing.html", "type": "docs"},
            {"title": "Express Crash Course (Free)", "url": "https://youtu.be/CnH3kAXSrmU", "type": "video"},
        ],
        "docker": [
            {"title": "Docker Official Tutorial", "url": "https://docs.docker.com/get-started/", "type": "docs"},
            {"title": "Docker Crash Course (Free)", "url": "https://youtu.be/fqMOX6JJhGo", "type": "video"},
        ],
        "kubernetes": [
            {"title": "Kubernetes Basics", "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/", "type": "docs"},
            {"title": "K8s Crash Course (Free)", "url": "https://youtu.be/X48VuDVv0do", "type": "video"},
        ],
        "aws": [
            {"title": "AWS Free Tier Training", "url": "https://aws.amazon.com/free/", "type": "course"},
            {"title": "AWS Cloud Practitioner", "url": "https://aws.amazon.com/certification/certified-cloud-practitioner/", "type": "cert"},
        ],
        "terraform": [
            {"title": "Terraform Official Tutorials", "url": "https://developer.hashicorp.com/terraform/tutorials", "type": "docs"},
            {"title": "Terraform Crash Course (Free)", "url": "https://youtu.be/l5k1ai_GBDE", "type": "video"},
        ],
        "machine learning": [
            {"title": "ML Crash Course by Google", "url": "https://developers.google.com/machine-learning/crash-course", "type": "course"},
            {"title": "Machine Learning by Andrew Ng", "url": "https://www.coursera.org/learn/machine-learning", "type": "course"},
        ],
        "deep learning": [
            {"title": "Deep Learning Specialization", "url": "https://www.coursera.org/specializations/deep-learning", "type": "course"},
            {"title": "Fast.ai Practical Deep Learning", "url": "https://course.fast.ai/", "type": "course"},
        ],
        "tensorflow": [
            {"title": "TensorFlow Official Tutorials", "url": "https://www.tensorflow.org/tutorials", "type": "docs"},
            {"title": "TensorFlow Crash Course", "url": "https://www.tensorflow.org/tutorials/quickstart/beginner", "type": "docs"},
        ],
        "pytorch": [
            {"title": "PyTorch Official Tutorial", "url": "https://pytorch.org/tutorials/", "type": "docs"},
            {"title": "PyTorch for Deep Learning", "url": "https://www.youtube.com/watch?v=aircAruvnKk", "type": "video"},
        ],
        "pandas": [
            {"title": "Pandas Official Documentation", "url": "https://pandas.pydata.org/docs/getting_started/introduction.html", "type": "docs"},
            {"title": "Pandas Tutorial (Free)", "url": "https://youtu.be/vmEHCJofslg", "type": "video"},
        ],
        "sql": [
            {"title": "SQL Tutorial", "url": "https://www.w3schools.com/sql/", "type": "docs"},
            {"title": "SQL Crash Course (Free)", "url": "https://youtu.be/HXV3zeQKqGY", "type": "video"},
        ],
        "postgresql": [
            {"title": "PostgreSQL Official Documentation", "url": "https://www.postgresql.org/docs/current/tutorial.html", "type": "docs"},
            {"title": "PostgreSQL Crash Course (Free)", "url": "https://youtu.be/qw--VlpxnE4", "type": "video"},
        ],
        "mongodb": [
            {"title": "MongoDB Official Tutorial", "url": "https://www.mongodb.com/docs/manual/tutorial/getting-started/", "type": "docs"},
            {"title": "MongoDB Crash Course (Free)", "url": "https://youtu.be/-56x56UppqQ", "type": "video"},
        ],
        "react native": [
            {"title": "React Native Official Guide", "url": "https://reactnative.dev/docs/getting-started", "type": "docs"},
            {"title": "React Native Crash Course (Free)", "url": "https://youtu.be/0-S5a9eLho8", "type": "video"},
        ],
        "flutter": [
            {"title": "Flutter Official Documentation", "url": "https://docs.flutter.dev/get-started/install", "type": "docs"},
            {"title": "Flutter Crash Course (Free)", "url": "https://youtu.be/1gDIFuM9sKY", "type": "video"},
        ],
        "swift": [
            {"title": "Swift Official Documentation", "url": "https://docs.swift.org/swift-book/documentation/the-swift-programming-language/", "type": "docs"},
            {"title": "SwiftUI Tutorial", "url": "https://developer.apple.com/tutorials/swiftui", "type": "docs"},
        ],
        "kotlin": [
            {"title": "Kotlin Official Documentation", "url": "https://kotlinlang.org/docs/home.html", "type": "docs"},
            {"title": "Kotlin Crash Course (Free)", "url": "https://youtu.be/FdNLHkYEXEo", "type": "video"},
        ],
    }

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM learning_resources")
        if cursor.fetchone()[0] == 0:
            for skill_name, resources in resource_map.items():
                for res in resources:
                    cursor.execute(
                        "INSERT OR IGNORE INTO learning_resources (skill_name, title, url, resource_type) VALUES (?, ?, ?, ?)",
                        (skill_name, res["title"], res["url"], res["type"])
                    )

        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def seed_skill_difficulty():
    """Seed skill_difficulty table with default data."""
    from api.skill_matching import _SKILL_DIFFICULTY

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM skill_difficulty")
        if cursor.fetchone()[0] == 0:
            for skill_name, difficulty in _SKILL_DIFFICULTY.items():
                cursor.execute(
                    "INSERT OR IGNORE INTO skill_difficulty (skill_name, difficulty_level) VALUES (?, ?)",
                    (skill_name, difficulty)
                )

        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def seed_skill_clusters():
    """Seed skill_clusters table with default data."""
    skill_clusters = {
        "react_ecosystem": ["react", "next.js", "typescript", "tailwind", "redux", "zustand"],
        "vue_ecosystem": ["vue", "nuxt.js", "vuex", "pinia"],
        "python_backend": ["django", "flask", "fastapi", "python"],
        "java_backend": ["java", "spring boot", "hibernate"],
        "node_backend": ["node.js", "express", "mongodb", "graphql"],
        "cloud_aws": ["aws", "terraform", "docker", "kubernetes", "ci/cd"],
        "cloud_azure": ["azure", "terraform", "docker", "kubernetes", "ci/cd"],
        "data_science": ["python", "pandas", "numpy", "matplotlib", "seaborn", "statistics"],
        "ml_engineering": ["machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn"],
        "mobile_cross": ["react native", "flutter", "dart"],
        "mobile_native": ["swift", "kotlin", "swiftui", "jetpack compose"],
        "devops_tools": ["docker", "kubernetes", "jenkins", "ci/cd", "terraform", "ansible"],
        "databases": ["sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch"],
        "testing": ["testing", "unit testing", "integration testing", "selenium", "qa"],
    }

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM skill_clusters")
        if cursor.fetchone()[0] == 0:
            for cluster_name, skills in skill_clusters.items():
                for skill_name in skills:
                    cursor.execute(
                        "INSERT OR IGNORE INTO skill_clusters (cluster_name, skill_name) VALUES (?, ?)",
                        (cluster_name, skill_name)
                    )

        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


# ============================================================
# Cache loaders for Sprint 4 data
# ============================================================

_ROADMAPS_CACHE = {"data": {}, "loaded": False}
_ACTIONS_CACHE = {"data": {}, "loaded": False}
_RESOURCES_CACHE = {"data": {}, "loaded": False}
_DIFFICULTY_CACHE = {"data": {}, "loaded": False}
_CLUSTERS_CACHE = {"data": {}, "loaded": False}


def load_roadmaps_cache():
    """Load roadmap templates from database into memory cache."""
    global _ROADMAPS_CACHE

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT field_name, step_number, title, duration, skills FROM roadmap_templates ORDER BY field_name, step_number")
        roadmaps = {}
        for row in cursor.fetchall():
            if row["field_name"] not in roadmaps:
                roadmaps[row["field_name"]] = []
            roadmaps[row["field_name"]].append({
                "step": row["step_number"],
                "title": row["title"],
                "duration": row["duration"],
                "skills": json.loads(row["skills"]),
            })

        _ROADMAPS_CACHE = {"data": roadmaps, "loaded": True}
    except Exception as e:
        logger.error(f"Failed to load roadmaps cache: {e}")
        _ROADMAPS_CACHE["loaded"] = False
    finally:
        if conn:
            conn.close()


def load_actions_cache():
    """Load learning actions from database into memory cache."""
    global _ACTIONS_CACHE

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT skill_name, action_text FROM learning_actions ORDER BY skill_name, sort_order")
        actions = {}
        for row in cursor.fetchall():
            if row["skill_name"] not in actions:
                actions[row["skill_name"]] = []
            actions[row["skill_name"]].append(row["action_text"])

        _ACTIONS_CACHE = {"data": actions, "loaded": True}
    except Exception as e:
        logger.error(f"Failed to load actions cache: {e}")
        _ACTIONS_CACHE["loaded"] = False
    finally:
        if conn:
            conn.close()


def load_resources_cache():
    """Load learning resources from database into memory cache."""
    global _RESOURCES_CACHE

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT skill_name, title, url, resource_type FROM learning_resources ORDER BY skill_name")
        resources = {}
        for row in cursor.fetchall():
            if row["skill_name"] not in resources:
                resources[row["skill_name"]] = []
            resources[row["skill_name"]].append({
                "title": row["title"],
                "url": row["url"],
                "type": row["resource_type"],
            })

        _RESOURCES_CACHE = {"data": resources, "loaded": True}
    except Exception as e:
        logger.error(f"Failed to load resources cache: {e}")
        _RESOURCES_CACHE["loaded"] = False
    finally:
        if conn:
            conn.close()


def load_difficulty_cache():
    """Load skill difficulty from database into memory cache."""
    global _DIFFICULTY_CACHE

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT skill_name, difficulty_level FROM skill_difficulty")
        difficulty = {}
        for row in cursor.fetchall():
            difficulty[row["skill_name"]] = row["difficulty_level"]

        _DIFFICULTY_CACHE = {"data": difficulty, "loaded": True}
    except Exception as e:
        logger.error(f"Failed to load difficulty cache: {e}")
        _DIFFICULTY_CACHE["loaded"] = False
    finally:
        if conn:
            conn.close()


def load_clusters_cache():
    """Load skill clusters from database into memory cache."""
    global _CLUSTERS_CACHE

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT cluster_name, skill_name FROM skill_clusters")
        clusters = {}
        for row in cursor.fetchall():
            if row["cluster_name"] not in clusters:
                clusters[row["cluster_name"]] = set()
            clusters[row["cluster_name"]].add(row["skill_name"])

        _CLUSTERS_CACHE = {"data": clusters, "loaded": True}
    except Exception as e:
        logger.error(f"Failed to load clusters cache: {e}")
        _CLUSTERS_CACHE["loaded"] = False
    finally:
        if conn:
            conn.close()


def get_roadmaps():
    """Get roadmap templates from cache."""
    if not _ROADMAPS_CACHE["loaded"]:
        load_roadmaps_cache()
    return _ROADMAPS_CACHE["data"]


def get_learning_actions():
    """Get learning actions from cache."""
    if not _ACTIONS_CACHE["loaded"]:
        load_actions_cache()
    return _ACTIONS_CACHE["data"]


def get_learning_resources():
    """Get learning resources from cache."""
    if not _RESOURCES_CACHE["loaded"]:
        load_resources_cache()
    return _RESOURCES_CACHE["data"]


def get_skill_difficulty():
    """Get skill difficulty from cache."""
    if not _DIFFICULTY_CACHE["loaded"]:
        load_difficulty_cache()
    return _DIFFICULTY_CACHE["data"]


def get_skill_clusters():
    """Get skill clusters from cache."""
    if not _CLUSTERS_CACHE["loaded"]:
        load_clusters_cache()
    return _CLUSTERS_CACHE["data"]


# ============================================================
# Sprint 5: Video Resources & Role Configs
# ============================================================

def seed_video_resources():
    """Seed video_resources table with default data."""
    from api.courses import RESUME_VIDEOS, INTERVIEW_VIDEOS, SKILL_TUTORIAL_VIDEOS

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM video_resources")
        if cursor.fetchone()[0] == 0:
            # Resume videos
            for field_name, urls in RESUME_VIDEOS.items():
                for idx, url in enumerate(urls):
                    cursor.execute(
                        "INSERT OR IGNORE INTO video_resources (field_name, video_type, url, sort_order) VALUES (?, ?, ?, ?)",
                        (field_name, "resume", url, idx)
                    )

            # Interview videos
            for field_name, urls in INTERVIEW_VIDEOS.items():
                for idx, url in enumerate(urls):
                    cursor.execute(
                        "INSERT OR IGNORE INTO video_resources (field_name, video_type, url, sort_order) VALUES (?, ?, ?, ?)",
                        (field_name, "interview", url, idx)
                    )

            # Skill tutorial videos
            for skill_name, url in SKILL_TUTORIAL_VIDEOS.items():
                cursor.execute(
                    "INSERT OR IGNORE INTO video_resources (field_name, video_type, url, sort_order) VALUES (?, ?, ?, ?)",
                    (skill_name, "skill_tutorial", url, 0)
                )

        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def seed_role_configs():
    """Seed role_configs table with default data."""
    role_configs = {
        "software engineer": {
            "project_types": ["full-stack web app", "REST API with authentication", "microservices architecture"],
            "interview_focus": ["system design", "data structures", "algorithms"],
            "portfolio_emphasis": "GitHub contributions and code quality",
            "key_tools": ["Git", "CI/CD", "testing frameworks"],
        },
        "frontend": {
            "project_types": ["interactive web app", "component library", "responsive dashboard"],
            "interview_focus": ["UI/UX discussions", "performance optimization", "accessibility"],
            "portfolio_emphasis": "Live demos and design thinking",
            "key_tools": ["browser DevTools", "Lighthouse", "Figma"],
        },
        "backend": {
            "project_types": ["REST API with database", "microservice with Docker", "real-time WebSocket app"],
            "interview_focus": ["API design", "database optimization", "scalability"],
            "portfolio_emphasis": "API documentation and system architecture",
            "key_tools": ["Postman", "database tools", "monitoring"],
        },
        "data scientist": {
            "project_types": ["end-to-end ML pipeline", "data visualization dashboard", "predictive model deployment"],
            "interview_focus": ["statistics", "ML algorithms", "data cleaning"],
            "portfolio_emphasis": "Jupyter notebooks and Kaggle competitions",
            "key_tools": ["Jupyter", "pandas", "scikit-learn"],
        },
        "devops": {
            "project_types": ["CI/CD pipeline", "infrastructure as code", "monitoring dashboard"],
            "interview_focus": ["infrastructure design", "incident response", "automation"],
            "portfolio_emphasis": "automation scripts and infrastructure diagrams",
            "key_tools": ["Terraform", "Kubernetes", "monitoring tools"],
        },
        "mobile developer": {
            "project_types": ["cross-platform app", "native mobile app", "app with backend integration"],
            "interview_focus": ["mobile UX", "performance", "offline functionality"],
            "portfolio_emphasis": "App Store links and user feedback",
            "key_tools": ["mobile IDE", "emulators", "testing frameworks"],
        },
        "full stack": {
            "project_types": ["full-stack SaaS", "real-time web app", "e-commerce platform"],
            "interview_focus": ["system design", "full-stack debugging", "architecture"],
            "portfolio_emphasis": "deployed applications and end-to-end ownership",
            "key_tools": ["frontend frameworks", "backend frameworks", "databases"],
        },
        "cybersecurity": {
            "project_types": ["security audit", "vulnerability scanner", "security automation tool"],
            "interview_focus": ["threat modeling", "incident response", "compliance frameworks"],
            "portfolio_emphasis": "CTF competitions and security certifications",
            "key_tools": ["Wireshark", "Burp Suite", "SIEM tools"],
        },
    }

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM role_configs")
        if cursor.fetchone()[0] == 0:
            for role_key, config in role_configs.items():
                cursor.execute(
                    "INSERT OR IGNORE INTO role_configs (role_key, project_types, interview_focus, portfolio_emphasis, key_tools) VALUES (?, ?, ?, ?, ?)",
                    (role_key, json.dumps(config["project_types"]), json.dumps(config["interview_focus"]),
                     config["portfolio_emphasis"], json.dumps(config["key_tools"]))
                )

        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


# Cache variables for Sprint 5
_VIDEOS_CACHE = {"data": {}, "loaded": False}
_ROLE_CONFIGS_CACHE = {"data": {}, "loaded": False}


def load_videos_cache():
    """Load video resources from database into memory cache."""
    global _VIDEOS_CACHE

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT field_name, video_type, url FROM video_resources ORDER BY field_name, video_type, sort_order")
        videos = {}
        for row in cursor.fetchall():
            field = row["field_name"]
            vtype = row["video_type"]
            if field not in videos:
                videos[field] = {}
            if vtype not in videos[field]:
                videos[field][vtype] = []
            videos[field][vtype].append(row["url"])

        _VIDEOS_CACHE = {"data": videos, "loaded": True}
    except Exception as e:
        logger.error(f"Failed to load videos cache: {e}")
        _VIDEOS_CACHE["loaded"] = False
    finally:
        if conn:
            conn.close()


def load_role_configs_cache():
    """Load role configs from database into memory cache."""
    global _ROLE_CONFIGS_CACHE

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT role_key, project_types, interview_focus, portfolio_emphasis, key_tools FROM role_configs")
        configs = {}
        for row in cursor.fetchall():
            configs[row["role_key"]] = {
                "project_types": json.loads(row["project_types"]),
                "interview_focus": json.loads(row["interview_focus"]),
                "portfolio_emphasis": row["portfolio_emphasis"],
                "key_tools": json.loads(row["key_tools"]),
            }

        _ROLE_CONFIGS_CACHE = {"data": configs, "loaded": True}
    except Exception as e:
        logger.error(f"Failed to load role configs cache: {e}")
        _ROLE_CONFIGS_CACHE["loaded"] = False
    finally:
        if conn:
            conn.close()


def get_resume_videos():
    """Get resume videos from cache."""
    if not _VIDEOS_CACHE["loaded"]:
        load_videos_cache()
    return {k: v.get("resume", []) for k, v in _VIDEOS_CACHE["data"].items()}


def get_interview_videos():
    """Get interview videos from cache."""
    if not _VIDEOS_CACHE["loaded"]:
        load_videos_cache()
    return {k: v.get("interview", []) for k, v in _VIDEOS_CACHE["data"].items()}


def get_skill_tutorial_videos():
    """Get skill tutorial videos from cache."""
    if not _VIDEOS_CACHE["loaded"]:
        load_videos_cache()
    return {k: v.get("skill_tutorial", []) for k, v in _VIDEOS_CACHE["data"].items()}


def get_role_configs():
    """Get role configs from cache."""
    if not _ROLE_CONFIGS_CACHE["loaded"]:
        load_role_configs_cache()
    return _ROLE_CONFIGS_CACHE["data"]


def get_role_config(role: str) -> dict:
    """Get a specific role's config, with fallback to default."""
    configs = get_role_configs()
    role_lower = role.lower()

    for key, config in configs.items():
        if key in role_lower:
            return config

    # Default config
    return {
        "project_types": ["personal project", "open-source contribution", "technical blog"],
        "interview_focus": ["technical fundamentals", "problem solving", "communication"],
        "portfolio_emphasis": "demonstrated learning and growth",
        "key_tools": ["version control", "documentation", "testing"],
    }


# ============================================================
# Cache invalidation functions
# ============================================================

_CACHES = [
    _SKILLS_CACHE, _MARKET_CACHE, _SKILL_RECS_CACHE, _ROADMAPS_CACHE,
    _ACTIONS_CACHE, _RESOURCES_CACHE, _DIFFICULTY_CACHE, _CLUSTERS_CACHE,
    _VIDEOS_CACHE, _ROLE_CONFIGS_CACHE,
]


def invalidate_all_caches():
    """Invalidate all in-memory caches. Call after admin mutations."""
    for cache in _CACHES:
        cache["loaded"] = False


def seed_courses():
    """Auto-seed courses from COURSE_MAP if the courses table is empty."""
    from api.courses import COURSE_MAP

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM courses")
        if cursor.fetchone()[0] > 0:
            return

        for field, courses in COURSE_MAP.items():
            for course in courses:
                name = course[0] if isinstance(course, (list, tuple)) else course.get('name', '')
                url = course[1] if isinstance(course, (list, tuple)) else course.get('url', '')
                if name and url:
                    cursor.execute(
                        "INSERT INTO courses (field, course_name, course_url) VALUES (?, ?, ?)",
                        (field, name, url)
                    )

        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
