"""Enhanced local resume parsing using spaCy NER, dateutil, and rapidfuzz."""

import re
import logging
from typing import Any, Dict, List, Optional, Set, Tuple

import spacy
from dateutil import parser as date_parser
from dateutil.parser import ParserError
from rapidfuzz import fuzz, process

from api.seed_data import get_all_skills

logger = logging.getLogger("resume-analyzer")

# Skill inference graph: if key is found, infer values as implicit skills
# This gives the parser basic semantic understanding of technology relationships
SKILL_INFERENCE_GRAPH: Dict[str, List[str]] = {
    # Frontend frameworks → core web technologies
    "react": ["javascript", "html", "css", "jsx", "typescript"],
    "reactjs": ["javascript", "html", "css", "jsx", "typescript"],
    "react native": ["javascript", "typescript", "mobile development"],
    "angular": ["javascript", "typescript", "html", "css"],
    "angularjs": ["javascript", "html", "css"],
    "vue": ["javascript", "html", "css", "typescript"],
    "vuejs": ["javascript", "html", "css", "typescript"],
    "svelte": ["javascript", "html", "css"],
    "next.js": ["javascript", "react", "html", "css", "typescript"],
    "nextjs": ["javascript", "react", "html", "css", "typescript"],
    "gatsby": ["javascript", "react", "html", "css"],
    "nuxt": ["javascript", "vue", "html", "css"],

    # Backend frameworks → languages & concepts
    "flask": ["python", "rest api", "web development"],
    "django": ["python", "rest api", "web development", "mvc"],
    "fastapi": ["python", "rest api", "web development"],
    "express": ["javascript", "node.js", "rest api", "web development"],
    "expressjs": ["javascript", "node.js", "rest api", "web development"],
    "spring": ["java", "rest api", "web development", "mvc"],
    "spring boot": ["java", "rest api", "web development", "microservices"],
    "rails": ["ruby", "web development", "mvc", "rest api"],
    "ruby on rails": ["ruby", "web development", "mvc", "rest api"],
    "asp.net": ["c#", "web development", "mvc", "rest api"],
    "laravel": ["php", "web development", "mvc", "rest api"],
    "symfony": ["php", "web development", "mvc"],

    # Languages → typical ecosystems
    "javascript": ["web development", "dom manipulation"],
    "typescript": ["javascript", "web development", "type systems"],
    "python": ["scripting", "automation", "data analysis"],
    "java": ["object-oriented programming", "jvm"],
    "golang": ["concurrency", "systems programming"],
    "rust": ["systems programming", "memory safety"],
    "c++": ["systems programming", "object-oriented programming"],
    "c#": [".net", "object-oriented programming"],
    "php": ["web development", "server-side programming"],
    "ruby": ["web development", "scripting"],
    "swift": ["ios development", "mobile development"],
    "kotlin": ["android development", "mobile development", "jvm"],
    "scala": ["jvm", "functional programming", "big data"],
    "r": ["statistics", "data analysis", "data visualization"],

    # Databases → related concepts
    "postgresql": ["sql", "database administration", "data modeling"],
    "mysql": ["sql", "database administration", "data modeling"],
    "mongodb": ["nosql", "database administration", "data modeling"],
    "redis": ["caching", "nosql", "database administration"],
    "elasticsearch": ["search", "nosql", "data analysis"],
    "cassandra": ["nosql", "distributed systems", "database administration"],
    "dynamodb": ["nosql", "aws", "database administration"],
    "firebase": ["nosql", "google cloud", "real-time databases"],

    # Cloud platforms → ecosystem services
    "aws": ["cloud computing", "devops", "infrastructure"],
    "amazon web services": ["cloud computing", "devops", "infrastructure"],
    "gcp": ["cloud computing", "devops", "infrastructure"],
    "google cloud": ["cloud computing", "devops", "infrastructure"],
    "azure": ["cloud computing", "devops", "infrastructure"],
    "heroku": ["cloud computing", "paas", "devops"],
    "digitalocean": ["cloud computing", "infrastructure", "devops"],

    # DevOps tools → practices
    "docker": ["containerization", "devops", "infrastructure"],
    "kubernetes": ["containerization", "devops", "infrastructure", "orchestration"],
    "k8s": ["containerization", "devops", "infrastructure", "orchestration"],
    "terraform": ["infrastructure as code", "devops", "cloud computing"],
    "ansible": ["configuration management", "devops", "infrastructure as code"],
    "jenkins": ["ci/cd", "devops", "automation"],
    "github actions": ["ci/cd", "devops", "automation"],
    "gitlab ci": ["ci/cd", "devops", "automation"],
    "circleci": ["ci/cd", "devops", "automation"],
    "prometheus": ["monitoring", "observability", "devops"],
    "grafana": ["monitoring", "observability", "data visualization"],
    "elk stack": ["logging", "monitoring", "data analysis"],
    "datadog": ["monitoring", "observability", "devops"],

    # ML/Data tools → domain knowledge
    "tensorflow": ["python", "machine learning", "deep learning", "neural networks"],
    "pytorch": ["python", "machine learning", "deep learning", "neural networks"],
    "keras": ["python", "machine learning", "deep learning"],
    "scikit-learn": ["python", "machine learning", "data analysis"],
    "pandas": ["python", "data analysis", "data manipulation"],
    "numpy": ["python", "data analysis", "scientific computing"],
    "spark": ["big data", "data engineering", "distributed computing"],
    "apache spark": ["big data", "data engineering", "distributed computing"],
    "hadoop": ["big data", "data engineering", "distributed computing"],
    "airflow": ["data engineering", "etl", "workflow orchestration"],
    "dbt": ["data engineering", "etl", "data transformation"],
    "snowflake": ["data warehousing", "sql", "data engineering"],
    "databricks": ["big data", "data engineering", "spark"],
    "tableau": ["data visualization", "business intelligence", "data analysis"],
    "power bi": ["data visualization", "business intelligence", "data analysis"],
    "looker": ["data visualization", "business intelligence", "data analysis"],

    # Mobile development
    "flutter": ["dart", "mobile development", "cross-platform"],
    "react native": ["javascript", "mobile development", "cross-platform"],
    "xamarin": ["c#", "mobile development", "cross-platform"],
    "ionic": ["javascript", "mobile development", "cross-platform"],

    # Testing frameworks → practices
    "jest": ["javascript", "testing", "unit testing"],
    "pytest": ["python", "testing", "unit testing"],
    "selenium": ["testing", "automation", "web testing"],
    "cypress": ["javascript", "testing", "end-to-end testing"],
    "junit": ["java", "testing", "unit testing"],

    # Version control & collaboration
    "git": ["version control", "collaboration"],
    "github": ["version control", "collaboration", "git"],
    "gitlab": ["version control", "collaboration", "git"],
    "bitbucket": ["version control", "collaboration", "git"],

    # APIs & protocols
    "graphql": ["api development", "rest api"],
    "rest api": ["api development", "web development"],
    "restful": ["api development", "web development"],
    "grpc": ["api development", "microservices"],
    "websocket": ["real-time communication", "web development"],
    "microservices": ["distributed systems", "api development", "architecture"],
}

_nlp = None


def _get_nlp():
    """Lazy-load spaCy model (singleton)."""
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found, falling back to regex-only parsing")
            _nlp = False
    return _nlp


def detect_name_spacy(text: str, lines: List[str]) -> str:
    """Use spaCy NER to find the person's name in the first few lines."""
    nlp = _get_nlp()
    if not nlp:
        return ""

    # Only process first 10 lines for efficiency
    header_text = "\n".join(lines[:10])
    doc = nlp(header_text[:2000])

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text.strip()
            # Filter out false positives (too short, contains digits)
            if len(name) >= 3 and not re.search(r"\d", name):
                # Skip if it looks like a section header
                if not re.search(
                    r"(experience|education|skills|projects|summary|profile|objective)",
                    name.lower(),
                ):
                    return name
    return ""


_NOISE_SKILLS = {
    # Single/double letter abbreviations that aren't skills
    "c", "r", "go",
    # Generic computing terms that aren't specific skills
    "cpu", "gpu", "ram", "ssd", "hdd", "ui", "ux", "os", "db",
    "ide", "api", "saas", "iaas",
    # Protocols/standards that are too generic alone
    "tcp", "udp", "ip", "ftp", "ssh", "ssl", "tls", "dns", "vpc", "vpn",
    "jwt", "xml", "json", "yaml", "csv", "pdf",
    # Media formats
    "png", "jpg", "svg", "mp3", "mp4",
}


def infer_implicit_skills(found_skills: List[str]) -> List[str]:
    """Expand found skills with implicit skills from the inference graph.

    Example: if "react" is found, infer ["javascript", "html", "css", "jsx"]
    """
    inferred = []
    seen = {s.lower() for s in found_skills}

    for skill in found_skills:
        skill_lower = skill.lower()
        # Look up direct matches in the graph
        if skill_lower in SKILL_INFERENCE_GRAPH:
            for implicit_skill in SKILL_INFERENCE_GRAPH[skill_lower]:
                if implicit_skill.lower() not in seen:
                    seen.add(implicit_skill.lower())
                    inferred.append(implicit_skill.title())
        # Also check for partial matches (e.g., "react native" matches "react")
        for key, values in SKILL_INFERENCE_GRAPH.items():
            if key in skill_lower and key != skill_lower:
                for implicit_skill in values:
                    if implicit_skill.lower() not in seen:
                        seen.add(implicit_skill.lower())
                        inferred.append(implicit_skill.title())

    return inferred


def extract_skills_fuzzy(
    text: str, threshold: int = 85
) -> List[str]:
    """Extract skills using rapidfuzz fuzzy matching against the taxonomy.

    Catches variants like:
      "JS" → "JavaScript", "Py" → "Python", "ReactJS" → "React"
      "k8s" → "Kubernetes", "ml" → "Machine Learning"
    """
    text_lower = text.lower()
    all_skills = get_all_skills()
    found = []
    seen = set()

    # Build a mapping of lowercase skill → original casing
    skill_map = {s.lower(): s for s in all_skills}

    # Tokenize into words and short phrases (1-3 grams)
    words = re.findall(r"[a-z0-9+#\.]+", text_lower)
    candidates = set()
    for w in words:
        if len(w) >= 2:
            candidates.add(w)
    # Bigrams and trigrams
    for i in range(len(words) - 1):
        candidates.add(f"{words[i]} {words[i+1]}")
    for i in range(len(words) - 2):
        candidates.add(f"{words[i]} {words[i+1]} {words[i+2]}")

    for candidate in candidates:
        if len(candidate) < 3 and not candidate.isdigit():
            continue
        # Skip common noise
        if candidate.lower() in _NOISE_SKILLS:
            continue
        match = process.extractOne(
            candidate,
            list(skill_map.keys()),
            scorer=fuzz.WRatio,
            score_cutoff=threshold,
        )
        if match:
            matched_key = match[0]
            original = skill_map[matched_key]
            if original.lower() not in seen and original.lower() not in _NOISE_SKILLS:
                seen.add(original.lower())
                # Title-case for consistency with the rest of the app
                found.append(original.title())

    return found


_DATE_CHARS_RE = re.compile(
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|"
    r"\d{4}|\d{1,2}[/\-]\d{2,4}|present|current|now)",
    re.IGNORECASE,
)

# Precompiled date patterns (order matters — most specific first)
_DATE_PATTERNS = [
    # "Jan 2020 - Present" or "Jan 2020 - Dec 2023"
    re.compile(
        r"(?P<start_month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+(?P<start_year>(?:19|20)\d{2})"
        r"\s*(?:-|–|—|to|until)\s*"
        r"(?:(?P<end_month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+)?(?P<end_year>(?:19|20)\d{2}|present|current|now)",
        re.IGNORECASE,
    ),
    # "2020 - 2023" (year range)
    re.compile(
        r"(?P<start_year>(?:19|20)\d{2})\s*(?:-|–|—|to|until)\s*(?P<end_year>(?:19|20)\d{2}|present|current|now)",
        re.IGNORECASE,
    ),
    # "01/2020 - 12/2023"
    re.compile(
        r"\d{1,2}/\d{4}\s*(?:-|–|—|to|until)\s*(?:\d{1,2}/\d{4}|present|current|now)",
        re.IGNORECASE,
    ),
    # "since 2020"
    re.compile(r"since\s+(?P<year>(?:19|20)\d{2})", re.IGNORECASE),
]


def parse_date_range(text: str) -> Tuple[str, str]:
    """Extract start/end dates from a line using regex patterns + dateutil validation.

    Handles formats like:
      "Jan 2020 - Present", "2020-2023", "01/2020 to 12/2023",
      "March 2021 – current", "since 2019"

    Returns ("", "") if no date range is found (avoids false positives from
    fuzzy dateutil matching on non-date text).
    """
    text_stripped = text.strip()
    if not text_stripped:
        return ("", "")

    # Quick check: must contain at least one date-like component
    if not _DATE_CHARS_RE.search(text_stripped):
        return ("", "")

    # Try each pattern
    for pattern in _DATE_PATTERNS:
        m = pattern.search(text_stripped)
        if m:
            groups = m.groupdict()
            if "start_month" in groups and groups.get("start_month"):
                # Month-year range
                start = f"{groups['start_month']} {groups['start_year']}"
                end = groups.get("end_month")
                if end:
                    end = f"{end} {groups['end_year']}"
                else:
                    end_raw = m.group(0).split("-")[-1].strip() if "-" in m.group(0) else "Present"
                    end = "Present" if "present" in end_raw.lower() else end_raw
                return (start, end)
            elif "start_year" in groups and groups.get("start_year"):
                # Year range or "since year"
                start = groups["start_year"]
                end = groups.get("end_year", "")
                if not end:
                    # Check for "present/current" after the separator
                    tail = text_stripped[m.end() - len(m.group(0)) + len(start):]
                    if re.search(r"present|current|now", text_stripped[m.start():], re.IGNORECASE):
                        end = "Present"
                return (start, end)

    # Fallback: try dateutil on lines that explicitly contain month names or years
    if re.search(r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\b", text_stripped, re.IGNORECASE):
        # Normalize separators
        normalized = re.sub(r"\s*(–|—|to|until|through)\s*", " - ", text_stripped)
        parts = normalized.split(" - ")
        if len(parts) == 2:
            start = _parse_single_date(parts[0].strip())
            end = _parse_single_date(parts[1].strip())
            if start or end:
                return (start, end)

    return ("", "")


def _parse_single_date(text: str) -> str:
    """Parse a single date string using dateutil (strict mode)."""
    text = text.strip()
    if not text:
        return ""

    # Handle present/current/now
    if text.lower() in ("present", "current", "now", "today"):
        return "Present"

    # Must contain a year or month name
    if not re.search(r"(?:\b(?:19|20)\d{2}\b|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)", text, re.IGNORECASE):
        return ""

    try:
        dt = date_parser.parse(text, fuzzy=False, default=None)
        # If only year was given, return just the year
        if re.match(r"^\d{4}$", text):
            return str(dt.year)
        # If month + year
        if re.match(
            r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)",
            text.lower(),
        ):
            return dt.strftime("%b %Y")
        return dt.strftime("%b %Y")
    except (ParserError, ValueError, OverflowError):
        pass

    # Fallback: extract year
    year_match = re.search(r"\b(19|20)\d{2}\b", text)
    if year_match:
        return year_match.group(0)

    return ""


def extract_companies_spacy(text: str) -> List[str]:
    """Use spaCy NER to find organization names."""
    nlp = _get_nlp()
    if not nlp:
        return []

    doc = nlp(text[:5000])
    companies = []
    seen = set()

    for ent in doc.ents:
        if ent.label_ == "ORG":
            name = ent.text.strip()
            # Filter out common false positives
            if len(name) < 2:
                continue
            if re.search(
                r"(resume|curriculum|vitae|bachelor|master|university|college)",
                name.lower(),
            ):
                continue
            if name.lower() not in seen:
                seen.add(name.lower())
                companies.append(name)

    return companies


def extract_locations_spacy(text: str) -> List[str]:
    """Use spaCy NER to find location names."""
    nlp = _get_nlp()
    if not nlp:
        return []

    doc = nlp(text[:5000])
    locations = []
    seen = set()

    for ent in doc.ents:
        if ent.label_ in ("GPE", "LOC"):
            loc = ent.text.strip()
            if loc.lower() not in seen:
                seen.add(loc.lower())
                locations.append(loc)

    return locations
