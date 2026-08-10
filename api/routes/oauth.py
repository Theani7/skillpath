import logging
import os
import secrets
import time
from typing import Optional
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse

from api.auth import (
    COOKIE_NAME,
    REFRESH_COOKIE_NAME,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
)
from api.database import get_db_connection
from api.security import get_password_hash

logger = logging.getLogger("resume-analyzer")

router = APIRouter(prefix="/api/auth", tags=["oauth"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/google/callback")
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

ENV = os.getenv("ENV", "development").lower()
IS_PROD = ENV in ("production", "prod")


@router.get("/google")
async def google_login():
    """Redirect user to Google OAuth consent screen."""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=503,
            detail="Google OAuth is not configured. Please contact the administrator.",
        )

    state = secrets.token_urlsafe(32)
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    response = RedirectResponse(url=auth_url)
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        secure=IS_PROD,
        samesite="lax",
        max_age=600,
        path="/",
    )
    return response


@router.get("/google/callback")
async def google_callback(request: Request, response: Response):
    """Handle Google OAuth callback, create/link account, issue JWT tokens."""
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    stored_state = request.cookies.get("oauth_state")

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    if not state or state != stored_state:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    token_data = await _exchange_code(code)
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to obtain access token from Google")

    user_info = await _get_google_user(access_token)
    email = user_info.get("email", "").lower()
    name = user_info.get("name", "")
    google_id = user_info.get("id", "")

    if not email:
        raise HTTPException(status_code=400, detail="Could not retrieve email from Google")

    user, needs_verification = _find_or_create_user(email, name, google_id)

    if needs_verification:
        link_token = secrets.token_urlsafe(32)
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO oauth_link_tokens (token, user_id, google_id, expires_at) "
                "VALUES (%s, %s, %s, %s) "
                "ON CONFLICT (token) DO UPDATE SET user_id = EXCLUDED.user_id, "
                "google_id = EXCLUDED.google_id, expires_at = EXCLUDED.expires_at",
                (link_token, user["id"], google_id, int(time.time()) + 600),
            )
            conn.commit()
        finally:
            conn.close()

        response.delete_cookie(key="oauth_state", path="/")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/verify-google-link?email={email}&link_token={link_token}",
            status_code=302,
        )

    access_jwt = create_access_token(
        data={"sub": user["username"]},
        expires_delta=__import__("datetime").timedelta(minutes=30),
    )
    refresh_jwt = create_refresh_token(data={"sub": user["username"]})
    refresh_payload = decode_token(refresh_jwt)
    token_hash = hash_token(refresh_jwt)

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO refresh_tokens(token, user_id, expires_at) VALUES (%s, %s, %s)",
            (token_hash, user["id"], int(refresh_payload["exp"])),
        )
        conn.commit()
    finally:
        conn.close()

    response.delete_cookie(key="oauth_state", path="/")

    token_params = f"?oauth_token={access_jwt}&oauth_refresh={refresh_jwt}"
    return RedirectResponse(url=f"{FRONTEND_URL}/app{token_params}", status_code=302)


async def _exchange_code(code: str) -> dict:
    """Exchange authorization code for access token."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
    if resp.status_code != 200:
        logger.error(f"Google token exchange failed: {resp.text}")
        raise HTTPException(status_code=400, detail="Failed to exchange authorization code")
    return resp.json()


async def _get_google_user(access_token: str) -> dict:
    """Fetch user info from Google."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
    if resp.status_code != 200:
        logger.error(f"Google userinfo failed: {resp.text}")
        raise HTTPException(status_code=400, detail="Failed to fetch user info from Google")
    return resp.json()


def _find_or_create_user(email: str, name: str, google_id: str) -> tuple[dict, bool]:
    """Find existing user by email or Google ID, or create a new one.

    Returns:
        tuple of (user_dict, needs_password_verification)
        needs_password_verification is True when an existing password-based
        account was found and Google needs to be linked after verification.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            user_dict = dict(user)
            existing_google_id = user_dict.get("google_id")

            if existing_google_id == google_id:
                return user_dict, False

            if existing_google_id and existing_google_id != google_id:
                raise HTTPException(
                    status_code=409,
                    detail="This email is linked to a different Google account. Please sign in with your password instead.",
                )

            if not existing_google_id:
                return user_dict, True

        base_username = email.split("@")[0].lower()
        username = base_username
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            username = f"{base_username}_{secrets.token_hex(3)}"
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                username = f"{base_username}_{int(time.time())}"

        full_name = name or username
        random_password = secrets.token_urlsafe(32)

        cursor.execute(
            "INSERT INTO users (username, email, full_name, hashed_password, role, email_verified, google_id) "
            "VALUES (%s, %s, %s, %s, 'user', 1, %s)",
            (username, email, full_name, get_password_hash(random_password), google_id),
        )
        conn.commit()

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        new_user = cursor.fetchone()
        return dict(new_user), False
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OAuth user creation error: {e}")
        conn.rollback()
        raise HTTPException(status_code=500, detail="Failed to create user account")
    finally:
        conn.close()
