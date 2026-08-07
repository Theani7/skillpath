"""Test environment isolation.

Runs before any api.* module is imported, so it must point DATABASE_URL
at a dedicated test database and disable SMTP/Gemini regardless of what
.env contains.

Requires a running PostgreSQL instance with a `skillpath_test` database:
    createdb skillpath_test
"""
import os

os.environ["DATABASE_URL"] = os.getenv(
    "TEST_DATABASE_URL", "postgresql://postgres@localhost:5432/skillpath_test"
)
os.environ["SMTP_USERNAME"] = ""
os.environ["SMTP_PASSWORD"] = ""
os.environ["GEMINI_API_KEY"] = ""
os.environ["ENV"] = "development"


# Captured OTPs so tests can verify the email flow without a real SMTP server.
_captured_otps: dict[str, str] = {}


def _mock_send_otp_email(to_email: str, otp: str, purpose: str) -> bool:
    """Store the OTP keyed by (email, purpose) so tests can retrieve it."""
    _captured_otps[f"{to_email}:{purpose}"] = otp
    return True


def get_captured_otp(email: str, purpose: str = "register"):
    return _captured_otps.get(f"{email}:{purpose}")


def clear_captured_otps():
    _captured_otps.clear()


import pytest

@pytest.fixture(autouse=True)
def _mock_smtp(monkeypatch):
    """Mock SMTP for all tests so the OTP flow works without a real mail server."""
    monkeypatch.setattr("api.routes.auth.send_otp_email", _mock_send_otp_email)
    monkeypatch.setattr("api.routes.auth.email_configured", lambda: True)
    clear_captured_otps()
    yield
    clear_captured_otps()
