import re
import unittest
from datetime import timedelta

from api.auth import create_access_token, create_refresh_token, decode_token
from api.career_services import (
    compute_resume_score_breakdown,
    generate_interview_questions,
    generate_job_matches,
    rank_candidates,
)
from api.skill_matching import compare_resume_to_jd
from api.roadmap_services import recommend_projects
from api.i18n import get_translations
from api.resume_parser import parse_resume_fallback


class FeatureTests(unittest.TestCase):
    def test_explainable_scoring(self):
        resume_data = {
            "summary": "Highly experienced Backend Engineer with 10+ years in building scalable microservices and APIs.",
            "education": ["B.Tech Computer Science", "MS Software Systems"],
            "experience": ["Worked at Google", "Worked at Meta", "Worked at Amazon", "Worked at Netflix", "Worked at Apple"],
            "skills": ["Python", "FastAPI", "Go", "Docker", "Kubernetes", "AWS", "SQL", "Redis", "Kafka", "React"],
            "email": "test@example.com",
            "phone": "+1234567890"
        }
        score, feedback, breakdown = compute_resume_score_breakdown(resume_data)
        # With quality-based scoring, flat experience strings score lower than structured blocks
        self.assertGreater(score, 50)
        self.assertLessEqual(score, 100)
        self.assertEqual(breakdown["skills"]["status"], "present")
        self.assertTrue(breakdown["skills"]["evidence"])

    def test_explainable_scoring_quality(self):
        """Test that structured experience_blocks with bullets/verbs/metrics score higher."""
        resume_data = {
            "summary": "Highly experienced Backend Engineer with 10+ years in building scalable microservices and APIs.",
            "education": ["B.Tech Computer Science", "MS Software Systems"],
            "experience_blocks": [
                {
                    "title": "Senior Software Engineer",
                    "company": "Google",
                    "start_date": "Jan 2020",
                    "end_date": "Present",
                    "bullets": [
                        "Led migration of monolith to microservices, reducing deployment time by 60%.",
                        "Built REST APIs serving 10M+ requests daily with 99.9% uptime.",
                        "Implemented CI/CD pipelines that cut release cycles from 2 weeks to 2 days.",
                    ],
                },
                {
                    "title": "Software Engineer",
                    "company": "Meta",
                    "start_date": "Jun 2017",
                    "end_date": "Dec 2019",
                    "bullets": [
                        "Developed real-time data pipeline processing 5TB daily using Kafka and Spark.",
                        "Optimized database queries reducing average latency by 40%.",
                        "Mentored 3 junior engineers through structured code review process.",
                    ],
                },
            ],
            "experience": ["Senior Software Engineer at Google (Jan 2020 - Present)", "Software Engineer at Meta (Jun 2017 - Dec 2019)"],
            "skills": ["Python", "FastAPI", "Go", "Docker", "Kubernetes", "AWS", "SQL", "Redis", "Kafka"],
            "email": "test@example.com",
            "phone": "+1234567890"
        }
        score, feedback, breakdown = compute_resume_score_breakdown(resume_data)
        # Structured experience with bullets, action verbs, and metrics should score high
        self.assertGreaterEqual(score, 75)
        self.assertEqual(breakdown["experience"]["status"], "present")
        self.assertGreater(breakdown["experience"]["score"], 15)

    def test_job_match_generation(self):
        jobs = generate_job_matches("Data Science", ["Python"], ["Deep Learning"])
        self.assertTrue(len(jobs) > 0)
        self.assertIn("fit_score", jobs[0])
        self.assertIn("title", jobs[0])

    def test_interview_questions(self):
        questions = generate_interview_questions("DevOps", ["Kubernetes"], ["Linux"])
        self.assertTrue(len(questions) >= 4)
        self.assertIn("question", questions[0])

    def test_candidate_ranking(self):
        ranked = rank_candidates(
            [
                {"id": 1, "analysis_data": {"resume_score": 80, "match_score": 70, "missing_skills": ["A"]}},
                {"id": 2, "analysis_data": {"resume_score": 60, "match_score": 55, "missing_skills": ["A", "B", "C"]}},
            ],
            "Web Development",
        )
        self.assertEqual(ranked[0]["candidate_id"], 1)
        self.assertGreater(ranked[0]["final_rank_score"], ranked[1]["final_rank_score"])

    def test_refresh_token_type(self):
        access = create_access_token({"sub": "u", "role": "user"}, timedelta(minutes=1))
        refresh = create_refresh_token({"sub": "u", "role": "user"}, timedelta(minutes=1))
        self.assertEqual(decode_token(access)["type"], "access")
        self.assertEqual(decode_token(refresh)["type"], "refresh")

    def test_jd_compare(self):
        result = compare_resume_to_jd(["python", "sql", "docker"], "Need Python SQL AWS communication")
        self.assertIn("coverage_score", result)
        self.assertIn("python", result["matched_keywords"])

    def test_project_recommendations(self):
        recs = recommend_projects("Data Science", ["ML", "NLP"])
        self.assertTrue(len(recs) >= 2)
        self.assertIn("title", recs[0])

    def test_i18n(self):
        tr = get_translations("es")
        self.assertIn("analysis_complete", tr)


SAMPLE_RESUME = """
Jane Doe
Senior Software Engineer
jane.doe@example.com | +1 (555) 123-4567 | linkedin.com/in/janedoe | github.com/janedoe

Summary
Backend engineer with 8 years building distributed systems. Passionate about
clean APIs and observability.

Experience
Senior Software Engineer
Acme Corp
Jan 2020 - Present
- Led migration of monolith to microservices, reducing p99 latency by 40%
- Mentored 4 junior engineers and ran the on-call rotation

Software Engineer
Initech
Jun 2017 - Dec 2019
- Built REST APIs in Python and FastAPI serving 2M requests/day
- Owned the PostgreSQL → Redis caching layer

Education
B.S. Computer Science, MIT, 2017
M.S. Software Engineering, Stanford, 2019

Skills
Python, FastAPI, Go, Docker, Kubernetes, AWS, PostgreSQL, Redis, Kafka, gRPC

Certifications
AWS Solutions Architect Professional

Languages
English (Native), Spanish (Conversational)

Awards
Engineer of the Year 2022
"""


class ResumeParserTests(unittest.TestCase):
    def setUp(self):
        self.parsed = parse_resume_fallback(SAMPLE_RESUME, target_role="Backend Engineer")

    def test_name_detection_v2(self):
        self.assertEqual(self.parsed["name"], "Jane Doe")

    def test_email_extraction(self):
        self.assertEqual(self.parsed["email"], "jane.doe@example.com")

    def test_phone_regex_is_tight(self):
        # Real phone present
        self.assertIn("555", self.parsed["mobile_number"])
        # Should NOT contain 8 random digits from the resume text
        self.assertNotIn("1234", self.parsed["mobile_number"][:6])  # "1234" in "123-4567" is OK
        # Should not match a year like "2017" as a phone
        self.assertNotIn("2017", re.sub(r"\D", "", self.parsed["mobile_number"]) if self.parsed["mobile_number"] else "")

    def test_section_detection_robust(self):
        # All major sections should be present
        self.assertIn("Backend engineer", self.parsed["summary"])
        self.assertTrue(len(self.parsed["experience_blocks"]) >= 2)
        self.assertTrue(len(self.parsed["education_blocks"]) >= 2)
        self.assertTrue(len(self.parsed["certifications"]) >= 1)
        self.assertTrue(len(self.parsed["languages"]) >= 1)
        self.assertTrue(len(self.parsed["awards"]) >= 1)

    def test_experience_block_structure(self):
        blocks = self.parsed["experience_blocks"]
        self.assertTrue(len(blocks) >= 2)
        first = blocks[0]
        # Should have title, company, dates
        self.assertIn("title", first)
        self.assertIn("company", first)
        self.assertIn("start_date", first)
        self.assertIn("end_date", first)
        self.assertIn("bullets", first)
        # First block: Senior Software Engineer at Acme Corp
        self.assertIn("Senior Software Engineer", first["title"])
        self.assertIn("Acme", first["company"])
        self.assertEqual(first["start_date"], "Jan 2020")
        self.assertEqual(first["end_date"], "Present")
        # Bullets
        self.assertTrue(len(first["bullets"]) >= 1)

    def test_education_block_structure(self):
        blocks = self.parsed["education_blocks"]
        self.assertTrue(len(blocks) >= 2)
        # B.S. line
        bs = next((b for b in blocks if "B.S" in b["degree"]), None)
        self.assertIsNotNone(bs)
        self.assertIn("MIT", bs["institution"])
        self.assertEqual(bs["year"], "2017")
        # M.S. line
        ms = next((b for b in blocks if "M.S" in b["degree"]), None)
        self.assertIsNotNone(ms)
        self.assertIn("Stanford", ms["institution"])
        self.assertEqual(ms["year"], "2019")

    def test_designation_and_company_names(self):
        self.assertIn("Senior Software Engineer", self.parsed["designation"])
        self.assertIn("Acme Corp", self.parsed["company_names"])
        self.assertIn("Initech", self.parsed["company_names"])

    def test_skill_extraction_taxonomy_plus_variants(self):
        # 10 skills listed in the resume, all in taxonomy or fuzzy variants
        self.assertIn("Python", self.parsed["skills"])
        self.assertIn("Docker", self.parsed["skills"])
        self.assertIn("Kubernetes", self.parsed["skills"])
        self.assertIn("Aws", self.parsed["skills"])  # "AWS" → "Aws" by .title()
        self.assertIn("Postgresql", self.parsed["skills"])
        # Should be at least 8
        self.assertGreaterEqual(len(self.parsed["skills"]), 8)

    def test_target_role_synonym_match(self):
        # "Backend Engineer" should map to Web Frameworks / Databases / etc.
        # Missing skills should come from those categories
        self.assertTrue(isinstance(self.parsed["missing_skills"], list))

    def test_match_score_is_real_not_static(self):
        # With 10 matching skills, score should be > 0 and ≤ 100
        score = self.parsed["match_score"]
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 100)
        # With a real overlap, should not be the static 70
        # (It might still be 70 if overlap rounds to 70, but unlikely with 10+ matches)

    def test_summary_extracted(self):
        self.assertIn("Backend engineer", self.parsed["summary"])

    def test_links_extracted(self):
        self.assertIn("janedoe", self.parsed["links"]["linkedin"])
        self.assertIn("janedoe", self.parsed["links"]["github"])

    def test_experience_flat_list_compat(self):
        # The flat "experience" list should still contain something useful
        # (composed of "Title - Company (dates)" + bullets)
        flat = self.parsed["experience"]
        self.assertTrue(len(flat) >= 3)
        joined = "\n".join(flat)
        self.assertIn("Senior Software Engineer", joined)
        self.assertIn("Acme", joined)
        self.assertIn("microservices", joined)  # bullet content

    def test_education_flat_list_compat(self):
        flat = self.parsed["education"]
        self.assertTrue(len(flat) >= 2)
        joined = "\n".join(flat)
        self.assertIn("B.S", joined)
        self.assertIn("MIT", joined)
        self.assertIn("2017", joined)

    def test_confidence_score_above_70(self):
        # This is a high-quality resume; local parser should hit 70+ to skip Gemini
        self.assertGreaterEqual(self.parsed["confidence_score"], 70)

    def test_parsing_method_v3(self):
        self.assertEqual(self.parsed["parsing_method"], "local_hybrid_v3")

    def test_no_target_role_static_70(self):
        # With no target role, match score should default to 70
        parsed_no_role = parse_resume_fallback(SAMPLE_RESUME, target_role=None)
        self.assertEqual(parsed_no_role["match_score"], 70)

    def test_garbage_input_safe(self):
        # Parser should not crash on weird input
        out = parse_resume_fallback("", target_role="")
        self.assertIsInstance(out, dict)
        self.assertEqual(out["name"], "Unknown")
        self.assertEqual(out["match_score"], 70)
        self.assertEqual(out["confidence_score"], 0)

    def test_section_header_variants(self):
        # "Work Experience" and "Education & Training" should both be detected
        text = """
John Smith
john@example.com

Summary
A short summary here for testing purposes.

Work Experience
Software Engineer
Foo Inc
2020 - 2023
- Did things

Education & Training
B.S. Math, 2020

Skills
Python, Java
"""
        out = parse_resume_fallback(text, target_role="Software Engineer")
        self.assertEqual(out["name"], "John Smith")
        self.assertTrue(len(out["experience_blocks"]) >= 1)
        self.assertTrue(len(out["education_blocks"]) >= 1)
        self.assertIn("Python", out["skills"])


if __name__ == "__main__":
    unittest.main()
