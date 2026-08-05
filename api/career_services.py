import json
import re
from typing import Any, Dict, List, Tuple

from api.market_data import get_market_trends_for_role
from api.skill_matching import _target_categories_for_role
from api.seed_data import get_skills_taxonomy


# Action verbs that signal strong, results-oriented bullets
_ACTION_VERBS = {
    "led", "built", "developed", "implemented", "optimized", "delivered", "managed",
    "created", "established", "spearheaded", "architected", "designed", "launched",
    "reduced", "increased", "improved", "automated", "streamlined", "migrated",
    "integrated", "deployed", "scaled", "refactored", "debugged", "resolved",
    "coordinated", "mentored", "guided", "directed", "oversaw", "owned",
    "drove", "championed", "pioneered", "invented", "produced", "shipped",
    "instrumented", "standardized", "consolidated", "quantified", "measured",
}

# Metrics patterns that indicate quantified impact
_METRICS_RE = re.compile(
    r"(?:\d+\.?\d*\s*(?:%|percent|ms|seconds?|minutes?|hours?|days?|weeks?|months?)"
    r"|\$\s*\d|kpi|roi|uptime|latency|throughput|revenue|cost\s*saving"
    r"|\d+\s*(?:users?|requests?|transactions?|deployments?|releases?))",
    re.IGNORECASE,
)


def _score_experience_blocks(exp_blocks: List[Dict[str, Any]]) -> Tuple[int, List[str]]:
    """Score experience quality based on structured experience_blocks.

    Returns (score_out_of_35, feedback_messages).
    Scoring dimensions:
      - Entry count (up to 8 pts)
      - Total bullet count (up to 8 pts)
      - Average bullets per entry (up to 6 pts)
      - Action verb usage (up to 6 pts)
      - Quantified metrics (up to 7 pts)
    """
    feedback: List[str] = []
    if not exp_blocks:
        feedback.append("No professional experience detected. Add work history with detailed bullet points.")
        return 0, feedback

    n_entries = len(exp_blocks)

    # --- Entry count (0-8) ---
    if n_entries >= 5:
        entry_pts = 8
    elif n_entries >= 3:
        entry_pts = 6
    elif n_entries >= 2:
        entry_pts = 4
    else:
        entry_pts = 2
        if n_entries == 1:
            feedback.append("You only have 1 experience entry. Add more roles to show career progression.")

    # --- Total bullet count (0-8) ---
    all_bullets = []
    for b in exp_blocks:
        all_bullets.extend(b.get("bullets", []))
    total_bullets = len(all_bullets)
    if total_bullets >= 12:
        bullet_pts = 8
    elif total_bullets >= 8:
        bullet_pts = 6
    elif total_bullets >= 5:
        bullet_pts = 4
    elif total_bullets >= 2:
        bullet_pts = 2
    else:
        bullet_pts = 1
        feedback.append("Your experience bullets are sparse. Aim for 3-5 bullet points per role with specific accomplishments.")

    # --- Average bullets per entry (0-6) ---
    avg_bullets = total_bullets / n_entries if n_entries else 0
    if avg_bullets >= 4:
        avg_pts = 6
    elif avg_bullets >= 3:
        avg_pts = 4
    elif avg_bullets >= 2:
        avg_pts = 2
    else:
        avg_pts = 0
        if n_entries > 1:
            feedback.append("Some roles have very few bullets. Each role should have 3-5 detailed bullet points.")

    # --- Action verb usage (0-6) ---
    verbs_found = set()
    for bullet in all_bullets:
        first_word = bullet.strip().split()[0].lower().rstrip(".,;:") if bullet.strip() else ""
        if first_word in _ACTION_VERBS:
            verbs_found.add(first_word)
    verb_ratio = len(verbs_found) / max(1, total_bullets)
    if verb_ratio >= 0.6:
        verb_pts = 6
    elif verb_ratio >= 0.4:
        verb_pts = 4
    elif verb_ratio >= 0.2:
        verb_pts = 2
    else:
        verb_pts = 0
        if total_bullets >= 3:
            feedback.append("Start bullets with strong action verbs (Led, Built, Implemented, Optimized, Delivered) instead of 'Responsible for' or 'Worked on'.")

    # --- Quantified metrics (0-7) ---
    metrics_count = sum(1 for b in all_bullets if _METRICS_RE.search(b))
    metrics_ratio = metrics_count / max(1, total_bullets)
    if metrics_ratio >= 0.5:
        metrics_pts = 7
    elif metrics_ratio >= 0.3:
        metrics_pts = 5
    elif metrics_ratio >= 0.15:
        metrics_pts = 3
    elif metrics_count >= 1:
        metrics_pts = 1
    else:
        metrics_pts = 0
        if total_bullets >= 3:
            feedback.append("Add quantified results to your bullets (e.g., 'reduced latency by 40%', 'served 10K+ users', 'saved $50K annually').")

    total = entry_pts + bullet_pts + avg_pts + verb_pts + metrics_pts
    return min(35, total), feedback


def compute_resume_score_breakdown(resume_data: Dict[str, Any], target_role: str = None) -> Tuple[int, List[str], Dict[str, Any]]:
    breakdown = {
        "summary": {"weight": 15, "score": 0, "status": "missing", "evidence": []},
        "education": {"weight": 15, "score": 0, "status": "missing", "evidence": []},
        "experience": {"weight": 35, "score": 0, "status": "missing", "evidence": []},
        "skills": {"weight": 25, "score": 0, "status": "missing", "evidence": []},
        "contact_info": {"weight": 10, "score": 0, "status": "missing", "evidence": []},
    }
    feedback_msgs: List[str] = []

    # 1. Summary Analysis
    summary = resume_data.get("summary", "") or resume_data.get("objective", "")
    if summary and len(str(summary)) > 30:
        breakdown["summary"]["score"] = 15
        breakdown["summary"]["status"] = "present"
        breakdown["summary"]["evidence"] = [summary[:100] + "..."]
    else:
        feedback_msgs.append("Your professional summary is too short or missing. Add a 2-3 sentence overview of your career goals.")

    # 2. Education Analysis
    edu = resume_data.get("education") or resume_data.get("education_blocks") or []
    if edu:
        breakdown["education"]["score"] = 15
        breakdown["education"]["status"] = "present"
        breakdown["education"]["evidence"] = edu[:2] if isinstance(edu, list) else [str(edu)[:100]]
    else:
        feedback_msgs.append("Education details not found. Ensure your degrees and universities are clearly listed.")

    # 3. Experience Analysis - quality-aware (uses experience_blocks if available)
    exp_blocks = resume_data.get("experience_blocks") or []
    exp_flat = resume_data.get("experience") or []
    if exp_blocks:
        exp_score, exp_feedback = _score_experience_blocks(exp_blocks)
        breakdown["experience"]["score"] = exp_score
        breakdown["experience"]["status"] = "present"
        breakdown["experience"]["evidence"] = [
            f"{b.get('title', '?')} at {b.get('company', '?')}" for b in exp_blocks[:2]
        ]
        feedback_msgs.extend(exp_feedback)
    elif exp_flat:
        # Fallback: treat flat experience as a list of strings
        exp_count = len(exp_flat)
        if exp_count >= 5:
            breakdown["experience"]["score"] = 25
        elif exp_count >= 3:
            breakdown["experience"]["score"] = 18
        else:
            breakdown["experience"]["score"] = 10
            feedback_msgs.append("Your experience section is brief. Add more detailed bullet points describing your impact.")
        breakdown["experience"]["status"] = "present"
        breakdown["experience"]["evidence"] = exp_flat[:2]
    else:
        feedback_msgs.append("No professional experience detected. Add internships, projects, or work history.")

    # 4. Skills Analysis - role-aware scoring (uses admin-defined role skills)
    skills = resume_data.get("skills") or []
    if skills:
        skill_count = len(skills)

        # If a target role is provided, score by RELEVANT skills (from job_role_skills)
        if target_role:
            from api.skill_matching import _get_role_skills_from_db, _get_required_skills_from_db
            role_skills = _get_role_skills_from_db(target_role)
            required_skills = _get_required_skills_from_db(target_role)
            role_skills_lower = {s.lower() for s in role_skills}
            required_lower = {s.lower() for s in required_skills}
            relevant_count = sum(1 for s in skills if s.lower() in role_skills_lower)
            required_matched = sum(1 for s in skills if s.lower() in required_lower)
            nice_matched = relevant_count - required_matched

            # Required skills count 2x: base 0 + required*3 + nice*1, max 25
            score = min(25, required_matched * 3 + nice_matched * 1)
            breakdown["skills"]["score"] = score

            if relevant_count == 0:
                feedback_msgs.append(
                    f"None of your {skill_count} skills match {target_role}. "
                    f"Add skills like: {', '.join(role_skills[:5])}."
                )
            elif required_matched < len(required_skills):
                missing_required = [s for s in required_skills if s.lower() not in {sk.lower() for sk in skills}]
                feedback_msgs.append(
                    f"You have {required_matched}/{len(required_skills)} core skills for {target_role}. "
                    f"Add missing core skills: {', '.join(missing_required[:3])}."
                )
        else:
            # No target role - count-based scoring (original behavior)
            if skill_count >= 10:
                breakdown["skills"]["score"] = 25
            elif skill_count >= 5:
                breakdown["skills"]["score"] = 15
            else:
                breakdown["skills"]["score"] = 10
                feedback_msgs.append("You have very few skills listed. Add more technical and soft skills to improve visibility.")
        
        breakdown["skills"]["status"] = "present"
        breakdown["skills"]["evidence"] = skills[:8]
    else:
        feedback_msgs.append("Skills section is empty. This is critical for ATS matching.")

    # 5. Contact Info Analysis
    has_email = bool(resume_data.get("email"))
    has_phone = bool(resume_data.get("mobile_number") or resume_data.get("phone"))
    if has_email and has_phone:
        breakdown["contact_info"]["score"] = 10
        breakdown["contact_info"]["status"] = "present"
    elif has_email or has_phone:
        breakdown["contact_info"]["score"] = 5
        feedback_msgs.append("Missing either email or phone number. Recruiters need both to reach you.")
    else:
        feedback_msgs.append("Contact information missing. Ensure your email and phone are visible.")

    total = sum(v["score"] for v in breakdown.values())
    return total, feedback_msgs, breakdown


def generate_job_matches(target_role: str, skills: List[str], missing_skills: List[str]) -> List[Dict[str, Any]]:
    role = target_role or "General"
    trends = get_market_trends_for_role(role)
    regions = trends.get("regional_distribution", [])
    top_skills = trends.get("top_skills", [])
    skill_set = {s.lower() for s in skills}
    missing_set = {s.lower() for s in missing_skills}
    matches: List[Dict[str, Any]] = []

    workplaces = ["Remote", "Hybrid", "On-site"]
    for idx, row in enumerate(top_skills[:6]):
        skill = row.get("skill", "Core Skill")
        region = regions[idx % len(regions)]["region"] if regions else "Global"
        salary = row.get("salary", 0)
        has_skill = skill.lower() in skill_set
        is_missing = skill.lower() in missing_set
        
        base_score = 70
        if has_skill:
            fit = base_score + 15
        elif is_missing:
            fit = base_score - 10
        else:
            fit = base_score + 5
            
        if salary and salary > 100000:
            fit = min(95, fit + 5)
            
        matches.append(
            {
                "job_id": f"{role[:3].upper()}-{idx+1:03d}",
                "title": f"{role} Specialist - {skill}",
                "company": f"{skill} Labs",
                "location": region,
                "workplace_type": workplaces[idx % len(workplaces)],
                "salary_estimate": salary,
                "fit_score": fit,
                "why_matched": [
                    f"Role aligns with {role}",
                    f"Market demand for {skill} is high",
                    "Score accounts for your current and missing skills",
                ],
            }
        )
    return matches


def generate_interview_questions(target_role: str, missing_skills: List[str], skills: List[str]) -> List[Dict[str, Any]]:
    role = target_role or "General"
    questions: List[Dict[str, Any]] = []
    baseline = [
        f"Walk me through your most relevant {role} project end-to-end.",
        "Describe a technical challenge where your first solution failed and how you recovered.",
        "How do you prioritize delivery speed versus quality in a team setting?",
    ]
    for idx, q in enumerate(baseline, start=1):
        questions.append({"id": idx, "question": q, "category": "behavioral"})

    start = len(questions) + 1
    focus_skills = missing_skills[:4] if missing_skills else skills[:4]
    for offset, skill in enumerate(focus_skills):
        questions.append(
            {
                "id": start + offset,
                "question": f"How would you design, implement, and validate a feature using {skill} for a {role} product?",
                "category": "technical",
                "focus_skill": skill,
            }
        )
    return questions


def rank_candidates(candidate_payloads: List[Dict[str, Any]], target_role: str) -> List[Dict[str, Any]]:
    ranked: List[Dict[str, Any]] = []
    for item in candidate_payloads:
        data = item.get("analysis_data") or item
        
        if isinstance(data, dict):
            inner_data = data.get("data", data)
        else:
            inner_data = data
            
        resume_score = float(inner_data.get("resume_score", 0) if isinstance(inner_data, dict) else 0)
        match_score = float(inner_data.get("match_score", 0) if isinstance(inner_data, dict) else 0)
        
        missing_skills = inner_data.get("missing_skills", []) if isinstance(inner_data, dict) else []
        missing_count = len(missing_skills) if isinstance(missing_skills, list) else 0
        
        final = round((resume_score * 0.5) + (match_score * 0.45) - (missing_count * 1.5), 2)
        name = inner_data.get("name") if isinstance(inner_data, dict) else item.get("name", "Unknown")
        
        ranked.append(
            {
                "candidate_id": item.get("candidate_id") or item.get("id"),
                "name": name,
                "target_role": target_role,
                "resume_score": resume_score,
                "match_score": match_score,
                "missing_skills_count": missing_count,
                "final_rank_score": max(0, min(100, final)),
            }
        )
    return sorted(ranked, key=lambda x: x["final_rank_score"], reverse=True)


def rewrite_resume_bullets_fallback(resume_data: Dict[str, Any], target_role: str) -> Dict[str, Any]:
    role = target_role or "target role"
    experience = resume_data.get("experience") or []
    rewritten = []
    
    if not experience:
        return {"target_role": role, "rewritten_bullets": []}
    
    action_verbs = ["Led", "Developed", "Implemented", "Optimized", "Streamlined"]
    for idx, line in enumerate(experience[:5]):
        bullet = str(line).strip()
        if not bullet:
            continue
        verb = action_verbs[idx % len(action_verbs)]
        rewritten.append(
            {
                "before": bullet,
                "after": f"{verb} key initiatives in {role}, driving measurable improvements through strategic planning and cross-functional collaboration.",
            }
        )
    
    if not rewritten:
        rewritten.append(
            {
                "before": "Worked on projects and responsibilities.",
                "after": f"Contributed to {role} projects with demonstrated impact on team delivery and business outcomes.",
            }
        )
    return {"target_role": role, "rewritten_bullets": rewritten}


def parse_json_safely(text: str) -> Dict[str, Any]:
    try:
        payload = json.loads(text)
        if isinstance(payload, dict):
            return payload
    except Exception:
        pass
    return {}
