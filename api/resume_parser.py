"""Local fallback resume parsing: section detection and structured extraction without LLM calls.

Enhanced with spaCy NER, dateutil parsing, and rapidfuzz fuzzy matching.
"""

import re
import logging
from typing import Any, Dict, List, Optional

from api.skill_matching import (
    _get_role_skills_from_db,
    _get_required_skills_from_db,
    prioritize_missing_skills,
    _compute_local_match_score,
)
from api.roadmap_services import generate_personalized_roadmap
from api.parser_enhancements import (
    detect_name_spacy,
    extract_skills_fuzzy,
    parse_date_range,
    extract_companies_spacy,
    infer_implicit_skills,
)

logger = logging.getLogger("resume-analyzer")
from api.resume_patterns import (
    BULLET_PREFIX_RE, DEGREE_RE, NOISE_LINE_RE,
    PHONE_RE, SECTION_HEADERS, SECTION_RETURN_KEY, TITLE_KEYWORDS,
    _SECTION_ORDER,
)

def _detect_section(line_lower: str) -> Optional[str]:
    """Return canonical section name if `line_lower` is a section header, else None.

    Strips leading bullet characters (•, ·, -, *, ▪) and trailing punctuation,
    then word-boundary matches against SECTION_HEADERS.
    """
    cleaned = re.sub(r"^[\s\-\•\·\*▪►▸→]+", "", line_lower).strip().rstrip(":.,;")
    if not cleaned or len(cleaned) > 40:
        return None
    # Walk in canonical order so e.g. "Work Experience" beats "Experience"
    for sec in _SECTION_ORDER:
        for header in SECTION_HEADERS[sec]:
            if re.search(rf"\b{re.escape(header)}\b", cleaned):
                return sec
    return None

def _extract_company_from_line(line: str) -> Optional[str]:
    """Extract company from a 'Title at Company' or 'Title - Company' or 'Title, Company' line."""
    # "Title at Company" / "Title @ Company"
    m = re.search(r"(?:\s+at\s+|\s+@\s+)([A-Z][\w&.,'\- ]{1,60})", line)
    if m:
        return m.group(1).strip().rstrip(",.;")
    # "Title - Company" / "Title - Company" (em-dash)
    m = re.search(r"\s+[\-–—]\s+([A-Z][\w&.,'\- ]{1,60})$", line)
    if m:
        return m.group(1).strip().rstrip(",.;")
    # "Title, Company" (comma only if no year present)
    if "," in line and not re.search(r"\b(?:19|20)\d{2}\b", line):
        parts = [p.strip() for p in line.split(",") if p.strip()]
        if len(parts) == 2:
            return parts[1]
    return None

def _looks_like_title(line: str) -> bool:
    lower = line.lower()
    return any(kw in lower for kw in TITLE_KEYWORDS)

def _parse_experience_blocks(lines: List[str]) -> List[Dict[str, Any]]:
    """Group raw experience-section lines into {title, company, start_date, end_date, bullets}.

    Uses dateutil for flexible date parsing. Algorithm:
      1. Find every line that contains a date range - each one marks an entry boundary.
      2. For each entry, scan BACKWARDS from the date line to collect contiguous
         header lines (no bullets, < 100 chars, no blank lines in between).
         Convention: with 2+ header lines, line[0] is the title and line[-1] is the
         company. With 1 header line, try to extract via "at / @ / -" separator.
      3. Scan FORWARDS from the date line (to the next date or section end) to
         collect bullet lines (anything that isn't another date or a new entry's
         title-style header line).
      4. If a date line also contains the title/company on the same line (e.g.
         "Senior Engineer at Acme, Jan 2020 - Present"), extract from the line
         itself by stripping the date match.
    """
    # Step 1: locate every date-line index using dateutil
    date_positions: List[tuple] = []  # [(idx, start, end, stripped), ...]
    for i, raw in enumerate(lines):
        stripped = BULLET_PREFIX_RE.sub("", raw.strip(), count=1).strip()
        start, end = parse_date_range(stripped)
        if start or end:
            date_positions.append((i, start, end, stripped))

    if not date_positions:
        # No dates found - return empty list (don't synthesize a phantom block)
        return []

    blocks: List[Dict[str, Any]] = []
    for k, (idx, start, end, stripped) in enumerate(date_positions):
        # Step 2: collect header lines by scanning backwards
        header_lines: List[str] = []
        j = idx - 1
        while j >= 0:
            prev = lines[j].strip()
            if not prev:
                break
            if BULLET_PREFIX_RE.match(prev):
                break
            if len(prev) > 100:
                break
            header_lines.insert(0, prev)
            j -= 1

        # If the date line itself has title/company content, extract it
        date_text = f"{start} - {end}" if start and end else (start or end)
        same_line_header = stripped
        if date_text:
            same_line_header = stripped.replace(date_text, "").strip(" ,-–—")
        same_line_company = _extract_company_from_line(same_line_header) or ""
        same_line_title = ""
        if same_line_company and same_line_header.endswith(same_line_company):
            same_line_title = same_line_header[: -len(same_line_company)].rstrip(" ,-–—@at").strip()
        elif same_line_company:
            same_line_title = re.sub(
                rf"(\s+at\s+|\s+@\s+|\s+[\-–—]\s+){re.escape(same_line_company)}\s*$",
                "", same_line_header, flags=re.IGNORECASE,
            ).strip().rstrip(",;")
        else:
            same_line_title = same_line_header

        # Merge: prefer explicit header_lines, fall back to same_line extraction
        title, company = "", ""
        if len(header_lines) >= 2:
            title = header_lines[0]
            company = header_lines[1]
        elif len(header_lines) == 1:
            company = _extract_company_from_line(header_lines[0]) or ""
            if company and header_lines[0].endswith(company):
                title = header_lines[0][: -len(company)].rstrip(" ,-–—@at").strip()
            else:
                title = header_lines[0]
        elif same_line_title or same_line_company:
            title = same_line_title
            company = same_line_company

        # Step 3: collect bullet lines by scanning forwards to the next date
        bullets: List[str] = []
        next_idx = date_positions[k + 1][0] if k + 1 < len(date_positions) else len(lines)
        j = idx + 1
        while j < next_idx:
            raw_line = lines[j].strip()
            if not raw_line:
                j += 1
                continue
            bullet_clean = BULLET_PREFIX_RE.sub("", raw_line, count=1).strip()
            # Stop if this line is another date
            b_start, b_end = parse_date_range(bullet_clean)
            if b_start or b_end:
                break
            # Stop if this line looks like a job title (short, title case, no bullet prefix)
            if (
                not BULLET_PREFIX_RE.match(raw_line)
                and len(raw_line) < 60
                and raw_line[0].isupper()
                and _looks_like_title(raw_line)
            ):
                break
            bullets.append(bullet_clean)
            j += 1

        blocks.append({
            "title": title.strip(),
            "company": company.strip(),
            "start_date": start.strip(),
            "end_date": end.strip(),
            "bullets": bullets,
        })

    return blocks

def _entry_from_header_and_bullets(header_lines, bullet_lines, date_text=""):
    """Build a single experience entry when no date marker exists."""
    title, company = "", ""
    if len(header_lines) >= 2:
        title = header_lines[0]
        company = header_lines[1]
    elif header_lines:
        company = _extract_company_from_line(header_lines[0]) or ""
        if company and header_lines[0].endswith(company):
            title = header_lines[0][: -len(company)].rstrip(" ,-–—@at").strip()
        else:
            title = header_lines[0]
    return {
        "title": title.strip(),
        "company": company.strip(),
        "start_date": "",
        "end_date": "",
        "bullets": [BULLET_PREFIX_RE.sub("", b.strip(), count=1).strip() for b in bullet_lines if b.strip()],
    }

def _parse_education_blocks(lines: List[str]) -> List[Dict[str, Any]]:
    """Group education lines into {degree, institution, year} entries."""
    blocks: List[Dict[str, Any]] = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        degree = ""
        m = DEGREE_RE.search(line)
        if m:
            degree = m.group(0)

        # Year - first 4-digit year in [19|20]\d{2}
        year_match = re.search(r"\b(?:19|20)\d{2}\b", line)
        year = year_match.group(0) if year_match else ""

        # Institution - everything else, stripped of degree/year
        institution = line
        if degree:
            institution = institution.replace(degree, "").strip(" ,-–—")
        if year:
            institution = re.sub(rf"\b{year}\b", "", institution).strip(" ,-–—")
        # Clean stray separators and "in/from" preambles
        institution = re.sub(
            r"^(?:in|from|at|,)\s+", "", institution, flags=re.IGNORECASE,
        ).strip(" ,-–—")
        if not institution:
            institution = line

        blocks.append({
            "degree": degree,
            "institution": institution,
            "year": year,
        })
    return blocks

def _detect_name(text: str, lines: List[str]) -> str:
    """Find the candidate's name using spaCy NER, falling back to regex."""
    # Try spaCy first
    name = detect_name_spacy(text, lines)
    if name:
        return name

    # Fallback to regex heuristic
    for line in lines[:5]:
        candidate = line.strip()
        if not candidate or len(candidate) > 60:
            continue
        if NOISE_LINE_RE.search(candidate):
            continue
        words = candidate.split()
        if len(words) < 2 or len(words) > 4:
            continue
        if not all(w[0].isupper() for w in words if w):
            continue
        if re.search(r"\d", candidate):
            continue
        if _detect_section(candidate.lower()):
            continue
        return candidate
    return "Unknown"

def _tighten_phone(text: str) -> str:
    """Return a phone number if one is present and well-formed, else ''."""
    candidates: List[str] = []
    for m in PHONE_RE.finditer(text):
        raw = m.group(0).strip()
        digits = re.sub(r"\D", "", raw)
        # Accept 10-15 digits (international formats)
        if 10 <= len(digits) <= 15:
            # Reject if it's clearly a year (4 digits surrounded by spaces)
            if len(digits) == 4:
                continue
            candidates.append(raw)
    if not candidates:
        return ""
    # Prefer the one that contains + or parens
    for c in candidates:
        if "+" in c or "(" in c:
            return c
    return candidates[0]

def parse_resume_fallback(
    text: str,
    target_role: str = None,
    file_path: Optional[str] = None,
) -> dict:
    """
    Hybrid Resume Parser (v3).

    Produces a structured JSON payload matching the shape Gemini returns, using
    only local heuristics - no LLM calls. Used both as a high-confidence fast
    path (skips Gemini) and as a graceful fallback when Gemini is unavailable
    or rate-limited.

    Features:
      - Section detection with word-boundary header matching
      - Structured experience blocks: {title, company, start_date, end_date, bullets}
      - Structured education blocks: {degree, institution, year}
      - Job-title & company name extraction (populates designation + company_names)
      - Tightened phone regex (10-15 digits, requires + or parens, length-capped)
      - Name detection v2 (2-4 Title-Case words, first 5 lines)
      - Real match score (overlap with target-role category skills, 25-100)
      - Real page count for PDFs (via optional file_path)
      - Certifications / Languages / Awards sections captured separately
      - Target-role mapping via ROLE_SYNONYMS (covers common job titles)
    """
    text_lower = text.lower()
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    # 1. Section detection (improved - word-boundary, 40-char tolerance)
    sections: Dict[str, Any] = {
        "experience": [],
        "education": [],
        "skills": [],
        "projects": [],
        "summary": "",
        "certifications": [],
        "languages": [],
        "awards": [],
    }
    current_section: Optional[str] = None

    for line in lines:
        sec = _detect_section(line.lower())
        if sec is not None:
            current_section = sec
            continue
        if current_section is None:
            continue
        if current_section == "summary":
            sections["summary"] += line + " "
        else:
            sections[current_section].append(line)

    # 2. Entity extraction
    email_match = re.search(r'[\w.+-]+@[\w.-]+\.\w+', text)
    linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', text_lower)
    github_match = re.search(r'github\.com/[\w-]+', text_lower)
    phone = _tighten_phone(text)

    # 3. Skill extraction (rapidfuzzy matching against taxonomy)
    found_skills = extract_skills_fuzzy(text)

    # 3b. Semantic inference: expand found skills with related technologies
    implicit_skills = infer_implicit_skills(found_skills)
    found_skills = found_skills + implicit_skills

    # 4. Name detection (spaCy NER + regex fallback)
    name = _detect_name(text, lines)

    # 5. Structured experience & education blocks
    experience_blocks = _parse_experience_blocks(sections["experience"])
    education_blocks = _parse_education_blocks(sections["education"])

    # Also emit "flat" string lists for backward-compat with downstream code
    # that consumes resume_data.get("experience") as a list of strings.
    experience_flat: List[str] = []
    for b in experience_blocks:
        head = " - ".join(filter(None, [b.get("title"), b.get("company")]))
        dates = " - ".join(filter(None, [b.get("start_date"), b.get("end_date")]))
        if head and dates:
            experience_flat.append(f"{head} ({dates})")
        elif head:
            experience_flat.append(head)
        for bullet in b.get("bullets", []):
            experience_flat.append(f"  • {bullet}")
    if not experience_flat:
        experience_flat = sections["experience"][:10]

    education_flat: List[str] = []
    for b in education_blocks:
        head = " - ".join(filter(None, [b.get("degree"), b.get("institution")]))
        if b.get("year"):
            head = f"{head} ({b['year']})" if head else b["year"]
        if head:
            education_flat.append(head)
    if not education_flat:
        education_flat = sections["education"][:5]

    # 6. Designation + company_names from experience blocks + spaCy ORG
    designations = [b["title"] for b in experience_blocks if b.get("title")]
    company_names = [b["company"] for b in experience_blocks if b.get("company")]
    # Supplement with spaCy ORG entities if few companies found
    if len(company_names) < 2:
        spacy_companies = extract_companies_spacy(text)
        for c in spacy_companies:
            if c.lower() not in {x.lower() for x in company_names}:
                company_names.append(c)

    # 7. Missing skills for target role (use admin-defined skills from job_role_skills)
    target_skills = _get_role_skills_from_db(target_role)
    required_skills = _get_required_skills_from_db(target_role)
    required_set = {s.lower() for s in required_skills}
    raw_missing = [s for s in target_skills if s.title() not in found_skills]
    prioritized = prioritize_missing_skills(raw_missing, target_role, found_skills)
    missing_skills = [p["skill"] for p in prioritized[:8]]

    # 8. Match score (real, not static)
    match_score = _compute_local_match_score(found_skills, target_role)

    # 8b. Personalized roadmap based on actual gaps
    roadmap = generate_personalized_roadmap(target_role, found_skills, raw_missing)

    # 9. Page count (PDFs only - caller must pass file_path)
    no_of_pages = 1
    if file_path and file_path.lower().endswith(".pdf"):
        try:
            import fitz
            doc = fitz.open(file_path)
            no_of_pages = max(1, len(doc))
            doc.close()
        except Exception:
            pass

    # 10. Confidence scoring (more nuanced)
    confidence = 0
    if name != "Unknown":
        confidence += 20
    if email_match:
        confidence += 20
    if phone:
        confidence += 5
    if len(found_skills) >= 5:
        confidence += 25
    elif found_skills:
        confidence += 10
    if experience_blocks:
        confidence += 15
        if any(b.get("company") for b in experience_blocks):
            confidence += 5
    if education_blocks:
        confidence += 10
        if any(b.get("degree") for b in education_blocks):
            confidence += 5
    if sections["summary"].strip():
        confidence += 5
    confidence = min(100, confidence)

    return {
        "name": name,
        "email": email_match.group(0) if email_match else "",
        "mobile_number": phone,
        "skills": found_skills,
        "matched_role_skills": [
            {"skill": s, "is_required": s.lower() in required_set}
            for s in target_skills if s in found_skills or s.title() in found_skills
        ],
        "education": education_flat,
        "experience": experience_flat,
        "designation": designations,
        "company_names": company_names,
        "missing_skills": missing_skills,
        "match_score": match_score,
        "roadmap": roadmap,
        "links": {
            "linkedin": f"https://{linkedin_match.group(0)}" if linkedin_match else "",
            "github": f"https://{github_match.group(0)}" if github_match else "",
        },
        "summary": sections["summary"].strip(),
        "no_of_pages": no_of_pages,
        "experience_blocks": experience_blocks,
        "education_blocks": education_blocks,
        "certifications": sections["certifications"],
        "languages": sections["languages"],
        "awards": sections["awards"],
        "confidence_score": confidence,
        "parsing_method": "local_hybrid_v3",
    }

def rewrite_resume_fallback(resume_data: dict, target_role: str = None) -> dict:
    """Fallback resume rewriter using templates"""
    role = target_role or "Professional"
    name = resume_data.get("name", "Candidate")
    skills = resume_data.get("skills", [])
    original_exp = resume_data.get("experience", [])
    
    # Generate stronger action verbs for bullet points
    strong_verbs = ["Led", "Built", "Developed", "Implemented", "Optimized", "Delivered", "Managed", "Created", "Established", "Spearheaded"]
    
    rewritten_exp = []
    for exp in original_exp[:5]:
        if isinstance(exp, dict):
            new_desc = exp.get("description", "")
            # Add metrics-placeholder if not present
            if new_desc and not any(m in new_desc.lower() for m in ['increased', 'reduced', 'improved', '%', 'saved']):
                new_desc += " [Add metrics: e.g., improved efficiency by X%]"
            rewritten_exp.append(new_desc)
        elif isinstance(exp, str):
            rewritten_exp.append(exp)
    
    new_summary = f"Experienced {role} with proven ability to deliver results. Skilled in {', '.join(skills[:5]) if skills else 'technical skills'}."
    
    return {
        "name": name,
        "summary": new_summary,
        "experience": rewritten_exp,
        "skills": skills,
        "rewritten_method": "fallback"
    }
