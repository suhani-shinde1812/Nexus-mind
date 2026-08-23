"""
Small helpers to turn ORM rows (which store project/assignee as FK ids)
into the flat, name-based JSON shape the existing front-end already
understands (see web/src/js/state.js DEFAULT_STATE.tasks).
"""
from app import models


def task_to_dict(task: models.Task) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description or "",
        "project": task.project.name if task.project else None,
        "assignee": task.assignee.name if task.assignee else None,
        "status": task.status,
        "priority": task.priority,
        "dependsOn": task.depends_on or [],
        "x": task.x,
        "y": task.y,
        "dueDate": task.due_date,
        "aiRiskScore": task.ai_risk_score,
        "riskReason": task.risk_reason,
    }


def user_to_dict(user: models.User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "app_role": user.app_role,
        "avatar": user.avatar,
        "capacity": user.capacity,
        "active_tasks": user.active_tasks,
        "skills": user.skills or [],
    }


def alert_to_dict(alert: models.Alert) -> dict:
    return {
        "id": alert.id,
        "severity": alert.severity,
        "title": alert.title,
        "message": alert.message,
        "taskId": alert.task_id,
        "read": alert.read,
        "timestamp": alert.created_at.isoformat(),
    }


def meeting_to_dict(meeting: models.Meeting) -> dict:
    return {
        "id": meeting.id,
        "title": meeting.title,
        "project": meeting.project,
        "date": meeting.date,
        "time": meeting.time,
        "duration": meeting.duration,
        "attendees": meeting.attendees or [],
        "agenda": meeting.agenda,
        "organizer": meeting.organizer,
        "status": meeting.status,
        "link": meeting.link,
    }
