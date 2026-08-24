"""
Meetings & Video Collaboration Router:
- Schedule, List, Start, End, and Cancel Realtime Meetings
- Generates deterministic Jitsi Room URLs shared across all participants
- Broadcasts real-time events through Redis Pub/Sub & WebSocket connection manager
- Persists meeting records, attendees, and agenda notes in PostgreSQL/SQLite
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.serializers import alert_to_dict, meeting_to_dict
from app.services.realtime import manager

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


def _generate_jitsi_room(meeting_id: str) -> str:
    """Generate a clean, deterministic room identifier from meeting ID."""
    clean_id = meeting_id.lower().replace("_", "-").replace(":", "-")
    return f"nexusmind-{clean_id}"


@router.get("", response_model=list[schemas.MeetingOut])
def list_meetings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """List all scheduled and recent meetings for the user's organization."""
    if current_user.org_id:
        meetings = (
            db.query(models.Meeting)
            .filter((models.Meeting.org_id == current_user.org_id) | (models.Meeting.org_id == None))
            .order_by(models.Meeting.created_at.desc())
            .all()
        )
    else:
        meetings = db.query(models.Meeting).order_by(models.Meeting.created_at.desc()).all()

    return [meeting_to_dict(m) for m in meetings]


@router.get("/{meeting_id}", response_model=schemas.MeetingOut)
def get_meeting(
    meeting_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Retrieve details for a specific meeting."""
    meeting = db.get(models.Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    if current_user.org_id and meeting.org_id and meeting.org_id != current_user.org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this meeting")
    return meeting_to_dict(meeting)


@router.post("", response_model=schemas.MeetingOut, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    payload: schemas.MeetingIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Create a new team meeting, generate a stable Jitsi room URL, and broadcast real-time sync event."""
    meeting_id = f"MTG-{uuid.uuid4().hex[:10].upper()}"
    room_name = _generate_jitsi_room(meeting_id)
    jitsi_link = f"https://meet.jit.si/{room_name}"

    meeting = models.Meeting(
        id=meeting_id,
        org_id=current_user.org_id,
        title=payload.title.strip(),
        project=payload.project or "General",
        date=payload.date,
        time=payload.time,
        duration=payload.duration or "30",
        attendees=payload.attendees or [],
        agenda=payload.agenda or "",
        organizer=current_user.name,
        status="scheduled",
        link=jitsi_link,
    )
    db.add(meeting)

    # In-app alert for the organization & attendees
    alert = models.Alert(
        org_id=current_user.org_id,
        severity="info",
        title="📅 Meeting Scheduled",
        message=f'{current_user.name} scheduled "{meeting.title}" on {meeting.date} at {meeting.time}.',
    )
    db.add(alert)
    db.commit()
    db.refresh(meeting)

    data = meeting_to_dict(meeting)

    # Real-time Pub/Sub broadcasts
    await manager.publish("meeting_created", data)
    await manager.publish("MEETING_CREATED", data)
    await manager.publish("alert_created", alert_to_dict(alert))
    return data


@router.post("/{meeting_id}/start", response_model=schemas.MeetingOut)
async def start_meeting(
    meeting_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Mark a meeting as in-progress and notify participants."""
    meeting = db.get(models.Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    if current_user.org_id and meeting.org_id and meeting.org_id != current_user.org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    meeting.status = "in_progress"
    db.commit()
    db.refresh(meeting)

    data = meeting_to_dict(meeting)
    await manager.publish("meeting_started", data)
    await manager.publish("MEETING_STARTED", data)
    await manager.publish("meeting_updated", data)
    await manager.publish("MEETING_UPDATED", data)
    return data


@router.post("/{meeting_id}/end", response_model=schemas.MeetingOut)
async def end_meeting(
    meeting_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Mark a meeting as completed."""
    meeting = db.get(models.Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    if current_user.org_id and meeting.org_id and meeting.org_id != current_user.org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    meeting.status = "completed"
    db.commit()
    db.refresh(meeting)

    data = meeting_to_dict(meeting)
    await manager.publish("meeting_ended", data)
    await manager.publish("MEETING_ENDED", data)
    await manager.publish("meeting_updated", data)
    await manager.publish("MEETING_UPDATED", data)
    return data


@router.post("/{meeting_id}/cancel", response_model=schemas.MeetingOut)
async def cancel_meeting(
    meeting_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Cancel a scheduled meeting and notify participants."""
    meeting = db.get(models.Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    if current_user.org_id and meeting.org_id and meeting.org_id != current_user.org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    meeting.status = "cancelled"
    db.commit()
    db.refresh(meeting)

    data = meeting_to_dict(meeting)
    await manager.publish("meeting_cancelled", data)
    await manager.publish("MEETING_CANCELLED", data)
    await manager.publish("meeting_updated", data)
    await manager.publish("MEETING_UPDATED", data)
    return data
