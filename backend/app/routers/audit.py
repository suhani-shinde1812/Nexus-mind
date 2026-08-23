"""
Security Audit Log Router:
Searchable immutable chronological activity trail for compliance and security auditing.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user, require_permission

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/logs", response_model=list[schemas.AuditLogOut])
def get_audit_logs(
    action: str | None = None,
    resource_type: str | None = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_permission("audit:read")),
):
    query = db.query(models.AuditLog)
    if action:
        query = query.filter(models.AuditLog.action == action)
    if resource_type:
        query = query.filter(models.AuditLog.resource_type == resource_type)

    logs = query.order_by(models.AuditLog.created_at.desc()).offset(offset).limit(limit).all()
    return logs
