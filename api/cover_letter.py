"""AI-powered cover letter generation service.

IMPORTANT: Personal information (name, email, phone) ALWAYS comes from the
authenticated user's account/profile. The resume is ONLY used for skills,
experience, and education. This prevents a user from uploading someone else's
resume and getting a cover letter with that person's name/contact info.
"""

import logging
from datetime import date
from typing import Optional

from api.ai_provider import chat

logger = logging.getLogger("resume-analyzer")


def generate_cover_letter(
    resume_data: dict,
    target_role: str,
    company_name: str = "",
    job_description: str = "",
    hiring_manager: str = "",
    user_info: Optional[dict] = None,
) -> dict:
    """Generate a tailored cover letter using the AI provider chain.

    Args:
        resume_data: Parsed resume data (skills, experience, education only).
        target_role: The role being applied for.
        company_name: Optional company name.
        job_description: Optional job description text.
        hiring_manager: Optional hiring manager name.
        user_info: Authenticated user's real info (name, email, phone, etc).

    Returns:
        dict with cover letter text and metadata, or error if missing data.
    """
    info = user_info or {}

    name = (info.get("name") or "").strip()
    email = (info.get("email") or "").strip()
    phone = (info.get("phone") or "").strip()

    missing = []
    if not name:
        missing.append("full name")
    if not email:
        missing.append("email address")
    if not phone:
        missing.append("phone number")

    if missing:
        return {
            "error": True,
            "missing_fields": missing,
            "message": f"Missing required information: {', '.join(missing)}. Please update your profile.",
        }

    greeting_name = hiring_manager.strip() if hiring_manager.strip() else "Hiring Manager"
    today = date.today().strftime("%B %d, %Y")

    skills = resume_data.get("skills", [])
    experience_blocks = resume_data.get("experience_blocks", [])
    education_blocks = resume_data.get("education_blocks", [])

    exp_lines = []
    for block in experience_blocks[:4]:
        title = block.get("title", "")
        company = block.get("company", "")
        bullets = block.get("bullets", [])
        date_range = ""
        start = block.get("start_date", "")
        end = block.get("end_date", "")
        if start or end:
            date_range = f" ({start} - {end})"
        exp_lines.append(f"- {title} at {company}{date_range}")
        for bullet in bullets[:3]:
            exp_lines.append(f"  * {bullet}")

    edu_lines = []
    for block in education_blocks[:2]:
        degree = block.get("degree", "")
        institution = block.get("institution", "")
        year = block.get("year", "")
        edu_lines.append(f"- {degree}, {institution} ({year})" if year else f"- {degree}, {institution}")

    profile_context = ""
    profile_parts = []
    if info.get("location"):
        profile_parts.append(f"Location: {info['location']}")
    if info.get("experience_years"):
        profile_parts.append(f"Years of experience: {info['experience_years']}")
    if info.get("bio"):
        profile_parts.append(f"Background: {info['bio']}")
    if info.get("linkedin_url"):
        profile_parts.append(f"LinkedIn: {info['linkedin_url']}")
    if info.get("github_url"):
        profile_parts.append(f"GitHub: {info['github_url']}")
    if info.get("current_role"):
        profile_parts.append(f"Current role: {info['current_role']}")
    if profile_parts:
        profile_context = "\n\nADDITIONAL PROFILE INFORMATION:\n" + "\n".join(profile_parts)

    prompt = f"""You are an expert cover letter writer. Write a cover letter following this EXACT format and rules.

CANDIDATE INFORMATION (from authenticated user profile):
Name: {name}
Email: {email}
Phone: {phone}

TARGET ROLE: {target_role}
COMPANY: {company_name if company_name else "[Not provided - reference 'the team' or 'the company' generically]"}
HIRING MANAGER: {greeting_name}

CANDIDATE SKILLS (from resume):
{', '.join(skills[:20]) if skills else 'Not specified'}

CANDIDATE EXPERIENCE (from resume):
{chr(10).join(exp_lines) if exp_lines else 'Not specified'}

CANDIDATE EDUCATION (from resume):
{chr(10).join(edu_lines) if edu_lines else 'Not specified'}{profile_context}

JOB DESCRIPTION:
{job_description if job_description else 'Not provided - base the letter on the target role title and general industry expectations.'}

COVER LETTER FORMAT SPEC:

STRUCTURE (in this exact order):

1. HEADER
{name}
{email} | {phone}
{today}

2. GREETING
Dear {greeting_name},

3. OPENING PARAGRAPH (3-4 sentences)
- State the exact job title being applied for and the company name
- Lead with the single strongest, most relevant qualification or achievement
- Include a specific detail about your background that makes you a strong fit
- Do NOT use: "I am writing to express my strong interest in..." or "I am writing to apply for..."

4. BODY PARAGRAPH 1 (4-5 sentences)
- Pick the 2-3 skills/experiences from the candidate's background that most directly match the job description's requirements
- Include at least one concrete detail: a number, tool, project outcome, or scale
- Connect each point explicitly to what the role needs
- Describe a specific project or accomplishment with measurable results

5. BODY PARAGRAPH 3-4 sentences)
- Additional achievement or context, e.g. a specific project, certification, or domain knowledge relevant to this company/industry
- Explain why this specific company appeals to you (if company name provided)

6. CLOSING PARAGRAPH (3-4 sentences)
- Reaffirm interest in this specific role/company (name them again)
- One sentence on what the candidate brings to the team
- Clear, low-pressure call to action
- Thank the reader for their time

7. SIGN-OFF
Sincerely,
{name}

RULES:
- Total length: 300-400 words (this is a firm requirement)
- Only include skills that are actually relevant to the job title/description
- Never use placeholder values ("Unknown", "[Company]", etc.)
- Banned phrases: "I am writing to express my strong interest", "reputation for excellence", "eager to bring this experience", "confident that my skills align perfectly", "well-prepared to contribute effectively", "leverage my skills"
- No em dashes
- Tone: direct and specific, not corporate-generic
- Every claim about the candidate must be traceable to actual resume/profile data

Return ONLY a JSON object with this exact schema:
{{
  "header_name": "{name}",
  "header_email": "{email}",
  "header_phone": "{phone}",
  "header_date": "{today}",
  "greeting": "Dear {greeting_name},",
  "opening_paragraph": "string",
  "body_paragraph_1": "string",
  "body_paragraph_2": "string (optional, empty string if not needed)",
  "closing_paragraph": "string",
  "sign_off": "Sincerely,",
  "signature": "{name}",
  "full_text": "string - the complete cover letter assembled from all parts above"
}}"""

    messages = [
        {"role": "system", "content": "You are an expert cover letter writer. Return ONLY valid JSON, no markdown or code fences."},
        {"role": "user", "content": prompt},
    ]

    text = chat(messages, temperature=0.7)
    if not text:
        logger.warning("Cover letter generation failed on all AI providers")
        return _generate_fallback(target_role, company_name, greeting_name, name, email, phone, today, skills, experience_blocks)

    import json
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse cover letter JSON: {text[:200]}")
        return _generate_fallback(target_role, company_name, greeting_name, name, email, phone, today, skills, experience_blocks)

    data["error"] = False
    data["target_role"] = target_role
    data["company_name"] = company_name
    return data


def _generate_fallback(
    target_role: str,
    company_name: str,
    greeting_name: str,
    name: str,
    email: str,
    phone: str,
    today: str,
    skills: list,
    experience_blocks: list,
) -> dict:
    """Fallback cover letter when AI providers are unavailable."""
    top_skills = ", ".join(skills[:3]) if skills else ""
    company = company_name or "the company"
    role = target_role or "this position"

    opening_parts = []
    if experience_blocks:
        latest = experience_blocks[0]
        title = latest.get("title", "")
        latest_company = latest.get("company", "")
        if title and latest_company:
            opening_parts.append(f"As {title} at {latest_company}, I have developed the exact skills needed for the {role} position at {company}.")
        elif title:
            opening_parts.append(f"My experience as {title} has prepared me for the {role} position at {company}.")
    if top_skills:
        opening_parts.append(f"My background includes hands-on work with {top_skills}.")
    if not opening_parts:
        opening_parts.append(f"My background aligns closely with what the {role} position at {company} requires.")

    opening = " ".join(opening_parts)

    body_parts = []
    for block in experience_blocks[:2]:
        bullets = block.get("bullets", [])
        if bullets:
            body_parts.append(bullets[0])
    body_1 = ""
    if body_parts:
        body_1 = " ".join(body_parts)
        if top_skills:
            body_1 += f" These experiences directly involved {top_skills}, which applies directly to this role."

    closing = f"I would welcome the chance to discuss how my background can contribute to {company}'s goals. Thank you for considering my application."

    full_text = f"""{name}
{email} | {phone}
{today}

Dear {greeting_name},

{opening}

{body_1}

{closing}

Sincerely,
{name}"""

    return {
        "error": False,
        "header_name": name,
        "header_email": email,
        "header_phone": phone,
        "header_date": today,
        "greeting": f"Dear {greeting_name},",
        "opening_paragraph": opening,
        "body_paragraph_1": body_1,
        "body_paragraph_2": "",
        "closing_paragraph": closing,
        "sign_off": "Sincerely,",
        "signature": name,
        "full_text": full_text,
        "target_role": target_role,
        "company_name": company_name,
    }
