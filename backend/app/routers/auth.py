"""
Authentication & IAM Router:
- Registration, JWT Login, Refresh token rotation
- MFA (TOTP) Setup, Enable & Verification
- Active Session Management & Remote Revocation
"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas, security
from app.database import get_db
from app.deps import get_current_user, log_audit_event

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=schemas.TokenOut, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.RegisterIn, request: Request, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered")

    initials = "".join([part[0] for part in payload.name.split() if part])[:2].upper() or "US"

    # Default organization
    org = db.query(models.Organization).filter(models.Organization.slug == "default-org").first()
    if not org:
        org = models.Organization(name="Nexus Enterprise Corp", slug="default-org", plan="enterprise")
        db.add(org)
        db.flush()

    user = models.User(
        org_id=org.id,
        name=payload.name,
        email=payload.email,
        hashed_password=security.hash_password(payload.password),
        role=payload.role,
        app_role=payload.app_role,
        avatar=payload.avatar or initials,
        capacity=30,
        active_tasks=0,
        skills=payload.skills,
        mfa_enabled=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    log_audit_event(
        db,
        action="user_registered",
        resource_type="user",
        resource_id=user.id,
        actor=user,
        details={"email": user.email, "role": user.role},
        request=request,
    )

    access = security.create_access_token(user.id)
    refresh = security.create_refresh_token(user.id)

    # Record session
    session = models.UserSession(
        user_id=user.id,
        refresh_token_hash=security.hash_token(refresh),
        user_agent=request.headers.get("user-agent", "Browser")[:290],
        ip_address=request.client.host if request.client else "127.0.0.1",
        expires_at=datetime.now(timezone.utc) + timedelta(days=14),
    )
    db.add(session)
    db.commit()

    return schemas.TokenOut(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=schemas.TokenOut)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        # Log failed login attempt for security monitoring
        ip = request.client.host if request.client else "127.0.0.1"
        sec_event = models.SecurityEvent(
            severity="medium",
            event_type="failed_login_attempt",
            description=f"Failed login attempt for email '{form_data.username}' from {ip}",
            ip_address=ip,
        )
        db.add(sec_event)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is deactivated")

    # If MFA is enabled, challenge with temporary token
    if user.mfa_enabled:
        temp_token = security.create_temp_mfa_token(user.id)
        return schemas.TokenOut(
            access_token="",
            refresh_token="",
            mfa_required=True,
            temp_token=temp_token,
        )

    access = security.create_access_token(user.id)
    refresh = security.create_refresh_token(user.id)

    # Save active session
    session = models.UserSession(
        user_id=user.id,
        refresh_token_hash=security.hash_token(refresh),
        user_agent=request.headers.get("user-agent", "Browser")[:290],
        ip_address=request.client.host if request.client else "127.0.0.1",
        expires_at=datetime.now(timezone.utc) + timedelta(days=14),
    )
    db.add(session)
    db.commit()

    log_audit_event(
        db,
        action="user_login",
        resource_type="auth",
        resource_id=user.id,
        actor=user,
        request=request,
    )

    return schemas.TokenOut(access_token=access, refresh_token=refresh)


@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user


# --------------------------------------------------------------------------
# MFA (TOTP) Endpoints

# --------------------------------------------------------------------------
@router.post("/mfa/setup", response_model=schemas.MfaSetupOut)
def mfa_setup(current_user: models.User = Depends(get_current_user)):
    """Generate TOTP Secret and QR provisioning URI."""
    secret = security.generate_totp_secret()
    uri = security.get_totp_uri(secret, current_user.email)
    return schemas.MfaSetupOut(secret=secret, provisioning_uri=uri)


@router.post("/mfa/enable", response_model=schemas.MfaEnableOut)
def mfa_enable(
    payload: schemas.MfaVerifyIn,
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Confirm TOTP code, encrypt secret at rest, generate backup codes, and enable MFA."""
    if not payload.secret or not security.verify_totp_code(payload.secret, payload.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid TOTP verification code")

    plain_codes, hashed_codes = security.generate_backup_recovery_codes(8)

    current_user.mfa_enabled = True
    current_user.mfa_secret = security.encrypt_secret(payload.secret)
    current_user.mfa_backup_codes = hashed_codes
    db.commit()

    log_audit_event(
        db,
        action="mfa_enabled",
        resource_type="security",
        resource_id=current_user.id,
        actor=current_user,
        details={"backup_codes_generated": len(plain_codes)},
        request=request,
    )
    return schemas.MfaEnableOut(
        status="mfa_enabled",
        message="Two-Factor Authentication is now active. Save your backup recovery codes securely.",
        backup_codes=plain_codes,
    )


@router.post("/mfa/disable")
def mfa_disable(
    payload: schemas.MfaVerifyIn,
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Disable MFA, clear encrypted secret & backup codes, and invalidate other sessions."""
    if not current_user.mfa_enabled or not current_user.mfa_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA is not currently enabled")

    # Verify with TOTP or backup code
    is_valid = security.verify_totp_code(current_user.mfa_secret, payload.code)
    if not is_valid and current_user.mfa_backup_codes:
        is_backup, _ = security.verify_backup_code(payload.code, current_user.mfa_backup_codes)
        is_valid = is_backup

    if not is_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA verification code")

    current_user.mfa_enabled = False
    current_user.mfa_secret = None
    current_user.mfa_backup_codes = []

    # Invalidate all user sessions
    db.query(models.UserSession).filter(models.UserSession.user_id == current_user.id).update({"is_revoked": True})
    db.commit()

    log_audit_event(
        db,
        action="mfa_disabled",
        resource_type="security",
        resource_id=current_user.id,
        actor=current_user,
        request=request,
    )
    return {"status": "mfa_disabled", "message": "Two-Factor Authentication has been disabled."}


@router.post("/mfa/verify", response_model=schemas.TokenOut)
def mfa_verify(payload: schemas.MfaVerifyIn, request: Request, db: Session = Depends(get_db)):
    """Verify MFA challenge using 6-digit TOTP or 8-char backup recovery code."""
    if not payload.temp_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing temp_token")

    token_data = security.decode_token(payload.temp_token)
    if not token_data or token_data.get("type") != "temp":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired MFA token")

    user = db.get(models.User, token_data.get("sub"))
    if not user or not user.mfa_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User MFA is not configured")

    # Try TOTP verification
    verified = security.verify_totp_code(user.mfa_secret, payload.code)
    used_backup = False

    # Try Backup Code verification if TOTP fails
    if not verified and user.mfa_backup_codes:
        is_backup, remaining = security.verify_backup_code(payload.code, user.mfa_backup_codes)
        if is_backup:
            verified = True
            used_backup = True
            user.mfa_backup_codes = remaining
            db.commit()

    if not verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA verification code or backup code")

    access = security.create_access_token(user.id)
    refresh = security.create_refresh_token(user.id)

    session = models.UserSession(
        user_id=user.id,
        refresh_token_hash=security.hash_token(refresh),
        user_agent=request.headers.get("user-agent", "Browser")[:290],
        ip_address=request.client.host if request.client else "127.0.0.1",
        expires_at=datetime.now(timezone.utc) + timedelta(days=14),
    )
    db.add(session)
    db.commit()

    log_audit_event(
        db,
        action="mfa_login_success",
        resource_type="auth",
        actor=user,
        details={"used_backup_code": used_backup},
        request=request,
    )
    return schemas.TokenOut(access_token=access, refresh_token=refresh)



# --------------------------------------------------------------------------
# Session & Token Management
# --------------------------------------------------------------------------
@router.post("/refresh", response_model=schemas.TokenOut)
def refresh(payload: schemas.RefreshIn, request: Request, db: Session = Depends(get_db)):
    token_data = security.decode_token(payload.refresh_token)
    if not token_data or token_data.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = token_data.get("sub")
    user = db.get(models.User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive or not found")

    old_hash = security.hash_token(payload.refresh_token)
    session = db.query(models.UserSession).filter(models.UserSession.refresh_token_hash == old_hash).first()

    if not session or session.is_revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session has been revoked or expired")

    new_access = security.create_access_token(user.id)
    new_refresh = security.create_refresh_token(user.id)

    session.refresh_token_hash = security.hash_token(new_refresh)
    session.expires_at = datetime.now(timezone.utc) + timedelta(days=14)
    db.commit()

    return schemas.TokenOut(access_token=new_access, refresh_token=new_refresh)


@router.get("/sessions", response_model=list[schemas.UserSessionOut])
def list_sessions(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List all active login sessions for the authenticated user."""
    sessions = (
        db.query(models.UserSession)
        .filter(models.UserSession.user_id == current_user.id, models.UserSession.is_revoked == False)
        .all()
    )
    return sessions


@router.delete("/sessions/{session_id}")
@router.post("/sessions/{session_id}/revoke")
def revoke_session(
    session_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Revoke a specific session remotely."""
    session = db.get(models.UserSession, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    session.is_revoked = True
    db.commit()
    return {"status": "ok", "message": "Session revoked successfully"}
