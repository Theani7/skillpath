"""In-memory cache management for reference tables.

Moved out of api/database.py so that database.py owns only connections
and schema. Seed functions live in api/seeders.py; load_* functions here
build in-memory caches from the database; get_* and invalidate_all_caches
expose those caches to the rest of the app.
"""
import json
import logging

from api.database import get_db_connection

logger = logging.getLogger("resume-analyzer")



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


