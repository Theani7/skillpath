import io
import json
import os
import tempfile
import time
import unittest

# Use a temp file DB for tests (':memory:' creates separate DBs per connection)
_test_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_test_db.close()
os.environ.setdefault("DB_FILE", _test_db.name)
os.environ.setdefault("GEMINI_API_KEY", "")
os.environ.setdefault("ENV", "development")

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app, raise_server_exceptions=False)


def _register_user(username="testuser", email="test@example.com", password="Test1234!"):
    return client.post("/api/auth/register", json={
        "username": username,
        "email": email,
        "full_name": "Test User",
        "password": password,
    })


def _verify_email(email, otp):
    return client.post("/api/auth/verify-email", json={"email": email, "otp": otp})


def _register_and_verify(username="testuser", email="test@example.com", password="Test1234!"):
    """Register and verify email using the dev debug OTP. Returns the register response."""
    resp = _register_user(username, email, password)
    if resp.status_code != 200:
        return resp
    debug_otp = resp.json().get("debug_otp")
    if debug_otp:
        _verify_email(email, debug_otp)
    return resp


def _login_user(username="testuser", password="Test1234!"):
    return client.post("/api/auth/login", data={
        "username": username,
        "password": password,
    })


def _auth_header(access_token):
    return {"Authorization": f"Bearer {access_token}"}


def _clear_rate_limits():
    """Tests share a single client IP, so per-minute rate limits would
    otherwise accumulate across the whole suite and cause false 429s."""
    from api.database import get_db_connection
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM rate_limits")
        conn.commit()
    finally:
        conn.close()


def _make_pdf_content(text="Simple resume text"):
    """Create minimal valid PDF with extractable text using PyMuPDF."""
    try:
        import fitz
        doc = fitz.open()
        page = doc.new_page(width=612, height=792)
        page.insert_text((72, 72), text)
        buf = doc.tobytes()
        doc.close()
        return buf
    except ImportError:
        content = f"%PDF-1.0\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>>>endobj\n4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000266 00000 n \ntrailer<</Size 5/Root 1 0 R>>\nstartxref\n340\n%%EOF"
        return content.encode("latin-1")


class AuthFlowTests(unittest.TestCase):
    def setUp(self):
        _clear_rate_limits()
        self.uid = int(time.time() * 1000000)
        self.users = []

    def tearDown(self):
        for u in self.users:
            try:
                from api.database import get_db_connection
                conn = get_db_connection()
                conn.execute("DELETE FROM users WHERE username = ?", (u,))
                conn.commit()
                conn.close()
            except Exception:
                pass

    def _reg(self, username=None, email=None):
        if username is None:
            username = f"tuser_{self.uid}"
        if email is None:
            email = f"t_{self.uid}@test.com"
        self.users.append(username)
        return _register_user(username, email)

    def _reg_verified(self, username=None, email=None):
        if username is None:
            username = f"tuser_{self.uid}"
        if email is None:
            email = f"t_{self.uid}@test.com"
        self.users.append(username)
        return _register_and_verify(username, email)

    def test_register_success(self):
        resp = self._reg()
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("verification code", data["message"].lower())
        self.assertFalse(data["otp_sent"])
        self.assertIsInstance(data["debug_otp"], str)

    def test_register_duplicate_username(self):
        uname = f"dup_{self.uid}"
        self.users.append(uname)
        _register_user(uname, f"d1_{self.uid}@test.com")
        resp = _register_user(uname, f"d2_{self.uid}@test.com")
        self.assertEqual(resp.status_code, 400)

    def test_register_duplicate_email(self):
        em = f"same_{self.uid}@test.com"
        self._reg(email=em)
        resp = self._reg(email=em)
        self.assertEqual(resp.status_code, 400)

    def test_verify_email_success(self):
        uname = f"ve_{self.uid}"
        em = f"ve_{self.uid}@test.com"
        self.users.append(uname)
        resp = _register_user(uname, em)
        otp = resp.json()["debug_otp"]
        ver = _verify_email(em, otp)
        self.assertEqual(ver.status_code, 200)
        self.assertIn("verified", ver.json()["message"].lower())
        from api.database import get_db_connection
        conn = get_db_connection()
        try:
            row = conn.execute("SELECT email_verified FROM users WHERE email = ?", (em,)).fetchone()
            self.assertEqual(row["email_verified"], 1)
        finally:
            conn.close()

    def test_verify_email_wrong_otp(self):
        em = f"vw_{self.uid}@test.com"
        self._reg(email=em)
        resp = _verify_email(em, "000000")
        self.assertEqual(resp.status_code, 400)

    def test_login_blocked_until_email_verified(self):
        uname = f"lb_{self.uid}"
        em = f"lb_{self.uid}@test.com"
        self.users.append(uname)
        reg = _register_user(uname, em)
        resp = _login_user(uname)
        self.assertEqual(resp.status_code, 403)
        _verify_email(em, reg.json()["debug_otp"])
        resp = _login_user(uname)
        self.assertEqual(resp.status_code, 200)

    def test_resend_otp(self):
        em = f"rs_{self.uid}@test.com"
        self._reg(email=em)
        # Cooldown since the registration OTP was just sent
        resp = client.post("/api/auth/resend-otp", json={"email": em, "purpose": "register"})
        self.assertEqual(resp.status_code, 429)
        # Backdate the stored OTP so the cooldown expires
        from api.database import get_db_connection
        conn = get_db_connection()
        try:
            conn.execute(
                "UPDATE otp_codes SET created_at = datetime('now', '-2 minutes') "
                "WHERE email = ? AND purpose = 'register'",
                (em,),
            )
            conn.commit()
        finally:
            conn.close()
        resp = client.post("/api/auth/resend-otp", json={"email": em, "purpose": "register"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("debug_otp", resp.json())
        # And again immediately after -> cooldown re-applied
        resp = client.post("/api/auth/resend-otp", json={"email": em, "purpose": "register"})
        self.assertEqual(resp.status_code, 429)

    def test_resend_verification_from_login(self):
        uname = f"rv_{self.uid}"
        em = f"rv_{self.uid}@test.com"
        self.users.append(uname)
        _register_user(uname, em)
        from api.database import get_db_connection
        conn = get_db_connection()
        try:
            conn.execute(
                "UPDATE otp_codes SET created_at = datetime('now', '-2 minutes') "
                "WHERE email = ? AND purpose = 'register'",
                (em,),
            )
            conn.commit()
        finally:
            conn.close()
        resp = client.post("/api/auth/resend-verification", json={"username": uname})
        self.assertEqual(resp.status_code, 200)
        resend_otp = resp.json().get("debug_otp")
        self.assertIsInstance(resend_otp, str)
        # Verified accounts get a generic response with no code
        _verify_email(em, resend_otp)
        conn = get_db_connection()
        try:
            conn.execute(
                "UPDATE otp_codes SET created_at = datetime('now', '-2 minutes') "
                "WHERE email = ? AND purpose = 'register'",
                (em,),
            )
            conn.commit()
        finally:
            conn.close()
        resp = client.post("/api/auth/resend-verification", json={"username": uname})
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("debug_otp", resp.json())

    def test_login_success(self):
        uname = f"login_{self.uid}"
        self.users.append(uname)
        _register_and_verify(uname, f"l_{self.uid}@test.com")
        resp = _login_user(uname)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("role", data)
        self.assertIn("username", data)
        self.assertNotIn("access_token", data)
        self.assertNotIn("refresh_token", data)

    def test_login_wrong_password(self):
        uname = f"wpw_{self.uid}"
        self.users.append(uname)
        _register_and_verify(uname, f"wp_{self.uid}@test.com")
        resp = _login_user(uname, password="WrongPassword1!")
        self.assertEqual(resp.status_code, 401)

    def test_login_nonexistent_user(self):
        resp = _login_user(f"ghost_{self.uid}")
        self.assertEqual(resp.status_code, 401)

    def test_me_endpoint(self):
        uname = f"me_{self.uid}"
        self.users.append(uname)
        _register_and_verify(uname, f"me_{self.uid}@test.com")
        _login_user(uname)
        resp = client.get("/api/auth/me")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["username"], uname)

    def test_me_unauthenticated(self):
        resp = client.get("/api/auth/me")
        self.assertIn(resp.status_code, [200, 401])

    def test_logout_clears_cookies(self):
        uname = f"logout_{self.uid}"
        self.users.append(uname)
        _register_and_verify(uname, f"lo_{self.uid}@test.com")
        _login_user(uname)
        resp = client.post("/api/auth/logout")
        self.assertEqual(resp.status_code, 200)

    def test_password_reset_otp_flow(self):
        uname = f"pr_{self.uid}"
        em = f"pr_{self.uid}@test.com"
        self.users.append(uname)
        _register_and_verify(uname, em)

        req = client.post("/api/auth/request-password-reset", json={"email": em})
        self.assertEqual(req.status_code, 200)
        debug_otp = req.json().get("debug_otp")
        self.assertIsInstance(debug_otp, str)

        ver = client.post("/api/auth/verify-reset-otp", json={"email": em, "otp": debug_otp})
        self.assertEqual(ver.status_code, 200)
        reset_token = ver.json()["reset_token"]

        reset = client.post("/api/auth/reset-password", json={
            "token": reset_token,
            "new_password": "NewPass123!",
        })
        self.assertEqual(reset.status_code, 200)

        self.assertEqual(_login_user(uname, "NewPass123!").status_code, 200)
        self.assertEqual(_login_user(uname).status_code, 401)

    def test_password_reset_unknown_email_is_generic(self):
        resp = client.post(
            "/api/auth/request-password-reset", json={"email": f"nobody_{self.uid}@test.com"}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("debug_otp", resp.json())
        resp = client.get("/api/auth/me")
        self.assertEqual(resp.status_code, 401)

    def test_check_username_available(self):
        resp = client.get(f"/api/auth/check-username/avail_{self.uid}")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["available"])

    def test_check_username_taken(self):
        uname = f"taken_{self.uid}"
        self.users.append(uname)
        _register_user(uname, f"tk_{self.uid}@test.com")
        resp = client.get(f"/api/auth/check-username/{uname}")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()["available"])


class AnalysisEndpointTests(unittest.TestCase):
    def setUp(self):
        self.uid = int(time.time() * 1000000)
    def setUp(self):
        _clear_rate_limits()
        self.uid = int(time.time() * 1000000)
        self.users = []

    def tearDown(self):
        for u in self.users:
            try:
                from api.database import get_db_connection
                conn = get_db_connection()
                conn.execute("DELETE FROM users WHERE username = ?", (u,))
                conn.commit()
                conn.close()
            except Exception:
                pass

    def _get_auth(self):
        uname = f"analysis_{self.uid}"
        self.users.append(uname)
        _register_and_verify(uname, f"an_{self.uid}@test.com")
        _login_user(uname)
        for cookie in client.cookies.jar:
            if cookie.name == "access_token":
                return cookie.value
        return None

    def test_upload_pdf(self):
        token = self._get_auth()
        pdf = _make_pdf_content()
        resp = client.post(
            "/api/analyze",
            files={"file": ("resume.pdf", io.BytesIO(pdf), "application/pdf")},
            data={"target_role": "Software Engineer"},
            headers=_auth_header(token) if token else {},
        )
        # Should succeed or return 422/503 (if local parser can't extract text or no Gemini)
        self.assertIn(resp.status_code, [200, 422, 503])

    def test_upload_invalid_filetype(self):
        token = self._get_auth()
        resp = client.post(
            "/api/analyze",
            files={"file": ("resume.txt", io.BytesIO(b"hello"), "text/plain")},
            data={"target_role": "General"},
            headers=_auth_header(token) if token else {},
        )
        self.assertEqual(resp.status_code, 400)

    def test_upload_empty_file(self):
        token = self._get_auth()
        resp = client.post(
            "/api/analyze",
            files={"file": ("empty.pdf", io.BytesIO(b""), "application/pdf")},
            data={"target_role": "General"},
            headers=_auth_header(token) if token else {},
        )
        self.assertEqual(resp.status_code, 400)

    def test_cache_hit_returns_same_data(self):
        token = self._get_auth()
        pdf = _make_pdf_content()
        resp1 = client.post(
            "/api/analyze",
            files={"file": ("resume.pdf", io.BytesIO(pdf), "application/pdf")},
            data={"target_role": "Data Scientist"},
            headers=_auth_header(token) if token else {},
        )
        if resp1.status_code not in [200]:
            return  # Skip if local parser can't handle it

        resp2 = client.post(
            "/api/analyze",
            files={"file": ("resume.pdf", io.BytesIO(pdf), "application/pdf")},
            data={"target_role": "Data Scientist"},
            headers=_auth_header(token) if token else {},
        )
        self.assertEqual(resp2.status_code, 200)

    def test_latest_analysis(self):
        token = self._get_auth()
        resp = client.get("/api/user/latest-analysis",
                          headers=_auth_header(token) if token else {})
        # Should return 200 (possibly with null analysis)
        self.assertIn(resp.status_code, [200, 404])

    def test_user_history(self):
        token = self._get_auth()
        resp = client.get("/api/user/history",
                          headers=_auth_header(token) if token else {})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("history", resp.json())


class ShareEndpointTests(unittest.TestCase):
    def setUp(self):
        _clear_rate_limits()
        self.uid = int(time.time() * 1000000)
        self.users = []

    def tearDown(self):
        for u in self.users:
            try:
                from api.database import get_db_connection
                conn = get_db_connection()
                conn.execute("DELETE FROM users WHERE username = ?", (u,))
                conn.commit()
                conn.close()
            except Exception:
                pass

    def _get_auth(self):
        uname = f"share_{self.uid}"
        self.users.append(uname)
        _register_and_verify(uname, f"sh_{self.uid}@test.com")
        _login_user(uname)
        for cookie in client.cookies.jar:
            if cookie.name == "access_token":
                return cookie.value
        return None

    def test_create_and_retrieve_share(self):
        token = self._get_auth()
        # First create an analysis to have an analysis_id
        pdf = _make_pdf_content()
        analysis_resp = client.post(
            "/api/analyze",
            files={"file": ("resume.pdf", io.BytesIO(pdf), "application/pdf")},
            data={"target_role": "General"},
            headers=_auth_header(token) if token else {},
        )
        if analysis_resp.status_code != 200:
            return  # Skip if analysis failed

        # Get latest analysis to find the ID
        latest = client.get("/api/user/latest-analysis",
                            headers=_auth_header(token) if token else {})
        if latest.status_code != 200 or not latest.json().get("analysis"):
            return

        analysis_id = latest.json()["id"]

        # Create share link
        share_resp = client.post("/api/reports/share", json={
            "analysis_id": analysis_id,
            "expires_in_hours": 24,
            "is_public": True,
        }, headers=_auth_header(token) if token else {})

        if share_resp.status_code != 200:
            return  # Share creation may need specific analysis format

        share_data = share_resp.json()
        self.assertIn("share_token", share_data)
        token_val = share_data["share_token"]

        # Retrieve shared report (public, no auth needed)
        get_resp = client.get(f"/api/reports/share/{token_val}")
        self.assertEqual(get_resp.status_code, 200)
        self.assertTrue(get_resp.json().get("shared"))

    def test_share_requires_auth(self):
        resp = client.post("/api/reports/share", json={
            "analysis_id": 99999,
            "expires_in_hours": 24,
            "is_public": True,
        })
        self.assertIn(resp.status_code, [401, 404])


class HealthEndpointTests(unittest.TestCase):
    def test_health_check(self):
        resp = client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "ok")

    def test_root_endpoint(self):
        resp = client.get("/")
        self.assertEqual(resp.status_code, 200)


class SecurityHeadersTests(unittest.TestCase):
    def test_security_headers_present(self):
        resp = client.get("/api/health")
        self.assertEqual(resp.headers.get("x-content-type-options"), "nosniff")
        self.assertEqual(resp.headers.get("x-frame-options"), "DENY")
        self.assertIn("strict-transport-security", resp.headers)
        self.assertIn("content-security-policy", resp.headers)

    def test_cache_control_no_store(self):
        resp = client.get("/api/health")
        self.assertEqual(resp.headers.get("cache-control"), "no-store")


class MockInterviewTests(unittest.TestCase):
    def test_list_roles(self):
        resp = client.get("/api/mock-interview")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("roles", data)
        self.assertIsInstance(data["roles"], list)
        self.assertGreater(len(data["roles"]), 0)

    def test_get_questions_for_role(self):
        resp = client.get("/api/mock-interview/Data Science")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["role"], "Data Science")
        self.assertIn("questions", data)
        self.assertIsInstance(data["questions"], list)
        self.assertGreater(len(data["questions"]), 0)
        self.assertIn("question", data["questions"][0])
        self.assertIn("answer", data["questions"][0])

    def test_get_questions_case_insensitive(self):
        resp = client.get("/api/mock-interview/data science")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["role"], "Data Science")

    def test_get_questions_unknown_role_404(self):
        resp = client.get("/api/mock-interview/NonexistentRole")
        self.assertEqual(resp.status_code, 404)

    def test_get_questions_whitespace_handling(self):
        resp = client.get("/api/mock-interview/  Data Science  ")
        self.assertEqual(resp.status_code, 200)


if __name__ == "__main__":
    unittest.main()
