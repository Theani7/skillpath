import random
from datetime import datetime

from api.seed_data import get_skill_recommendations
from api.database import get_db_connection

# Track the last time a simulation was run
last_scraped_timestamp = None

# Define some logical market shifts we can simulate
# Format: (Field, Outdated_Skill, Trending_Skill)
MARKET_SHIFTS = [
    ('Web Development', 'HTML', 'Tailwind CSS'),
    ('Web Development', 'CSS', 'Svelte'),
    ('Data Science', 'Spark', 'Generative AI'),
    ('Data Science', 'Hadoop', 'LLMOps'),
    ('Android Development', 'RxJava', 'Jetpack Compose'),
    ('IOS Development', 'Objective-C', 'SwiftUI'),
    ('DevOps', 'Jenkins', 'GitHub Actions'),
    ('Quality Assurance', 'Manual Testing', 'Cypress')
]

def simulate_trend_update():
    """
    Simulates a background web scraper identifying shifting industry trends
    and updating the skill recommendations in the database and cache.
    """
    global last_scraped_timestamp
    
    # Pick a random shift to apply
    shift = random.choice(MARKET_SHIFTS)
    field, old_skill, new_skill = shift
    
    # Check if the field exists and if the old skill is in the current recommendations
    skill_recs = get_skill_recommendations()
    if field in skill_recs:
        current_skills = skill_recs[field]
        
        # We only apply the shift if the old skill is still there and the new one isn't
        if old_skill in current_skills and new_skill not in current_skills:
            # Replace the old skill with the new one in the cache
            index = current_skills.index(old_skill)
            current_skills[index] = new_skill
            
            # Update the database
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE skill_recommendations SET skill_name = %s WHERE field_name = %s AND skill_name = %s",
                    (new_skill, field, old_skill)
                )
                conn.commit()
            finally:
                conn.close()
            
            # Print to server console for debugging
            print(f"[SIMULATED SCRAPER] Market Shift Detected!")
            print(f"[SIMULATED SCRAPER] Field: {field} | Out: '{old_skill}' -> In: '{new_skill}'")
    
    # Update timestamp
    last_scraped_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"status": "success", "message": "Trend simulation applied.", "timestamp": last_scraped_timestamp}

def get_scraper_status():
    """Returns the current status of the scraper."""
    return {
        "last_scraped": last_scraped_timestamp,
        "active_skills": get_skill_recommendations()
    }
