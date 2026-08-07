import hashlib
import json
import logging
import os
import random
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field

from api.auth import (
    COOKIE_NAME,
    REFRESH_COOKIE_NAME,
    client_ip,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    get_current_user_from_cookie,
    hash_token,
)
from api.database import get_db_connection
from api.email_service import email_configured, send_otp_email
from api.security import get_password_hash, verify_password

logger = logging.getLogger("resume-analyzer")

router = APIRouter(prefix="/api/auth", tags=["auth"])

MAX_LOGIN_ATTEMPTS = 5

OTP_LENGTH = 6
OTP_TTL_SECONDS = 10 * 60
OTP_MAX_ATTEMPTS = 5
RESET_TOKEN_TTL_SECONDS = 10 * 60

ENV = os.getenv("ENV", "development").lower()
IS_PROD = ENV in ("production", "prod")

# In development, rate limits are relaxed so local testing isn't annoying.
# In production, these values are enforced strictly.
LOGIN_LOCKOUT_MINUTES = 1 if IS_PROD else 0
AUTH_RATE_LIMIT_PER_MINUTE = 20 if IS_PROD else 1000
OTP_RESEND_COOLDOWN_SECONDS = 60 if IS_PROD else 5


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[A-Za-z0-9_.-]+$')
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(default="", max_length=100)


class RefreshTokenRequest(BaseModel):
    refresh_token: Optional[str] = None


def _check_strict_rate_limit(key: str, limit: int = AUTH_RATE_LIMIT_PER_MINUTE):
    """Per-endpoint rate limit (stricter than global). Raises 429 if exceeded."""
    now_minute = int(time.time() // 60)
    bucket = f"{key}:{now_minute}"
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO rate_limits (key, count, updated_at) VALUES (%s, 1, %s) "
            "ON CONFLICT (key) DO UPDATE SET count = rate_limits.count + 1, updated_at = %s",
            (bucket, now_minute, now_minute),
        )
        cursor.execute("SELECT count FROM rate_limits WHERE key = %s", (bucket,))
        row = cursor.fetchone()
        count = row["count"] if row else 1
        conn.commit()
        if count > limit:
            raise HTTPException(status_code=429, detail="Too many requests. Try again in a minute.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth rate limit error: {e}")
        conn.rollback()
    finally:
        conn.close()


async def _extract_refresh_from_request(request: Request) -> Optional[str]:
    try:
        body = await request.body()
        if body:
            data = json.loads(body)
            return data.get("refresh_token")
    except Exception:
        pass
    return None


def _generate_otp() -> str:
    return f"{random.SystemRandom().randint(0, 10 ** OTP_LENGTH - 1):0{OTP_LENGTH}d}"


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def _send_otp(email: str, otp: str, purpose: str) -> dict:
    """Send an OTP email. Returns {'otp_sent': bool}.

    If SMTP is not configured or delivery fails, returns {'otp_sent': False}.
    Callers surface this as HTTP 503.
    """
    if email_configured():
        sent = send_otp_email(email, otp, purpose)
        if sent:
            return {"otp_sent": True}
        logger.error("Failed to send %s OTP email to %s", purpose, email)
    else:
        logger.warning(
            "SMTP not configured – %s OTP for %s could not be sent.",
            purpose, email,
        )
    return {"otp_sent": False}


def _store_otp(cursor, conn, email: str, purpose: str, otp: str) -> None:
    cursor.execute(
        "INSERT INTO otp_codes (email, purpose, code_hash, expires_at) VALUES (%s, %s, %s, %s)",
        (email, purpose, _hash_code(otp), int(time.time()) + OTP_TTL_SECONDS),
    )
    conn.commit()


def _consume_otp(email: str, purpose: str, otp: str) -> Optional[int]:
    """Validate an OTP. Returns the user id on success, None otherwise.

    Tracks failed attempts and marks the code used on success.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM otp_codes WHERE expires_at < %s",
            (int(time.time()),),
        )
        conn.commit()
        cursor.execute(
            "SELECT id, code_hash, attempts FROM otp_codes "
            "WHERE email = %s AND purpose = %s AND used = 0 "
            "ORDER BY id DESC LIMIT 1",
            (email, purpose),
        )
        row = cursor.fetchone()
        if not row:
            return None
        if int(row["attempts"]) >= OTP_MAX_ATTEMPTS:
            cursor.execute("UPDATE otp_codes SET used = 1 WHERE id = %s", (row["id"],))
            conn.commit()
            return None
        if _hash_code(otp) != row["code_hash"]:
            cursor.execute(
                "UPDATE otp_codes SET attempts = attempts + 1 WHERE id = %s",
                (row["id"],),
            )
            conn.commit()
            return None
        cursor.execute("UPDATE otp_codes SET used = 1 WHERE id = %s", (row["id"],))
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user_row = cursor.fetchone()
        user_id = user_row["id"] if user_row else None
        conn.commit()
        return user_id
    finally:
        conn.close()


class EmailOnlyRequest(BaseModel):
    email: EmailStr


class EmailOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=OTP_LENGTH, max_length=OTP_LENGTH, pattern=r'^\d+$')


class ResendOTPRequest(BaseModel):
    email: EmailStr
    purpose: str = Field(default="register", pattern=r'^(register|password_reset)$')


class ResendVerificationRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[A-Za-z0-9_.-]+$')


@router.post("/resend-verification")
def resend_verification(payload: ResendVerificationRequest, request: Request):
    """Resend the registration OTP for an unverified account (from the login screen)."""
    _check_strict_rate_limit(f"resend-verif:{client_ip(request)}")
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, email, email_verified FROM users WHERE username = %s",
            (payload.username,),
        )
        user = cursor.fetchone()
        if not user or int(user["email_verified"]) == 1:
            return {"status": "success", "message": "If your account needs verification, a new code has been sent."}
        email = user["email"]
        cursor.execute(
            "SELECT created_at FROM otp_codes WHERE email = %s AND purpose = 'register' "
            "ORDER BY id DESC LIMIT 1",
            (email,),
        )
        last = cursor.fetchone()
        if last:
            try:
                last_dt = datetime.fromisoformat(
                    str(last["created_at"]).replace(" ", "T")
                ).replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                last_dt = None
            if last_dt and (datetime.now(timezone.utc) - last_dt).total_seconds() < OTP_RESEND_COOLDOWN_SECONDS:
                remaining = max(1, int(OTP_RESEND_COOLDOWN_SECONDS - (datetime.now(timezone.utc) - last_dt).total_seconds()))
                raise HTTPException(
                    status_code=429,
                    detail=f"Please wait {remaining} seconds before requesting a new code.",
                )
    finally:
        conn.close()

    otp = _generate_otp()
    delivery = _send_otp(email, otp, "register")
    if not delivery["otp_sent"]:
        raise HTTPException(
            status_code=503,
            detail="Unable to send the verification email. Please try again later.",
        )
    conn = get_db_connection()
    try:
        _store_otp(conn.cursor(), conn, email, "register", otp)
    finally:
        conn.close()
    return {"status": "success", "message": "If your account needs verification, a new code has been sent."}


@router.get("/check-username/{username}")
def check_username(username: str, request: Request):
    _check_strict_rate_limit(f"username-check:{client_ip(request)}")
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        exists = cursor.fetchone() is not None
    finally:
        conn.close()
    return {"available": not exists}


@router.post("/register")
def register_user(user: UserRegister, request: Request):
    _check_strict_rate_limit(f"register:{client_ip(request)}")
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Check if username exists
        cursor.execute("SELECT * FROM users WHERE username = %s", (user.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already registered")

        # Check if email exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")

        # Generate and deliver the verification OTP before creating the account
        # so a broken email service never leaves orphan accounts behind.
        otp = _generate_otp()
        delivery = _send_otp(user.email, otp, "register")
        if not delivery["otp_sent"]:
            raise HTTPException(
                status_code=503,
                detail="Unable to send the verification email. Please try again later.",
            )

        hashed_password = get_password_hash(user.password)
        cursor.execute(
            "INSERT INTO users (username, email, full_name, hashed_password, role, email_verified) "
            "VALUES (%s, %s, %s, %s, 'user', 0)",
            (user.username, user.email, user.full_name, hashed_password)
        )
        _store_otp(cursor, conn, user.email, "register", otp)
        return {
            "message": "Registration successful. Check your email for the verification code.",
            "otp_sent": delivery["otp_sent"],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration DB error for {user.username}: {e}")
        raise HTTPException(status_code=500, detail="Database Error")
    finally:
        conn.close()


@router.post("/verify-email")
def verify_email(payload: EmailOTPRequest, request: Request):
    _check_strict_rate_limit(f"verify-email:{client_ip(request)}")
    user_id = _consume_otp(payload.email, "register", payload.otp)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET email_verified = 1 WHERE id = %s", (user_id,))
        conn.commit()
    finally:
        conn.close()
    return {"status": "success", "message": "Email verified successfully. You can now sign in."}


@router.post("/resend-otp")
def resend_otp(payload: ResendOTPRequest, request: Request):
    _check_strict_rate_limit(f"resend-otp:{client_ip(request)}")
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT created_at FROM otp_codes "
            "WHERE email = %s AND purpose = %s ORDER BY id DESC LIMIT 1",
            (payload.email, payload.purpose),
        )
        last = cursor.fetchone()
        if last:
            try:
                last_dt = datetime.fromisoformat(
                    str(last["created_at"]).replace(" ", "T")
                ).replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                last_dt = None
            if last_dt and (datetime.now(timezone.utc) - last_dt).total_seconds() < OTP_RESEND_COOLDOWN_SECONDS:
                remaining = max(1, int(OTP_RESEND_COOLDOWN_SECONDS - (datetime.now(timezone.utc) - last_dt).total_seconds()))
                raise HTTPException(
                    status_code=429,
                    detail=f"Please wait {remaining} seconds before requesting a new code.",
                )
        if payload.purpose == "register":
            cursor.execute("SELECT id FROM users WHERE email = %s AND email_verified = 0", (payload.email,))
        else:
            cursor.execute("SELECT id FROM users WHERE email = %s", (payload.email,))
        user_row = cursor.fetchone()
        if not user_row:
            raise HTTPException(status_code=404, detail="No pending verification found for this email")
    finally:
        conn.close()

    otp = _generate_otp()
    delivery = _send_otp(payload.email, otp, payload.purpose)
    if not delivery["otp_sent"]:
        raise HTTPException(
            status_code=503,
            detail="Unable to send the verification email. Please try again later.",
        )

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        _store_otp(cursor, conn, payload.email, payload.purpose, otp)
    finally:
        conn.close()
    return {
        "message": "A new verification code has been sent.",
        "otp_sent": delivery["otp_sent"],
    }


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), response: Response = None, request: Request = None):
    _check_strict_rate_limit(f"login:{client_ip(request) if request else 'unknown'}")
    username = form_data.username
    now = int(time.time())

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Accept both username and email for login
        is_email = "@" in username
        if is_email:
            cursor.execute("SELECT * FROM users WHERE email = %s", (username,))
        else:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        # Check for existing lockout (by username, since that's what we track)
        login_key = user["username"] if user else username
        cursor.execute("SELECT * FROM login_attempts WHERE username = %s", (login_key,))
        attempt_row = cursor.fetchone()

        if attempt_row:
            if attempt_row["locked_until"] and now < attempt_row["locked_until"]:
                remaining = int(attempt_row["locked_until"] - now)
                conn.close()
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many failed attempts. Try again in {remaining} seconds."
                )

        if not user or not verify_password(form_data.password, user["hashed_password"]):
            # Increment failed attempts
            if attempt_row:
                attempts = attempt_row["attempts"] + 1
                locked_until = now + (LOGIN_LOCKOUT_MINUTES * 60) if attempts >= MAX_LOGIN_ATTEMPTS else 0
                cursor.execute(
                    "UPDATE login_attempts SET attempts = %s, locked_until = %s WHERE username = %s",
                    (attempts, locked_until, login_key)
                )
            else:
                cursor.execute(
                    "INSERT INTO login_attempts (username, attempts, first_attempt, locked_until) VALUES (%s, %s, %s, %s)",
                    (login_key, 1, now, 0)
                )
            conn.commit()
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_dict = dict(user)

        if "email_verified" in user_dict and user_dict["email_verified"] == 0:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email address first. Check your inbox for the verification code.",
            )

        if "is_active" in user_dict and user_dict["is_active"] == 0:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account has been deactivated. Contact an administrator.",
            )

        cursor.execute("DELETE FROM login_attempts WHERE username = %s", (username,))
        cursor.execute("DELETE FROM refresh_tokens WHERE user_id = %s", (user_dict["id"],))
        conn.commit()

        access_token = create_access_token(
            data={"sub": user_dict["username"]}, expires_delta=timedelta(minutes=30)
        )
        refresh_token = create_refresh_token(data={"sub": user_dict["username"]})
        refresh_payload = decode_token(refresh_token)
        token_hash = hash_token(refresh_token)
        cursor.execute(
            "INSERT INTO refresh_tokens(token, user_id, expires_at) VALUES (%s, %s, %s)",
            (token_hash, user_dict["id"], int(refresh_payload["exp"])),
        )
        conn.commit()
    finally:
        conn.close()

    # Use a less restrictive SameSite policy for development environments to allow
    # the frontend (running on a different port) to receive the auth cookies.
    # In production the Secure flag will enforce HTTPS and SameSite=Strict remains safe.
    same_site_policy = "lax" if not IS_PROD else "strict"
    response.set_cookie(
        key=COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=IS_PROD,
        samesite=same_site_policy,
        max_age=60 * 30,
        path="/",
    )
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=IS_PROD,
        samesite=same_site_policy,
        max_age=60 * 60 * 24 * 30,
        path="/api/auth",
    )

    return {
        "role": user_dict["role"],
        "full_name": user_dict.get("full_name", user_dict["username"]),
        "username": user_dict["username"]
    }


@router.post("/logout")
async def logout(request: Request, response: Response):
    refresh = request.cookies.get(REFRESH_COOKIE_NAME)
    if not refresh:
        refresh = await _extract_refresh_from_request(request)
    if refresh:
        try:
            decoded = decode_token(refresh)
            username = decoded.get("sub")
        except Exception:
            username = None
        if username:
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM refresh_tokens WHERE token = %s AND user_id = (SELECT id FROM users WHERE username = %s)",
                               (hash_token(refresh), username))
                conn.commit()
            except Exception as logout_err:
                logger.error(f"Logout DB error for {username}: {logout_err}")
            finally:
                conn.close()
    response.delete_cookie(key=COOKIE_NAME, path="/")
    response.delete_cookie(key=REFRESH_COOKIE_NAME, path="/api/auth")
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user_info(request: Request):
    try:
        user = await get_current_user_from_cookie(request)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {
        "username": user["username"],
        "role": user["role"],
        "full_name": user.get("full_name", user["username"]),
        "email": user.get("email"),
    }


@router.post("/refresh")
def refresh_access_token(request: Request, payload: RefreshTokenRequest, response: Response = None):
    refresh_token = payload.refresh_token or request.cookies.get(REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    try:
        decoded = decode_token(refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    token_hash = hash_token(refresh_token)
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, expires_at FROM refresh_tokens WHERE token = %s",
            (token_hash,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Refresh token not recognized")
        if int(row["expires_at"]) < int(time.time()):
            cursor.execute("DELETE FROM refresh_tokens WHERE token = %s", (token_hash,))
            conn.commit()
            raise HTTPException(status_code=401, detail="Refresh token expired")

        new_access_token = create_access_token(
            data={"sub": decoded.get("sub")},
            expires_delta=timedelta(minutes=30),
        )
        new_refresh_token = create_refresh_token(data={"sub": decoded.get("sub")})
        new_payload = decode_token(new_refresh_token)
        cursor.execute("DELETE FROM refresh_tokens WHERE token = %s", (token_hash,))
        cursor.execute(
            "INSERT INTO refresh_tokens(token, user_id, expires_at) VALUES (%s, %s, %s)",
            (hash_token(new_refresh_token), row["user_id"], int(new_payload["exp"])),
        )
        conn.commit()
        # Look up the user's role for the response
        cursor.execute("SELECT role FROM users WHERE id = %s", (row["user_id"],))
        user_row = cursor.fetchone()
        user_role = user_row["role"] if user_row else "user"
    finally:
        conn.close()

    if response:
        response.set_cookie(
            key=COOKIE_NAME,
            value=new_access_token,
            httponly=True,
            secure=IS_PROD,
            samesite="strict",
            max_age=60 * 30,
            path="/",
        )
        response.set_cookie(
            key=REFRESH_COOKIE_NAME,
            value=new_refresh_token,
            httponly=True,
            secure=IS_PROD,
            samesite="strict",
            max_age=60 * 60 * 24 * 30,
            path="/api/auth",
        )

    return {"token_type": "bearer", "role": user_role}


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str = Field(..., max_length=200)
    new_password: str = Field(..., min_length=8, max_length=128)


class ChangePassword(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)


RESET_COOLDOWN_SECONDS = 5 * 60


@router.post("/request-password-reset")
def request_password_reset(payload: PasswordResetRequest, request: Request):
    _check_strict_rate_limit(f"pwd-reset:{client_ip(request)}")
    debug_otp = None
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (payload.email,))
        user = cursor.fetchone()
        if user:
            cursor.execute(
                "SELECT created_at FROM otp_codes WHERE email = %s AND purpose = 'password_reset' "
                "ORDER BY id DESC LIMIT 1",
                (payload.email,),
            )
            last = cursor.fetchone()
            if last:
                try:
                    last_dt = datetime.fromisoformat(
                        str(last["created_at"]).replace(" ", "T")
                    ).replace(tzinfo=timezone.utc)
                except (ValueError, TypeError):
                    last_dt = None
                if last_dt and (datetime.now(timezone.utc) - last_dt).total_seconds() < RESET_COOLDOWN_SECONDS:
                    return {"status": "success", "message": "If the email exists, a reset code has been sent."}
            otp = _generate_otp()
            delivery = _send_otp(payload.email, otp, "password_reset")
            if not delivery["otp_sent"]:
                raise HTTPException(
                    status_code=503,
                    detail="Unable to send the reset email. Please try again later.",
                )
            _store_otp(cursor, conn, payload.email, "password_reset", otp)
    finally:
        conn.close()
    return {"status": "success", "message": "If the email exists, a reset code has been sent."}


class VerifyResetOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=OTP_LENGTH, max_length=OTP_LENGTH, pattern=r'^\d+$')


@router.post("/verify-reset-otp")
def verify_reset_otp(payload: VerifyResetOTPRequest, request: Request):
    _check_strict_rate_limit(f"verify-reset-otp:{client_ip(request)}")
    user_id = _consume_otp(payload.email, "password_reset", payload.otp)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")

    reset_token = secrets.token_urlsafe(32)
    expires_at = int(time.time()) + RESET_TOKEN_TTL_SECONDS
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO password_reset_tokens(token, user_id, expires_at, used) VALUES (%s, %s, %s, 0) "
            "ON CONFLICT (token) DO UPDATE SET user_id = EXCLUDED.user_id, expires_at = EXCLUDED.expires_at, used = 0",
            (reset_token, user_id, expires_at),
        )
        conn.commit()
    finally:
        conn.close()
    return {
        "status": "success",
        "message": "Code verified. Set your new password.",
        "reset_token": reset_token,
    }


@router.post("/reset-password")
def reset_password(payload: PasswordResetConfirm):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT token, user_id, expires_at, used FROM password_reset_tokens WHERE token = %s",
            (payload.token,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=400, detail="Invalid token")
        if int(row["used"]) == 1 or int(row["expires_at"]) < int(time.time()):
            raise HTTPException(status_code=400, detail="Token expired or already used")

        cursor.execute(
            "UPDATE users SET hashed_password = %s WHERE id = %s",
            (get_password_hash(payload.new_password), row["user_id"]),
        )
        cursor.execute("UPDATE password_reset_tokens SET used = 1 WHERE token = %s", (payload.token,))
        cursor.execute("DELETE FROM refresh_tokens WHERE user_id = %s", (row["user_id"],))
        conn.commit()
    finally:
        conn.close()
    return {"status": "success", "message": "Password reset successful"}


@router.post("/change-password")
def change_password(payload: ChangePassword, request: Request, current_user: dict = Depends(get_current_user)):
    _check_strict_rate_limit(f"change-pwd:{client_ip(request)}")

    if payload.current_password == payload.new_password:
        raise HTTPException(status_code=400, detail="New password must be different from current password")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT hashed_password FROM users WHERE id = %s", (current_user["id"],))
        row = cursor.fetchone()
        if not row or not verify_password(payload.current_password, row["hashed_password"]):
            raise HTTPException(status_code=401, detail="Current password is incorrect")

        cursor.execute(
            "UPDATE users SET hashed_password = %s WHERE id = %s",
            (get_password_hash(payload.new_password), current_user["id"]),
        )
        cursor.execute("DELETE FROM refresh_tokens WHERE user_id = %s", (current_user["id"],))
        conn.commit()
    finally:
        conn.close()

    return {"status": "success", "message": "Password changed successfully"}
