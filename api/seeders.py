import json
import logging

from api.database import get_db_connection

logger = logging.getLogger("resume-analyzer")


from api.seed_content import ROLE_ALIASES, action_templates, resource_map, skill_clusters, role_configs


def seed_skills_taxonomy():
    """Seed the skills taxonomy tables with default data."""
    from api.skills_taxonomy import SKILLS_TAXONOMY
    from api.skill_matching import ROLE_SYNONYMS, _SKILL_ALIASES

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Seed skill categories and skills
        cursor.execute("SELECT COUNT(*) AS cnt FROM skill_categories")
        if cursor.fetchone()["cnt"] == 0:
            for idx, (category, skills) in enumerate(SKILLS_TAXONOMY.items()):
                cursor.execute(
                    "INSERT INTO skill_categories (name, sort_order) VALUES (%s, %s) RETURNING id",
                    (category, idx)
                )
                cat_id = cursor.fetchone()["id"]
                for skill_idx, skill in enumerate(skills):
                    cursor.execute(
                        "INSERT INTO skills (category_id, name, sort_order) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                        (cat_id, skill.lower(), skill_idx)
                    )

        # Seed role synonyms
        cursor.execute("SELECT COUNT(*) AS cnt FROM role_synonyms")
        if cursor.fetchone()["cnt"] == 0:
            for role_key, categories in ROLE_SYNONYMS.items():
                cursor.execute(
                    "INSERT INTO role_synonyms (role_key, categories) VALUES (%s, %s)",
                    (role_key.lower(), ",".join(categories))
                )

        # Seed skill aliases
        cursor.execute("SELECT COUNT(*) AS cnt FROM skill_aliases")
        if cursor.fetchone()["cnt"] == 0:
            for alias, canonical in _SKILL_ALIASES.items():
                cursor.execute(
                    "INSERT INTO skill_aliases (alias, canonical_skill) VALUES (%s, %s) ON CONFLICT DO NOTHING",
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

def seed_market_data():
    """Seed field keywords, industry trends, and role aliases."""
    import json
    from api.courses import FIELD_KEYWORDS
    from api.trends import INDUSTRY_TRENDS

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Seed field keywords
        cursor.execute("SELECT COUNT(*) AS cnt FROM field_keywords")
        if cursor.fetchone()["cnt"] == 0:
            for field_name, keywords in FIELD_KEYWORDS.items():
                for keyword, weight in keywords.items():
                    cursor.execute(
                        "INSERT INTO field_keywords (field_name, keyword, weight) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                        (field_name, keyword.lower(), weight)
                    )

        # Seed industry trends
        cursor.execute("SELECT COUNT(*) AS cnt FROM industry_trends")
        if cursor.fetchone()["cnt"] == 0:
            for field_name, trends in INDUSTRY_TRENDS.items():
                for trend_type, data in trends.items():
                    cursor.execute(
                        "INSERT INTO industry_trends (field_name, trend_type, data) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                        (field_name, trend_type, json.dumps(data))
                    )

        # Seed market role aliases
        cursor.execute("SELECT COUNT(*) AS cnt FROM market_role_aliases")
        if cursor.fetchone()["cnt"] == 0:
            for alias, target in ROLE_ALIASES.items():
                cursor.execute(
                    "INSERT INTO market_role_aliases (alias, target_field) VALUES (%s, %s) ON CONFLICT DO NOTHING",
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

def seed_skill_recommendations():
    """Seed skill recommendations table with default data."""
    from api.courses import SKILL_RECOMMENDATIONS

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) AS cnt FROM skill_recommendations")
        if cursor.fetchone()["cnt"] == 0:
            for field_name, skills in SKILL_RECOMMENDATIONS.items():
                for idx, skill in enumerate(skills):
                    cursor.execute(
                        "INSERT INTO skill_recommendations (field_name, skill_name, sort_order) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
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

def seed_roadmap_templates():
    """Seed roadmap_templates table with default data."""
    from api.courses import ROADMAPS

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) AS cnt FROM roadmap_templates")
        if cursor.fetchone()["cnt"] == 0:
            for field_name, steps in ROADMAPS.items():
                for step in steps:
                    cursor.execute(
                        "INSERT INTO roadmap_templates (field_name, step_number, title, duration, skills) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
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

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) AS cnt FROM learning_actions")
        if cursor.fetchone()["cnt"] == 0:
            for skill_name, actions in action_templates.items():
                difficulty = _SKILL_DIFFICULTY.get(skill_name, 2)
                for idx, action_text in enumerate(actions):
                    cursor.execute(
                        "INSERT INTO learning_actions (skill_name, difficulty, action_text, sort_order) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
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
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) AS cnt FROM learning_resources")
        if cursor.fetchone()["cnt"] == 0:
            for skill_name, resources in resource_map.items():
                for res in resources:
                    cursor.execute(
                        "INSERT INTO learning_resources (skill_name, title, url, resource_type) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
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

        cursor.execute("SELECT COUNT(*) AS cnt FROM skill_difficulty")
        if cursor.fetchone()["cnt"] == 0:
            for skill_name, difficulty in _SKILL_DIFFICULTY.items():
                cursor.execute(
                    "INSERT INTO skill_difficulty (skill_name, difficulty_level) VALUES (%s, %s) ON CONFLICT DO NOTHING",
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
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) AS cnt FROM skill_clusters")
        if cursor.fetchone()["cnt"] == 0:
            for cluster_name, skills in skill_clusters.items():
                for skill_name in skills:
                    cursor.execute(
                        "INSERT INTO skill_clusters (cluster_name, skill_name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
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

def seed_video_resources():
    """Seed video_resources table with default data."""
    from api.courses import RESUME_VIDEOS, INTERVIEW_VIDEOS, SKILL_TUTORIAL_VIDEOS

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) AS cnt FROM video_resources")
        if cursor.fetchone()["cnt"] == 0:
            # Resume videos
            for field_name, urls in RESUME_VIDEOS.items():
                for idx, url in enumerate(urls):
                    cursor.execute(
                        "INSERT INTO video_resources (field_name, video_type, url, sort_order) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
                        (field_name, "resume", url, idx)
                    )

            # Interview videos
            for field_name, urls in INTERVIEW_VIDEOS.items():
                for idx, url in enumerate(urls):
                    cursor.execute(
                        "INSERT INTO video_resources (field_name, video_type, url, sort_order) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
                        (field_name, "interview", url, idx)
                    )

            # Skill tutorial videos
            for skill_name, url in SKILL_TUTORIAL_VIDEOS.items():
                cursor.execute(
                    "INSERT INTO video_resources (field_name, video_type, url, sort_order) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
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
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) AS cnt FROM role_configs")
        if cursor.fetchone()["cnt"] == 0:
            for role_key, config in role_configs.items():
                cursor.execute(
                    "INSERT INTO role_configs (role_key, project_types, interview_focus, portfolio_emphasis, key_tools) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
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

def seed_courses():
    """Auto-seed courses from COURSE_MAP if the courses table is empty."""
    from api.courses import COURSE_MAP

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS cnt FROM courses")
        if cursor.fetchone()["cnt"] > 0:
            return

        for field, courses in COURSE_MAP.items():
            for course in courses:
                name = course[0] if isinstance(course, (list, tuple)) else course.get('name', '')
                url = course[1] if isinstance(course, (list, tuple)) else course.get('url', '')
                if name and url:
                    cursor.execute(
                        "INSERT INTO courses (field, course_name, course_url) VALUES (%s, %s, %s)",
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
