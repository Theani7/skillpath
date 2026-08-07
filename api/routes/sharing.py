import json
import logging
import secrets
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from api.auth import get_current_user, get_current_optional_user
from api.database import get_db_connection

logger = logging.getLogger("resume-analyzer")

router = APIRouter(prefix="/api/reports", tags=["sharing"])


class ShareReportRequest(BaseModel):
    analysis_id: int = Field(..., gt=0)
    expires_in_hours: int = Field(default=72, ge=1, le=8760)
    is_public: bool = False


@router.post("/share")
def create_share_link(payload: ShareReportRequest, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM user_data WHERE ID = %s AND user_id = %s",
            (payload.analysis_id, current_user["id"]),
        )
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Analysis not found")
        token = secrets.token_urlsafe(24)
        expires_at = int(time.time()) + (payload.expires_in_hours * 3600)
        cursor.execute(
            """
            INSERT INTO shared_reports(token, user_id, analysis_id, expires_at, is_public)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (token, current_user["id"], payload.analysis_id, expires_at, int(payload.is_public)),
        )
        conn.commit()
    finally:
        conn.close()
    return {"share_token": token, "expires_at": expires_at}


@router.get("/share/{token}")
def get_shared_report(token: str, current_user: Optional[dict] = Depends(get_current_optional_user)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM shared_reports WHERE token = %s", (token,))
        share = cursor.fetchone()
        if not share:
            raise HTTPException(status_code=404, detail="Share link not found")
        if int(share["expires_at"]) < int(time.time()):
            raise HTTPException(status_code=410, detail="Share link expired")

        # Check access: public shares are open, private shares require owner auth
        if not share["is_public"]:
            if not current_user or current_user["id"] != share["user_id"]:
                raise HTTPException(status_code=403, detail="This is a private share link")

        cursor.execute("SELECT analysis_data FROM user_data WHERE ID = %s", (share["analysis_id"],))
        row = cursor.fetchone()
    finally:
        conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found")
    try:
        payload = json.loads(row["analysis_data"])
    except Exception:
        payload = {}
    return {"analysis": payload, "shared": True}


@router.delete("/share/{token}")
def revoke_share_link(token: str, current_user: dict = Depends(get_current_user)):
    """Revoke a share link so it can no longer be accessed."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id FROM shared_reports WHERE token = %s",
            (token,),
        )
        share = cursor.fetchone()
        if not share:
            raise HTTPException(status_code=404, detail="Share link not found")
        if share["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to revoke this link")
        cursor.execute("DELETE FROM shared_reports WHERE token = %s", (token,))
        conn.commit()
    finally:
        conn.close()
    return {"detail": "Share link revoked"}


@router.get("/my-shares")
def get_my_shares(current_user: dict = Depends(get_current_user)):
    """List all share links created by the current user."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT sr.token, sr.analysis_id, sr.expires_at, sr.is_public,
                   sr.created_at, ud.pdf_name, ud.target_role
            FROM shared_reports sr
            JOIN user_data ud ON sr.analysis_id = ud.ID
            WHERE sr.user_id = %s
            ORDER BY sr.created_at DESC
            """,
            (current_user["id"],),
        )
        rows = cursor.fetchall()
    finally:
        conn.close()

    shares = []
    for row in rows:
        shares.append({
            "token": row["token"],
            "analysis_id": row["analysis_id"],
            "pdf_name": row["pdf_name"],
            "target_role": row["target_role"],
            "expires_at": row["expires_at"],
            "is_public": bool(row["is_public"]),
            "expired": int(row["expires_at"]) < int(time.time()),
        })
    return {"shares": shares}
