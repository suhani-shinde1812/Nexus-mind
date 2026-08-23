"""
Firebase Cloud Messaging push notifications for the Flutter mobile app.
Uses the legacy FCM HTTP API (single server key) to keep the backend
dependency-light; swap for the HTTP v1 API + service-account OAuth if you
need per-message analytics/receipts.
"""
from __future__ import annotations

import logging

import httpx
from sqlalchemy.orm import Session

from app import models
from app.config import get_settings

logger = logging.getLogger("nexusmind.push")
settings = get_settings()

FCM_URL = "https://fcm.googleapis.com/fcm/send"


async def send_push_to_user(db: Session, user_id: str, title: str, body: str, data: dict | None = None) -> None:
    if not settings.fcm_server_key:
        logger.debug("FCM_SERVER_KEY not set -- skipping push notification")
        return

    tokens = db.query(models.PushToken).filter(models.PushToken.user_id == user_id).all()
    if not tokens:
        return

    headers = {
        "Authorization": f"key={settings.fcm_server_key}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        for t in tokens:
            payload = {
                "to": t.token,
                "notification": {"title": title, "body": body},
                "data": data or {},
            }
            try:
                await client.post(FCM_URL, json=payload, headers=headers)
            except Exception:
                logger.exception("Failed to push to token %s", t.token)
