import os
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from jwt import InvalidTokenError
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from api.database import get_db_connection
from api.security import verify_password

load_dotenv()

_SECRET_FROM_ENV = os.getenv("JWT_SECRET_KEY")
if not _SECRET_FROM_ENV or len(_SECRET_FROM_ENV) < 32:
    if os.getenv("ENV", "development").lower() in ("production", "prod"):
        raise RuntimeError(
            "JWT_SECRET_KEY must be set to a 32+ char secret in production."
        )
    _SECRET_FROM_ENV = os.urandom(32).hex()

SECRET_KEY = _SECRET_FROM_ENV
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30
COOKIE_NAME = "skillpath_access"
REFRESH_COOKIE_NAME = "skillpath_refresh"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def _create_token(data: dict, token_type: str, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    jti = hashlib.sha256(os.urandom(16)).hexdigest()[:16]
    to_encode.update({"exp": expire, "type": token_type, "jti": jti})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    return _create_token(data, "access", expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    return _create_token(data, "refresh", expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _decode(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def _load_user(username: str) -> Optional[dict]:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id, username, email, full_name, role, created_at, is_active FROM users WHERE username = %s",
                (username,),
            )
        except Exception:
            cursor.execute(
                "SELECT id, username, email, full_name, role FROM users WHERE username = %s",
                (username,),
            )
        user = cursor.fetchone()
        return dict(user) if user else None
    finally:
        conn.close()


def _raise_401() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)) -> dict:
    auth_token = token
    if not auth_token:
        auth_token = request.cookies.get(COOKIE_NAME)
    if not auth_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            auth_token = auth_header.split(" ", 1)[1]
    if not auth_token:
        raise _raise_401()
    try:
        payload = _decode(auth_token)
    except InvalidTokenError:
        raise _raise_401()
    username = payload.get("sub")
    token_type = payload.get("type")
    if not username or token_type != "access":
        raise _raise_401()
    user = _load_user(username)
    if user is None:
        raise _raise_401()
    if user.get("is_active") == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated. Contact an administrator.",
        )
    return user


async def get_current_optional_user(request: Request) -> Optional[dict]:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    if not token:
        return None
    try:
        payload = _decode(token)
    except InvalidTokenError:
        return None
    username = payload.get("sub")
    token_type = payload.get("type")
    if not username or token_type != "access":
        return None
    user = _load_user(username)
    if user is not None and user.get("is_active") == 0:
        return None
    return user


async def get_current_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
    return current_user


def decode_token(token: str) -> dict:
    return _decode(token)


async def get_user_from_cookie(request: Request) -> Optional[str]:
    token = request.cookies.get(COOKIE_NAME)
    if token:
        return token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    return None


async def get_current_user_from_cookie(request: Request) -> dict:
    token = await get_user_from_cookie(request)
    if not token:
        raise _raise_401()
    try:
        payload = _decode(token)
    except InvalidTokenError:
        raise _raise_401()
    username = payload.get("sub")
    token_type = payload.get("type")
    if not username or token_type != "access":
        raise _raise_401()
    user = _load_user(username)
    if user is None:
        raise _raise_401()
    if user.get("is_active") == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated. Contact an administrator.",
        )
    return user


def client_ip(request: Request) -> str:
    if request.client and request.client.host:
        return request.client.host
    return "unknown"
