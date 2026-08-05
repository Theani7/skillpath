"""Learning roadmap generation (personalized, synthetic, fallback) and project recommendations."""

import os
import logging
from typing import Any, Dict, List

from api.skill_matching import _skill_difficulty, prioritize_missing_skills
from api.seed_data import (
    get_skills_taxonomy, get_role_config, get_skill_clusters,
    get_learning_actions, get_learning_resources,
)

logger = logging.getLogger("resume-analyzer")

SKIP_LOCAL_LLM = os.getenv("SKIP_LOCAL_LLM", "false").lower() in ("1", "true", "yes")
def generate_personalized_roadmap(
    target_role: str, found_skills: List[str], missing_skills: List[str]
) -> List[dict]:
    """Generate a smart, role-specific learning roadmap using local LLM with template fallback."""
    role = target_role or "Professional"
    prioritized = prioritize_missing_skills(missing_skills, target_role, found_skills)

    if not prioritized:
        return _generate_mastery_roadmap(role, found_skills)

    # Try LLM-powered action items first (unless disabled)
    llm_actions = {}
    if not SKIP_LOCAL_LLM:
        from api.local_llm import generate_roadmap_with_llm
        llm_actions = generate_roadmap_with_llm(role, found_skills, missing_skills)

    # Fallback to template-based generation

    # Get role-specific configuration
    role_config = _get_role_config(role)

    # Group related skills into learning chunks
    skill_groups = _group_related_skills(prioritized, role)

    # Build phases from skill groups
    phases = []

    for i, group in enumerate(skill_groups):
        group_skills = [s["skill"] for s in group]
        avg_difficulty = sum(_skill_difficulty(s) for s in group_skills) / len(group_skills)

        # Estimate duration based on difficulty
        if avg_difficulty <= 1.3:
            duration_weeks = max(1, len(group_skills))
            difficulty_label = "Fundamentals"
        elif avg_difficulty <= 2.3:
            duration_weeks = max(2, len(group_skills) + 1)
            difficulty_label = "Core Skills"
        else:
            duration_weeks = max(3, len(group_skills) + 1)
            difficulty_label = "Advanced Topics"

        # Generate specific action items for each skill
        action_items = []
        resources = []
        for skill in group:
            skill_lower = skill["skill"].lower()
            # Use LLM actions if available, otherwise fall back to templates
            if llm_actions and skill_lower in llm_actions:
                action_items.extend(llm_actions[skill_lower])
            else:
                skill_actions, skill_resources = _generate_skill_actions(skill, found_skills, role)
                action_items.extend(skill_actions)
                resources.extend(skill_resources)

        # Add role-specific project suggestion
        project_suggestion = _get_role_project_suggestion(group_skills, role, role_config)
        action_items.append(project_suggestion)
        action_items.append("Document your learning and add to portfolio")

        phase_title = _generate_phase_title(group_skills, i + 1, difficulty_label)

        phases.append({
            "step": i + 1,
            "title": phase_title,
            "duration": f"{duration_weeks} week{'s' if duration_weeks > 1 else ''}",
            "skills": group_skills,
            "action_items": action_items,
            "resources": resources[:6],
            "difficulty": difficulty_label,
        })

    # Add role-specific career prep phase
    career_prep = _generate_career_prep_phase(role, role_config)
    career_prep["step"] = len(phases) + 1
    phases.append(career_prep)

    return phases

def _get_role_config(role: str) -> dict:
    """Get role-specific configuration for roadmap generation."""
    return get_role_config(role)

def _get_role_project_suggestion(skills: List[str], role: str, role_config: dict) -> str:
    """Generate a role-specific project suggestion based on skills."""
    import random

    project_types = role_config.get("project_types", ["personal project"])

    # Match skills to specific project ideas
    skill_set = {s.lower() for s in skills}

    if "react" in skill_set or "vue" in skill_set or "angular" in skill_set:
        return f"Build a {random.choice(['interactive dashboard', 'task management app', 'portfolio website'])} using {skills[0]}"
    elif "docker" in skill_set or "kubernetes" in skill_set:
        return f"Containerize and deploy a {random.choice(['microservices app', 'full-stack application', 'ML model service'])} using Docker"
    elif "machine learning" in skill_set or "pytorch" in skill_set or "tensorflow" in skill_set:
        return f"Build an {random.choice(['image classifier', 'recommendation system', 'predictive model'])} end-to-end"
    elif "postgresql" in skill_set or "mongodb" in skill_set:
        return f"Design and implement a {random.choice(['database schema', 'data pipeline', 'API with database'])} for a real use case"
    elif "aws" in skill_set or "azure" in skill_set:
        return f"Deploy a {random.choice(['serverless application', 'web app with CI/CD', 'static site with CDN'])} to the cloud"
    else:
        return f"Build a {random.choice(project_types)} combining {', '.join(skills[:2])}"

def _generate_career_prep_phase(role: str, role_config: dict) -> dict:
    """Generate a role-specific career preparation phase."""
    interview_focus = role_config.get("interview_focus", ["technical fundamentals", "problem solving"])
    portfolio_emphasis = role_config.get("portfolio_emphasis", "demonstrated learning")

    return {
        "title": "Career Positioning & Interview Prep",
        "duration": "2 weeks",
        "skills": ["Interview Prep", "Portfolio", "Networking"],
        "action_items": [
            f"Update LinkedIn highlighting {portfolio_emphasis}",
            f"Practice {interview_focus[0]} and {interview_focus[1]} questions",
            "Build 1-2 portfolio projects showcasing your new skills",
            "Contribute to open-source projects in your target domain",
        ],
        "resources": [],
        "difficulty": "Preparation",
    }

def _generate_mastery_roadmap(role: str, found_skills: List[str]) -> List[dict]:
    """Generate roadmap when no skill gaps exist - focus on mastery and positioning."""
    top_skills = found_skills[:3] if found_skills else ["System Design"]
    return [
        {
            "step": 1,
            "title": f"Deepen Expertise in {top_skills[0]}",
            "duration": "3 weeks",
            "skills": top_skills[:2],
            "action_items": [
                f"Complete an advanced course in {top_skills[0]}",
                "Build a production-grade project showcasing depth",
                "Write a technical blog post about what you learned",
            ],
            "resources": [],
            "difficulty": "Advanced",
        },
        {
            "step": 2,
            "title": "Open Source & Community",
            "duration": "3 weeks",
            "skills": ["Open Source", "Technical Writing"],
            "action_items": [
                "Contribute to an open-source project in your domain",
                "Submit a pull request to a popular library",
                "Write 2-3 technical articles about your expertise",
            ],
            "resources": [],
            "difficulty": "Advanced",
        },
        {
            "step": 3,
            "title": "Leadership & Mentorship",
            "duration": "2 weeks",
            "skills": ["Technical Leadership", "Mentoring"],
            "action_items": [
                "Mentor a junior developer on a project",
                "Lead a code review or architecture discussion",
                "Document best practices for your team",
            ],
            "resources": [],
            "difficulty": "Advanced",
        },
        {
            "step": 4,
            "title": "Career Positioning",
            "duration": "2 weeks",
            "skills": ["Interview Prep", "Networking"],
            "action_items": [
                "Update LinkedIn and portfolio with recent work",
                "Practice system design and behavioral interviews",
                "Connect with professionals in your target role",
            ],
            "resources": [],
            "difficulty": "Preparation",
        },
    ]

def _group_related_skills(prioritized: List[dict], role: str) -> List[List[dict]]:
    """Group related skills into learning chunks for coherent phases."""
    skill_clusters = get_skill_clusters()

    # Assign each skill to the best matching cluster (first match wins)
    skill_to_cluster = {}
    clustered_skill_names = set()
    
    for skill in prioritized:
        skill_lower = skill["skill"].lower()
        if skill_lower in clustered_skill_names:
            continue
        for cluster_name, cluster_skills in skill_clusters.items():
            if skill_lower in cluster_skills:
                skill_to_cluster.setdefault(cluster_name, []).append(skill)
                clustered_skill_names.add(skill_lower)
                break

    # Skills not in any cluster go to their own group
    unclustered = [s for s in prioritized if s["skill"].lower() not in clustered_skill_names]

    # Build groups: clustered skills first, then unclustered
    groups = []
    for cluster_skills in skill_to_cluster.values():
        if cluster_skills:
            groups.append(cluster_skills)

    # Add unclustered skills in small batches
    for i in range(0, len(unclustered), 2):
        batch = unclustered[i:i+2]
        groups.append(batch)

    return groups if groups else [prioritized[:3]]

def _generate_skill_actions(skill_info: dict, found_skills: List[str], role: str) -> tuple:
    """Generate specific action items and resources for a skill."""
    skill = skill_info["skill"]
    difficulty = skill_info["difficulty"]
    skill_lower = skill.lower()

    # Get actions from cache
    action_cache = get_learning_actions()

    # Get actions for this skill, or generate generic ones
    if skill_lower in action_cache:
        actions = action_cache[skill_lower]
    elif any(x in skill_lower for x in ["react", "angular", "vue", "svelte"]):
        actions = [
            f"Learn {skill} fundamentals through official documentation",
            f"Build a small project using {skill}",
            f"Practice {skill} best practices and patterns",
        ]
    elif any(x in skill_lower for x in ["django", "flask", "fastapi", "express", "spring"]):
        actions = [
            f"Learn {skill} basics: routing, middleware, templates",
            f"Build a REST API with {skill}",
            f"Practice authentication and database integration",
        ]
    elif any(x in skill_lower for x in ["docker", "kubernetes", "terraform", "ci/cd"]):
        actions = [
            f"Learn {skill} fundamentals through hands-on tutorials",
            f"Set up {skill} in a practice environment",
            f"Apply {skill} to a real project",
        ]
    else:
        actions = [
            f"Learn {skill} fundamentals through official documentation",
            f"Practice {skill} with a small hands-on project",
            f"Apply {skill} in a real-world scenario",
        ]

    # Generate resource links
    resources = _get_skill_resources(skill, role)

    return actions, resources

def _get_skill_resources(skill: str, role: str) -> List[dict]:
    """Get learning resources for a specific skill."""
    resource_cache = get_learning_resources()

    skill_lower = skill.lower()
    if skill_lower in resource_cache:
        return resource_cache[skill_lower]

    # Generic fallback based on skill type
    return [
        {"title": f"Learn {skill} - Official Documentation", "url": "#", "type": "docs"},
    ]

def _generate_phase_title(skills: List[str], phase_num: int, difficulty: str) -> str:
    """Generate a descriptive title for a roadmap phase."""
    if len(skills) == 1:
        return f"Master {skills[0]}"
    elif len(skills) <= 2:
        return f"Learn {skills[0]} & {skills[1]}"
    else:
        return f"{difficulty}: {skills[0]}, {skills[1]} & {len(skills) - 2} more"

def generate_synthetic_roadmap(target_role: str, found_skills: List[str]) -> List[dict]:
    """Generates a structured career roadmap using local logic when AI is unavailable."""
    role = target_role or "Professional"
    # Determine missing skills based on taxonomy (simplified)
    role_category = "Other Technical"
    taxonomy = get_skills_taxonomy()
    for cat, skills in taxonomy.items():
        if any(s in role.lower() for s in cat.lower().split()):
            role_category = cat
            break
    
    potential_missing = [s for s in taxonomy.get(role_category, []) if s.title() not in found_skills]
    if not potential_missing:
        potential_missing = ["Advanced Architecture", "System Design", "Leadership", "Performance Optimization"]

    return [
        {
            "step": 1,
            "title": "Closing Core Gaps",
            "duration": "4 weeks",
            "skills": potential_missing[:2],
            "action_items": [f"Complete an advanced certification in {potential_missing[0]}", "Build a small CLI tool to practice."]
        },
        {
            "step": 2,
            "title": "Applied Projects",
            "duration": "6 weeks",
            "skills": potential_missing[2:4] if len(potential_missing) > 2 else ["Project Execution"],
            "action_items": ["Integrate new skills into a full-stack portfolio project.", "Open source a component on GitHub."]
        },
        {
            "step": 3,
            "title": "Scale & Optimization",
            "duration": "3 weeks",
            "skills": ["Performance", "Security", "Testing"],
            "action_items": ["Implement unit tests and CI/CD pipelines.", "Optimize application latency."]
        },
        {
            "step": 4,
            "title": "Market Readiness",
            "duration": "2 weeks",
            "skills": ["Interviewing", "Networking"],
            "action_items": ["Update LinkedIn with new portfolio projects.", "Practice mock interviews focusing on system design."]
        }
    ]

def generate_roadmap_fallback(role: str, target_skills: List[str], current_skills: List[str]) -> List[dict]:
    """Template-based roadmap"""
    missing = target_skills[:8] if target_skills else []
    
    roadmap = [
        {
            "phase": "Foundation",
            "duration": "2-3 weeks",
            "title": f"{role} Fundamentals",
            "skills": missing[:2] if missing else ["Core concepts", "Basic tools"],
            "resources": [
                {"type": "course", "title": f"{role} Basics Course"},
                {"type": "project", "title": "Simple practice project"}
            ]
        },
        {
            "phase": "Skill Building",
            "duration": "4-6 weeks",
            "title": "Practical Experience",
            "skills": missing[2:4] if len(missing) > 2 else ["Intermediate topics", "Hands-on practice"],
            "resources": [
                {"type": "course", "title": "Intermediate Level Course"},
                {"type": "project", "title": "Portfolio Project"}
            ]
        },
        {
            "phase": "Advanced & Portfolio",
            "duration": "4-6 weeks",
            "title": "Advanced Skills & Portfolio",
            "skills": missing[4:6] if len(missing) > 4 else ["Advanced topics", "Real-world application"],
            "resources": [
                {"type": "course", "title": "Advanced Course"},
                {"type": "project", "title": "Capstone Project"}
            ]
        },
        {
            "phase": "Job Ready",
            "duration": "2-3 weeks",
            "title": "Interview Preparation",
            "skills": ["Interview techniques", "Resume optimization", "Portfolio presentation"],
            "resources": [
                {"type": "practice", "title": "Mock interviews"},
                {"type": "review", "title": "Resume review"}
            ]
        }
    ]
    
    return roadmap

def recommend_projects(target_role: str, missing_skills: List[str]) -> List[Dict[str, Any]]:
    role = target_role or "General"
    skills = missing_skills[:5] if missing_skills else ["communication", "problem-solving", "execution"]
    projects = []
    for idx, skill in enumerate(skills, start=1):
        projects.append(
            {
                "title": f"{role} Portfolio Project {idx}: {skill}",
                "objective": f"Build a portfolio-grade project that demonstrates practical {skill} use.",
                "deliverables": [
                    "Architecture/design doc",
                    "Working demo with README",
                    "Metrics/results section",
                ],
                "estimated_weeks": 2 + (idx % 2),
            }
        )
    return projects
