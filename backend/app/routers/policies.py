from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/api/policies", tags=["policies"])


@router.get("", response_model=list[schemas.PolicyOut])
def list_policies(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    return db.query(models.Policy).all()
