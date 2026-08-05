"""Test environment isolation.

Runs before any api.* module is imported, so it must use a fresh temp
database and disable SMTP/Gemini regardless of what .env contains.
Without this, tests would run against the developer's real cv.db and
real SMTP credentials (registration would email real OTPs and never
return debug_otp, breaking the AuthFlow/AnalysisEndpoint suites).
"""
import os
import tempfile

_test_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_test_db.close()

os.environ["DB_FILE"] = _test_db.name
os.environ["SMTP_USERNAME"] = ""
os.environ["SMTP_PASSWORD"] = ""
os.environ["GEMINI_API_KEY"] = ""
os.environ["ENV"] = "development"
