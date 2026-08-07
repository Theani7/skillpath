"""Role-to-skill mapping, fuzzy skill matching, and gap prioritization."""

import re
import logging
from typing import Any, Dict, List, Optional

from api.database import get_db_connection
from api.seed_data import get_skills_taxonomy, get_role_synonyms, get_skill_aliases, get_skill_difficulty

logger = logging.getLogger("resume-analyzer")
def _skill_difficulty(skill: str) -> int:
    """Get skill difficulty from cache."""
    return get_skill_difficulty().get(skill.lower(), 2)

# Synonym table for target-role → skills-taxonomy category mapping.
# Keys are lowercase role fragments; values are the categories whose skills
# should be treated as "target skills" for that role.
ROLE_SYNONYMS: Dict[str, List[str]] = {
    "backend": ["Web Frameworks", "Databases", "Other Technical", "Cloud & DevOps"],
    "back-end": ["Web Frameworks", "Databases", "Other Technical", "Cloud & DevOps"],
    "frontend": ["Web Frameworks", "Other Technical"],
    "front-end": ["Web Frameworks", "Other Technical"],
    "fullstack": ["Web Frameworks", "Databases", "Other Technical", "Cloud & DevOps"],
    "full-stack": ["Web Frameworks", "Databases", "Other Technical", "Cloud & DevOps"],
    "web developer": ["Web Frameworks", "Databases"],
    "web engineer": ["Web Frameworks", "Databases"],
    "react": ["Web Frameworks"],
    "react developer": ["Web Frameworks"],
    "react native": ["Web Frameworks", "Mobile Development"],
    "angular": ["Web Frameworks"],
    "vue": ["Web Frameworks"],
    "next.js": ["Web Frameworks"],
    "node": ["Web Frameworks", "Databases"],
    "node.js": ["Web Frameworks", "Databases"],
    "django": ["Web Frameworks", "Databases"],
    "flask": ["Web Frameworks"],
    "fastapi": ["Web Frameworks", "Databases"],
    "python developer": ["Programming Languages", "Web Frameworks"],
    "python engineer": ["Programming Languages", "Web Frameworks"],
    "java developer": ["Programming Languages", "Web Frameworks"],
    "java engineer": ["Programming Languages", "Web Frameworks"],
    "spring": ["Web Frameworks", "Databases"],
    "go developer": ["Programming Languages", "Web Frameworks"],
    "golang": ["Programming Languages", "Web Frameworks"],
    "rust": ["Programming Languages"],
    "ruby": ["Programming Languages", "Web Frameworks"],
    "rails": ["Web Frameworks", "Databases"],
    "php": ["Programming Languages", "Web Frameworks"],
    "ios": ["Mobile Development"],
    "ios developer": ["Mobile Development"],
    "android": ["Mobile Development"],
    "android developer": ["Mobile Development"],
    "mobile developer": ["Mobile Development"],
    "flutter": ["Mobile Development"],
    "swift": ["Mobile Development"],
    "kotlin": ["Mobile Development"],
    "data scientist": ["Data Science & AI"],
    "data science": ["Data Science & AI"],
    "data analyst": ["Data Science & AI"],
    "data engineer": ["Data Science & AI", "Databases", "Cloud & DevOps"],
    "ml engineer": ["Data Science & AI", "Cloud & DevOps"],
    "machine learning": ["Data Science & AI"],
    "ai engineer": ["Data Science & AI", "Cloud & DevOps"],
    "ai researcher": ["Data Science & AI"],
    "deep learning": ["Data Science & AI"],
    "nlp": ["Data Science & AI"],
    "computer vision": ["Data Science & AI"],
    "devops": ["Cloud & DevOps"],
    "sre": ["Cloud & DevOps"],
    "site reliability": ["Cloud & DevOps"],
    "cloud engineer": ["Cloud & DevOps"],
    "cloud architect": ["Cloud & DevOps"],
    "platform engineer": ["Cloud & DevOps"],
    "infrastructure": ["Cloud & DevOps"],
    "security engineer": ["Other Technical"],
    "cybersecurity": ["Other Technical"],
    "qa engineer": ["Other Technical"],
    "test engineer": ["Other Technical"],
    "sdet": ["Other Technical"],
    "software engineer": ["Programming Languages", "Web Frameworks", "Databases"],
    "software developer": ["Programming Languages", "Web Frameworks", "Databases"],
    "tech lead": ["Programming Languages", "Soft Skills"],
    "engineering manager": ["Soft Skills"],
    "engineering manager,": ["Soft Skills"],
    "cto": ["Soft Skills"],
    "product manager": ["Soft Skills"],
    "project manager": ["Soft Skills"],
    "scrum master": ["Soft Skills"],
}

def compare_resume_to_jd(resume_skills: List[str], jd_text: str) -> Dict[str, Any]:
    resume_set = {s.lower().strip() for s in (resume_skills or []) if s}
    jd_tokens = {token.strip(".,:;()[]{}").lower() for token in jd_text.split()}
    strong_keywords = [kw for kw in jd_tokens if len(kw) > 3]
    matched = sorted([kw for kw in strong_keywords if kw in resume_set])[:40]
    missing = sorted([kw for kw in strong_keywords if kw not in resume_set])[:40]
    coverage = 0
    if strong_keywords:
        coverage = int((len(matched) / len(set(strong_keywords))) * 100)
    return {"coverage_score": coverage, "matched_keywords": matched, "missing_keywords": missing}

# Canonical alias → taxonomy skill name.
# Each key is a variation users write on resumes; the value is the canonical
# skill in ALL_SKILLS / SKILLS_TAXONOMY.  Checked word-boundary-insensitively.
_SKILL_ALIASES: Dict[str, str] = {
    # Languages
    "js": "javascript", "ts": "typescript", "golang": "go", "rb": "ruby",
    "c sharp": "c#", "dot net": "asp.net", ".net": "asp.net", "objc": "objective-c",
    "py": "python", "rs": "rust", "kt": "kotlin",
    # Frameworks
    "react.js": "react", "reactjs": "react", "nextjs": "next.js", "next": "next.js",
    "vue.js": "vue", "vuejs": "vue", "nuxt": "nuxt.js", "nuxtjs": "nuxt.js",
    "angular.js": "angular", "angularjs": "angular",
    "svelte.js": "svelte", "sveltejs": "svelte",
    "node": "express", "nodejs": "express", "express.js": "express",
    "django rest": "django", "drf": "django", "flask api": "flask",
    "spring": "spring boot", "springframework": "spring boot",
    "rails": "ruby on rails", "ruby on rails": "ruby on rails",
    "laravel php": "laravel", "asp net": "asp.net",
    "tailwindcss": "tailwind", "tw": "tailwind",
    "jetpackcompose": "jetpack compose",
    "swiftui": "swiftui", "uikit": "ios",
    # Databases
    "postgres": "postgresql", "pg": "postgresql", "psql": "postgresql",
    "mongo": "mongodb", "mongo db": "mongodb",
    "elastic": "elasticsearch", "elastic search": "elasticsearch", "es": "elasticsearch",
    "mariadb": "mariadb", "mssql": "sql",
    "dynamo": "dynamodb", "dynamo db": "dynamodb",
    "firebase rtdb": "firebase", "firestore": "firebase",
    "sqlite3": "sqlite",
    # Cloud & DevOps
    "amazon web services": "aws", "ec2": "aws", "s3": "aws", "lambda": "aws",
    "google cloud": "gcp", "google cloud platform": "gcp", "gke": "gcp",
    "microsoft azure": "azure", "azure devops": "azure",
    "k8s": "kubernetes", "kube": "kubernetes",
    "ci/cd pipelines": "ci/cd", "cicd": "ci/cd", "continuous integration": "ci/cd",
    "jenkins": "jenkins", "github actions": "github",
    "terraform.io": "terraform", "tf": "terraform",
    "prom": "prometheus", "graf": "grafana",
    "nginx": "nginx", "apache": "nginx",
    # Data & AI
    "ml": "machine learning", "machinelearning": "machine learning",
    "dl": "deep learning", "deeplearning": "deep learning",
    "nlp": "nlp", "natural language processing": "nlp",
    "cv": "computer vision", "computer vision": "computer vision",
    "sklearn": "scikit-learn", "scikit learn": "scikit-learn",
    "tf": "tensorflow", "keras": "tensorflow",
    "torch": "pytorch", "py torch": "pytorch",
    "pandas": "pandas", "np": "numpy", "numpy": "numpy",
    "mpl": "matplotlib", "seaborn": "seaborn",
    "tableau": "tableau", "powerbi": "power bi",
    # Mobile
    "rn": "react native", "reactnative": "react native",
    "flutter.io": "flutter", "dart-lang": "dart",
    "xamarine": "xamarin",
    # Soft skills & process
    "scrum": "scrum", "kanban": "kanban", "agile/scrum": "agile",
    "jira": "agile", "trello": "agile",
    "figma": "figma", "sketch": "figma", "adobe xd": "figma",
    # Other
    "rest": "rest api", "restful": "rest api", "restapi": "rest api",
    "graph ql": "graphql", "graphql": "graphql",
    "micro services": "microservices", "micro-service": "microservices",
    "unit tests": "unit testing", "integration tests": "integration testing",
    "i.o.t.": "iot", "internet of things": "iot",
    "block chain": "blockchain",
    "pen testing": "security", "infosec": "security", "cybersecurity": "security",
    "load balancer": "aws", "cdn": "aws",
    "posix": "linux", "ubuntu": "linux", "centos": "linux", "debian": "linux",
    "bash": "shell", "zsh": "shell", "powershell": "powershell",
}

def fuzzy_skill_match(text: str, skill: str) -> bool:
    """Check for skill with word boundaries and common variations."""
    pattern = rf'\b{re.escape(skill)}\b'
    if re.search(pattern, text, re.IGNORECASE):
        return True
    # Check the alias table from cache
    skill_aliases = get_skill_aliases()
    canonical = skill_aliases.get(skill.lower(), skill)
    if canonical != skill.lower():
        pattern2 = rf'\b{re.escape(canonical)}\b'
        if re.search(pattern2, text, re.IGNORECASE):
            return True
    # Also check all aliases that map TO this skill
    for alias, target in skill_aliases.items():
        if target == skill.lower() and alias != skill.lower():
            if re.search(rf'\b{re.escape(alias)}\b', text, re.IGNORECASE):
                return True
    return False

def _target_categories_for_role(target_role: str) -> List[str]:
    """Map a target role string to a list of skill-taxonomy categories."""
    if not target_role:
        return ["Other Technical"]
    role_lower = target_role.lower()
    # Try role synonyms from cache - match on the longest fragment first
    role_synonyms = get_role_synonyms()
    matched_categories: List[str] = []
    fragments = sorted(role_synonyms.keys(), key=len, reverse=True)
    for frag in fragments:
        if frag in role_lower:
            matched_categories = list(dict.fromkeys(role_synonyms[frag]))  # dedupe preserving order
            return matched_categories
    # Fallback: original behavior
    taxonomy = get_skills_taxonomy()
    for cat in taxonomy:
        if any(s in role_lower for s in cat.lower().split()):
            return [cat]
    return ["Other Technical"]

def _get_role_skills_from_db(target_role: str) -> List[str]:
    """Get skills for a role from job_role_skills table (admin-defined)."""
    if not target_role:
        return []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT js.skill_name FROM job_role_skills js "
            "JOIN job_roles jr ON js.job_role_id = jr.id "
            "WHERE jr.title = %s AND jr.is_active = 1",
            (target_role,)
        )
        skills = [row[0] for row in cursor.fetchall()]
        conn.close()
        return skills
    except Exception as e:
        logger.error(f"Failed to get role skills: {e}")
        return []

def _get_required_skills_from_db(target_role: str) -> List[str]:
    """Get only required (core) skills for a role."""
    if not target_role:
        return []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT js.skill_name FROM job_role_skills js "
            "JOIN job_roles jr ON js.job_role_id = jr.id "
            "WHERE jr.title = %s AND jr.is_active = 1 AND js.is_required = 1",
            (target_role,)
        )
        skills = [row[0] for row in cursor.fetchall()]
        conn.close()
        return skills
    except Exception as e:
        logger.error(f"Failed to get required skills: {e}")
        return []

def _compute_local_match_score(
    found_skills: List[str], target_role: Optional[str]
) -> int:
    """Compute match score based on admin-defined role skills.

    Required (core) skills count 2x toward the score vs nice-to-have.
    Score formula: base 20 + required_matches * 12 + nice_matches * 5
    Max 95, min 20.
    """
    if not target_role:
        return 70
    all_skills = _get_role_skills_from_db(target_role)
    required_skills = _get_required_skills_from_db(target_role)
    nice_to_have = [s for s in all_skills if s not in required_skills]

    if not all_skills:
        return 50

    found_lower = {s.lower() for s in found_skills}
    required_matched = sum(1 for s in required_skills if s.lower() in found_lower)
    nice_matched = sum(1 for s in nice_to_have if s.lower() in found_lower)

    score = 20 + required_matched * 12 + nice_matched * 5
    return max(20, min(95, score))

# Difficulty ratings for skills (1=beginner, 2=intermediate, 3=advanced).
# Used by prioritization and roadmap generation.
_SKILL_DIFFICULTY: Dict[str, int] = {
    # Beginner (1)
    "html": 1, "css": 1, "git": 1, "linux": 1, "agile": 1, "scrum": 1,
    "communication": 1, "leadership": 1, "problem solving": 1, "teamwork": 1,
    "time management": 1, "public speaking": 1, "critical thinking": 1,
    "adaptability": 1, "mentoring": 1, "project management": 1,
    "sql": 1, "excel": 1, "power bi": 1,
    # Intermediate (2)
    "javascript": 2, "python": 2, "java": 2, "react": 2, "angular": 2,
    "vue": 2, "node.js": 2, "django": 2, "flask": 2, "fastapi": 2,
    "spring boot": 2, "express": 2, "laravel": 2,
    "mysql": 2, "postgresql": 2, "mongodb": 2, "redis": 2, "sqlite": 2,
    "docker": 2, "aws": 2, "azure": 2, "gcp": 2,
    "rest api": 2, "graphql": 2, "json": 2, "xml": 2,
    "testing": 2, "unit testing": 2, "integration testing": 2,
    "pandas": 2, "numpy": 2, "matplotlib": 2, "seaborn": 2,
    "flutter": 2, "react native": 2, "kotlin": 2, "swift": 2,
    "tailwind": 2, "bootstrap": 2, "jquery": 2,
    "jenkins": 2, "github": 2, "gitlab": 2,
    "terraform": 2, "ansible": 2,
    "figma": 2, "sketch": 2,
    # Advanced (3)
    "machine learning": 3, "deep learning": 3, "nlp": 3, "computer vision": 3,
    "tensorflow": 3, "pytorch": 3, "scikit-learn": 3,
    "kubernetes": 3, "microservices": 3, "ci/cd": 3,
    "elasticsearch": 3, "cassandra": 3, "dynamodb": 3, "neo4j": 3,
    "typescript": 3, "go": 3, "rust": 3, "scala": 3,
    "spark": 3, "hadoop": 3, "kafka": 3, "airflow": 3,
    "prometheus": 3, "grafana": 3, "nginx": 3,
    "security": 3, "blockchain": 3, "iot": 3,
}

def prioritize_missing_skills(
    missing_skills: List[str], target_role: Optional[str], found_skills: List[str]
) -> List[Dict[str, Any]]:
    """Score and sort missing skills by importance, difficulty, and market demand.

    Returns a list of dicts: [{skill, priority_score, difficulty, reason}, ...]
    sorted by priority_score descending.
    """
    if not missing_skills:
        return []

    target_categories = _target_categories_for_role(target_role)
    # Build a set of which categories each missing skill belongs to
    skill_to_cats: Dict[str, List[str]] = {}
    taxonomy = get_skills_taxonomy()
    for cat in target_categories:
        for s in taxonomy.get(cat, []):
            skill_to_cats.setdefault(s.lower(), []).append(cat)

    found_lower = {s.lower() for s in found_skills}
    scored: List[Dict[str, Any]] = []

    for skill in missing_skills:
        sl = skill.lower()
        cats = skill_to_cats.get(sl, [])
        difficulty = _skill_difficulty(sl)

        # Priority factors:
        # 1. Category count - skills in more target categories are more important
        cat_score = min(5, len(cats))

        # 2. Foundational check - if user is missing a "basic" skill for the role,
        #    it should be flagged as critical
        foundational = difficulty == 1
        foundational_bonus = 3 if foundational else 0

        # 3. Adjacent-skill bonus - if user has related skills, this gap is easier to close
        #    (prioritize gaps where user already has adjacent skills)
        adjacent_skills = set()
        if sl in {"react", "angular", "vue", "svelte", "next.js", "nuxt.js"}:
            adjacent_skills = {"html", "css", "javascript", "typescript"}
        elif sl in {"django", "flask", "fastapi", "spring boot", "express", "laravel"}:
            adjacent_skills = {"python", "java", "javascript", "node.js"}
        elif sl in {"docker", "kubernetes", "terraform", "ansible"}:
            adjacent_skills = {"linux", "aws", "azure", "gcp", "ci/cd"}
        elif sl in {"machine learning", "deep learning", "nlp", "computer vision"}:
            adjacent_skills = {"python", "numpy", "pandas", "statistics"}
        elif sl in {"tensorflow", "pytorch", "scikit-learn"}:
            adjacent_skills = {"python", "machine learning", "numpy"}
        elif sl in {"postgresql", "mysql", "mongodb", "redis", "elasticsearch"}:
            adjacent_skills = {"sql", "docker", "linux"}
        elif sl in {"aws", "azure", "gcp"}:
            adjacent_skills = {"linux", "docker", "terraform"}

        has_adjacent = bool(adjacent_skills & found_lower)
        adjacent_bonus = 2 if has_adjacent else 0

        # Combined priority score
        priority = cat_score + foundational_bonus + adjacent_bonus

        # Difficulty label
        diff_label = "beginner" if difficulty == 1 else "intermediate" if difficulty == 2 else "advanced"

        # Reason
        reasons = []
        if foundational:
            reasons.append("foundational skill for this role")
        if cat_score >= 3:
            reasons.append(f"required across {len(cats)} target areas")
        if has_adjacent:
            reasons.append("you have adjacent skills - easier to learn")
        if not reasons:
            reasons.append("commonly required for this role")

        scored.append({
            "skill": skill,
            "priority_score": priority,
            "difficulty": diff_label,
            "reason": "; ".join(reasons),
        })

    # Sort by priority_score desc, then difficulty asc (easier first)
    diff_order = {"beginner": 0, "intermediate": 1, "advanced": 2}
    scored.sort(key=lambda x: (-x["priority_score"], diff_order.get(x["difficulty"], 1)))
    return scored
