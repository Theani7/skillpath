import logging
import time

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.auth import get_current_user
from api.database import get_db_connection
from api.i18n import get_translations
from api.scraper import get_scraper_status

logger = logging.getLogger("resume-analyzer")

router = APIRouter(tags=["misc"])


class BillingSubscribeRequest(BaseModel):
    plan: str = Field(..., pattern=r'^(free|pro|enterprise)$')


class NotificationInput(BaseModel):
    channel: str = Field(default="email", pattern=r'^(email|push|sms)$')
    message: str = Field(..., min_length=1, max_length=500)
    send_at: int = Field(default=0, ge=0)


class TranslationRequest(BaseModel):
    locale: str = Field(default="en", max_length=10)


@router.get("/api/trends/status")
def get_trends_status():
    """Returns the last scraped timestamp and current active skills."""
    return get_scraper_status()


@router.get("/api/billing/plans")
def get_billing_plans():
    return {
        "plans": [
            {"id": "free", "price_usd_month": 0, "features": ["Basic analysis", "Limited job matches"]},
            {"id": "pro", "price_usd_month": 19, "features": ["Advanced rewrite", "Interview packs", "Team ranking"]},
            {"id": "enterprise", "price_usd_month": 99, "features": ["Recruiter workspace", "Priority support", "Analytics exports"]},
        ]
    }


@router.post("/api/billing/subscribe")
def subscribe_plan(payload: BillingSubscribeRequest, current_user: dict = Depends(get_current_user)):
    allowed = {"free", "pro", "enterprise"}
    if payload.plan not in allowed:
        raise HTTPException(status_code=400, detail="Invalid plan")
    renews_at = int(time.time()) + (30 * 24 * 3600)
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO subscriptions(user_id, plan, status, renews_at, updated_at)
            VALUES (%s, %s, 'active', %s, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                plan = excluded.plan,
                status = 'active',
                renews_at = excluded.renews_at,
                updated_at = CURRENT_TIMESTAMP
            """,
            (current_user["id"], payload.plan, renews_at),
        )
        conn.commit()
    finally:
        conn.close()
    return {"status": "success", "plan": payload.plan, "renews_at": renews_at}


@router.get("/api/billing/subscription")
def get_subscription(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subscriptions WHERE user_id = %s", (current_user["id"],))
        row = cursor.fetchone()
    finally:
        conn.close()
    if not row:
        return {"subscription": {"plan": "free", "status": "active"}}
    return {"subscription": dict(row)}


@router.post("/api/notifications")
def create_notification(payload: NotificationInput, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notifications(user_id, channel, message, status, send_at) VALUES (%s, %s, %s, 'pending', %s) RETURNING id",
            (current_user["id"], payload.channel, payload.message, payload.send_at),
        )
        notification_id = cursor.fetchone()["id"]
        conn.commit()
    finally:
        conn.close()
    return {"status": "success", "notification_id": notification_id}


@router.get("/api/notifications")
def list_notifications(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notifications WHERE user_id = %s ORDER BY id DESC", (current_user["id"],))
        rows = [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()
    return {"notifications": rows}


@router.post("/api/notifications/{notification_id}/send")
def send_notification(notification_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE notifications SET status = 'sent' WHERE id = %s AND user_id = %s",
            (notification_id, current_user["id"]),
        )
        conn.commit()
    finally:
        conn.close()
    return {"status": "success", "message": "Notification marked as sent"}


@router.post("/api/i18n/translations")
def get_i18n_translations(payload: TranslationRequest):
    return {"locale": payload.locale, "translations": get_translations(payload.locale)}
