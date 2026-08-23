import random
import string

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.serializers import meeting_to_dict
from app.services.realtime import manager

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


def _slug(title: str) -> str:
    base = "".join(c if c.isalnum() else "-" for c in title.lower()).strip("-")[:40]
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{base}-{suffix}"


@router.get("", response_model=list[schemas.MeetingOut])
def list_meetings(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    return [meeting_to_dict(m) for m in db.query(models.Meeting).all()]


@router.post("", response_model=schemas.MeetingOut, status_code=201)
async def create_meeting(
    payload: schemas.MeetingIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    meeting = models.Meeting(
        title=payload.title,
        project=payload.project,
        date=payload.date,
        time=payload.time,
        duration=payload.duration,
        attendees=payload.attendees,
        agenda=payload.agenda,
        organizer=current_user.name,
        status="scheduled",
        link=f"https://meet.nexusmind.ai/{_slug(payload.title)}",
    )
    db.add(meeting)
    db.add(
        models.Alert(
            severity="info",
            title="📅 Meeting Scheduled",
            message=f'"{meeting.title}" scheduled on {meeting.date} at {meeting.time} with {len(meeting.attendees)} attendee(s).',
        )
    )
    db.commit()
    db.refresh(meeting)

    data = meeting_to_dict(meeting)
    await manager.publish("meeting_created", data)
    return data


@router.post("/{meeting_id}/cancel", response_model=schemas.MeetingOut)
async def cancel_meeting(
    meeting_id: str, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)
):
    meeting = db.get(models.Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    meeting.status = "cancelled"
    db.commit()
    db.refresh(meeting)
    data = meeting_to_dict(meeting)
    await manager.publish("meeting_cancelled", data)
    return data
