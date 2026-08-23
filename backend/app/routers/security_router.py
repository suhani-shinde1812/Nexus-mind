"""
Cybersecurity Center Router:
- Threat Radar Score & Active Hazard Assessment
- Security Event Log (brute force attempts, abnormal token usage)
- Anomaly Detection Evaluation
"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user, require_permission

router = APIRouter(prefix="/api/security", tags=["security"])


@router.get("/threat-radar", response_model=schemas.ThreatRadarOut)
def get_threat_radar(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    now = datetime.now(timezone.utc)
    day_ago = now - timedelta(hours=24)

    # Calculate failed logins in last 24h
    failed_logins = (
        db.query(models.SecurityEvent)
        .filter(
            models.SecurityEvent.event_type == "failed_login_attempt",
            models.SecurityEvent.created_at >= day_ago,
        )
        .count()
    )

    open_events = (
        db.query(models.SecurityEvent)
        .filter(models.SecurityEvent.status == "open")
        .order_by(models.SecurityEvent.created_at.desc())
        .limit(10)
        .all()
    )

    # Compute Threat Score (0 - 100)
    score = 12 + (failed_logins * 8) + (len(open_events) * 12)
    threat_score = min(98, max(5, score))

    if threat_score < 30:
        level = "SECURE"
    elif threat_score < 60:
        level = "ELEVATED"
    elif threat_score < 85:
        level = "HIGH"
    else:
        level = "CRITICAL"

    return schemas.ThreatRadarOut(
        threat_score=threat_score,
        threat_level=level,
        active_threats_count=len(open_events),
        failed_logins_24h=failed_logins,
        recent_anomalies=open_events,
    )


@router.get("/events", response_model=list[schemas.SecurityEventOut])
def list_security_events(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    events = db.query(models.SecurityEvent).order_by(models.SecurityEvent.created_at.desc()).limit(50).all()
    return events


@router.post("/events/{event_id}/resolve")
def resolve_security_event(
    event_id: str,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_permission("security:manage")),
):
    event = db.get(models.SecurityEvent, event_id)
    if event:
        event.status = "resolved"
        db.commit()
    return {"status": "resolved", "event_id": event_id}
