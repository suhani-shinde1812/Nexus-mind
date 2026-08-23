from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=list[schemas.UserOut])
def list_users(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    return db.query(models.User).all()


@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: str, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: str,
    payload: schemas.UserUpdateIn,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.post("/me/push-token", status_code=204)
def register_push_token(
    token: str,
    platform: str = "android",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Called by the Flutter app after obtaining an FCM device token."""
    existing = db.query(models.PushToken).filter(models.PushToken.token == token).first()
    if existing:
        existing.user_id = current_user.id
    else:
        db.add(models.PushToken(user_id=current_user.id, token=token, platform=platform))
    db.commit()
