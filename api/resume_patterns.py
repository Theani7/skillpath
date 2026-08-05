import re
from typing import Dict, List

# Section header variants (lowercased, stripped of leading bullets/trailing colons).
# First match wins; multi-word headers are kept short (<= 40 chars in detector).
SECTION_HEADERS: Dict[str, List[str]] = {
    "experience": [
        "experience", "work experience", "professional experience",
        "work history", "employment", "employment history",
        "professional background", "career history", "relevant experience",
    ],
    "education": [
        "education", "academic", "academic background",
        "qualifications", "education & training", "education and training",
        "university", "educational background",
    ],
    "skills": [
        "skills", "technical skills", "technical stack",
        "core competencies", "competencies", "technologies",
        "skills & tools", "skills and tools", "tech skills",
        "key skills", "areas of expertise", "expertise",
    ],
    "projects": [
        "projects", "personal projects", "academic projects",
        "portfolio", "selected projects", "notable projects",
    ],
    "summary": [
        "summary", "profile", "objective", "about me",
        "professional summary", "career objective", "personal statement",
        "about", "overview",
    ],
    "certifications": [
        "certifications", "certificates", "licenses",
        "licenses & certifications", "licenses and certifications",
        "professional certifications", "credentials",
    ],
    "languages": [
        "languages", "language skills", "spoken languages",
    ],
    "awards": [
        "awards", "honors", "honors & awards", "honors and awards",
        "achievements", "recognition", "publications",
    ],
}

# Section canonical order - earlier wins on ambiguous header lines.
_SECTION_ORDER = ["summary", "experience", "education", "skills", "projects",
                  "certifications", "languages", "awards"]

# Date range detector - captures "Jan 2020 - Present", "2020 - 2023",
# "01/2020 - 12/2023", "Jan 2020 – Dec 2023", "Since 2020", etc.
MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*"

YEAR = r"(?:19|20)\d{2}"

DATE_RANGE_RE = re.compile(
    rf"""
    (?P<start>
        {MONTH}\s+{YEAR}
        | {YEAR}
        | \d{{1,2}}/\d{{4}}
        | present|current|now
    )
    \s*(?:-|–|—|to|until|—)\s*
    (?P<end>
        {MONTH}\s+{YEAR}
        | {YEAR}
        | \d{{1,2}}/\d{{4}}
        | present|current|now
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

SINGLE_DATE_RE = re.compile(rf"(?:since\s+)?({MONTH}\s+{YEAR}|{YEAR})", re.IGNORECASE)

# Phone - require country code or area code in (parens), 10-11 digits total
PHONE_RE = re.compile(
    r"""
    (?:\+?\d{1,3}[\s.\-]?)?
    (?:\(\d{2,4}\)|\d{2,4})
    [\s.\-]?
    \d{3,4}
    [\s.\-]?
    \d{3,5}
    (?:[\s.\-]?\d{1,5})?
    """,
    re.VERBOSE,
)

# Name - 2-4 capitalized words, no digits, no noise chars, max 60 chars
NAME_RE = re.compile(
    r"^[A-Z][a-zA-ZÀ-ÿ'\-]+(?:\s+[A-Z][a-zA-ZÀ-ÿ'\-\.]+){1,3}$"
)

NOISE_LINE_RE = re.compile(
    r"(resume|curriculum|vitae|profile|@|http|www\.|phone|email|tel:|mobile|address)",
    re.IGNORECASE,
)

# Education degree keywords
DEGREE_KEYWORDS = [
    "PhD", "Ph.D", "Doctor of", "Doctorate",
    "MBA", "M.B.A.",
    "Master of", "M.S.", "M.Sc.", "MA", "M.A.", "M.Eng.", "M.Tech", "MSc",
    "Bachelor of", "B.S.", "B.Sc.", "BA", "B.A.", "B.Eng.", "B.Tech", "BSc",
    "Associate of", "A.S.", "A.A.",
    "Diploma in", "Higher National Diploma", "HND",
]

# Use negative lookbehind/ahead (not \b) because trailing period in "B.S." sits
# between two non-word chars, so \b never matches there.
DEGREE_RE = re.compile(
    r"(?<![\w])(" + "|".join(re.escape(d) for d in DEGREE_KEYWORDS) + r")(?![\w])",
    re.IGNORECASE,
)

# Bullets (leading char sets) - used by the experience parser to separate
# header lines from bullet lines
BULLET_PREFIX_RE = re.compile(r"^[\s\-\•\·\*▪►▸→]+")

# Job title keywords (used to identify title lines inside an experience entry)
TITLE_KEYWORDS = [
    "engineer", "developer", "architect", "manager", "lead", "head",
    "director", "consultant", "analyst", "scientist", "designer",
    "administrator", "specialist", "officer", "intern", "associate",
    "founder", "co-founder", "researcher", "principal", "staff",
    "senior", "junior", "vp", "chief", "coo", "cto", "ceo", "cfo", "cio",
    "product owner", "scrum master", "programmer", "technician",
    "data analyst", "data scientist", "data engineer", "ml engineer",
    "sre", "devops", "qa", "sdet", "scientist", "writer", "editor",
]

# Section content key → return-dict key
SECTION_RETURN_KEY = {
    "experience": "experience_blocks",
    "education": "education_blocks",
    "certifications": "certifications",
    "languages": "languages",
    "awards": "awards",
}
