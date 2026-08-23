from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.serializers import alert_to_dict
from app.services.realtime import manager

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=list[schemas.AlertOut])
def list_alerts(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    rows = db.query(models.Alert).order_by(models.Alert.created_at.desc()).all()
    return rows


@router.post("", response_model=schemas.AlertOut, status_code=201)
async def create_alert(
    payload: schemas.AlertIn, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)
):
    alert = models.Alert(
        severity=payload.severity, title=payload.title, message=payload.message, task_id=payload.taskId
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    data = alert_to_dict(alert)
    await manager.publish("alert_created", data)
    return alert


@router.post("/{alert_id}/read", status_code=204)
def mark_read(alert_id: str, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    alert = db.get(models.Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.read = True
    db.commit()
