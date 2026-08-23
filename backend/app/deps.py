"""
Shared FastAPI dependencies: DB session, current-user auth guard, and RBAC permission guards.
"""
from typing import Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.security import decode_token, has_permission

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_user_from_token(token: str, db: Session) -> models.User | None:
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return None
    user = db.get(models.User, payload.get("sub"))
    return user


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    user = get_user_from_token(token, db)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_permission(permission: str) -> Callable:
    """Dependency factory enforcing RBAC permission checks on API routes."""
    def _permission_guard(current_user: models.User = Depends(get_current_user)) -> models.User:
        if not has_permission(current_user.app_role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Missing required permission '{permission}' for role '{current_user.app_role}'",
            )
        return current_user

    return _permission_guard


def log_audit_event(
    db: Session,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    actor: models.User | None = None,
    details: dict | None = None,
    request: Request | None = None,
):
    """Utility to persist immutable security audit trail events."""
    ip = "127.0.0.1"
    user_agent = "API Client"
    if request:
        ip = request.client.host if request.client else "127.0.0.1"
        user_agent = request.headers.get("user-agent", "API Client")

    log = models.AuditLog(
        org_id=actor.org_id if actor else None,
        actor_id=actor.id if actor else None,
        actor_name=actor.name if actor else "System",
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip,
        user_agent=user_agent[:290],
        details=details or {},
    )
    db.add(log)
    db.commit()
