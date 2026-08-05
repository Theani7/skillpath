# Course data, field prediction, and video link generation.
from api.course_data import (
    COURSE_MAP, FIELD_KEYWORDS, INTERVIEW_VIDEOS, RESUME_VIDEOS, ROADMAPS,
    SKILL_RECOMMENDATIONS, SKILL_TUTORIAL_VIDEOS, android_course, ba_course,
    backend_course, cloud_course, cloudarch_course, cyber_course, de_course,
    devops_course, ds_course, frontend_course, fullstack_course, ios_course,
    it_course, ml_course, mobile_course, net_course, pm_course, qa_course,
    se_course, tw_course, uiux_course, web_course,
)

from api.seed_data import get_field_keywords

import urllib.parse

def predict_field_with_ai(resume_data: dict) -> str:
    """
    Takes the full parsed resume dictionary, and uses a weighted keyword 
    matching algorithm against skills, objective, and designation to find 
    the closest matching professional field.
    """
    # Defensive check
    if not resume_data:
        return "Unknown"
    
    field_keywords = get_field_keywords()
    if not field_keywords:
        return "Unknown"
        
    scores = {field: 0 for field in field_keywords.keys()}
    
    # Extract readable text fields
    skills = resume_data.get('skills', []) or []
    designation = resume_data.get('designation', []) or []
    objective = resume_data.get('objective', '') or ''
    
    # Normalize inputs
    user_skills_lower = [str(s).lower().strip() for s in skills]
    user_desig_lower = [str(d).lower().strip() for d in designation]
    objective_lower = str(objective).lower()
    
    for field, keyword_weights in field_keywords.items():
        for kw, weight in keyword_weights.items():
            kw = kw.lower()
            
            # --- 1. HIGHEST PRIORITY: Designation (Job Title) ---
            # If a user literally has the job title (e.g., "Data Scientist"), heavily favor it.
            if any(kw in d or d in kw for d in user_desig_lower):
                scores[field] += (weight * 3) # Triple weight for job titles
                
            # --- 2. HIGH PRIORITY: Exact Skill Matches ---
            # If "Machine Learning" exactly matches a skill in the list
            if kw in user_skills_lower:
                scores[field] += (weight * 2) # Double weight for exact skill match
            else:
                # --- 3. MEDIUM PRIORITY: Partial Skill Matches ---
                # e.g., skill is "Advanced React JS" and keyword is "React"
                if any(kw in s for s in user_skills_lower):
                    scores[field] += weight
                    
            # --- 4. LOWER PRIORITY: Objective/Summary Text ---
            # Look for the keyword organically in the objective paragraph
            if kw in objective_lower:
                scores[field] += weight
                
    # Find the field with the highest score
    best_field = max(scores, key=scores.get)
    best_score = scores[best_field]
    
    # Threshold: If their score is basically 0, we can't classify them
    if best_score < 3:
        return "Unknown"
        
    return best_field


def generate_youtube_search_links(skills: list) -> list:
    """
    Takes a list of recommended skills and generates exact video links if available,
    otherwise generates direct YouTube search query links.
    """
    links = []
    for skill in skills:
        skill_lower = skill.lower()
        if skill_lower in SKILL_TUTORIAL_VIDEOS:
            url = SKILL_TUTORIAL_VIDEOS[skill_lower]
            links.append({'title': f"Learn {skill}", 'url': url})
        else:
            query = urllib.parse.quote(f"{skill} tutorial for beginners")
            url = f"https://www.youtube.com/results?search_query={query}"
            links.append({'title': f"Learn {skill}", 'url': url})
    return links
