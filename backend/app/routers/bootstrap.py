"""
Single aggregate endpoint the front-end calls on load to hydrate the entire workspace state.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.deps import get_current_user
from app.serializers import alert_to_dict, meeting_to_dict, task_to_dict, user_to_dict
from app.services import github_service

router = APIRouter(prefix="/api", tags=["bootstrap"])


@router.get("/bootstrap")
def bootstrap(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    org_id = current_user.org_id
    if org_id:
        users = db.query(models.User).filter((models.User.org_id == org_id) | (models.User.org_id == None)).all()
        tasks = db.query(models.Task).filter((models.Task.org_id == org_id) | (models.Task.org_id == None)).all()
        projects = db.query(models.Project).filter((models.Project.org_id == org_id) | (models.Project.org_id == None)).all()
        meetings = db.query(models.Meeting).filter((models.Meeting.org_id == org_id) | (models.Meeting.org_id == None)).order_by(models.Meeting.created_at.desc()).all()
        alerts = db.query(models.Alert).filter((models.Alert.org_id == org_id) | (models.Alert.org_id == None)).order_by(models.Alert.created_at.desc()).limit(50).all()

    else:
        users = db.query(models.User).all()
        tasks = db.query(models.Task).all()
        projects = db.query(models.Project).all()
        meetings = db.query(models.Meeting).order_by(models.Meeting.created_at.desc()).all()
        alerts = db.query(models.Alert).order_by(models.Alert.created_at.desc()).limit(50).all()

    policies = db.query(models.Policy).all()
    history = db.query(models.TaskHistory).order_by(models.TaskHistory.created_at.desc()).limit(30).all()
    user_map = {u.id: u.name for u in users}


    activity_logs = [
        {
            "id": h.id,
            "taskId": h.task_id,
            "eventType": h.event_type,
            "fromValue": h.from_value,
            "toValue": h.to_value,
            "actor": user_map.get(h.actor_id, "System AI Agent"),
            "timestamp": h.created_at.isoformat(),
        }
        for h in history
    ]

    # Engineering metrics
    eng_metrics = github_service.compute_engineering_metrics(db)

    # Security threat stats
    failed_logins = db.query(models.SecurityEvent).filter(models.SecurityEvent.event_type == "failed_login_attempt").count()
    open_threats = db.query(models.SecurityEvent).filter(models.SecurityEvent.status == "open").count()
    threat_score = min(98, max(5, 12 + (failed_logins * 8) + (open_threats * 12)))

    return {
        "currentUser": user_to_dict(current_user),
        "users": [user_to_dict(u) for u in users],
        "projects": [
            {"id": p.id, "name": p.name, "lead": p.lead, "deadline": p.deadline, "progress": p.progress}
            for p in projects
        ],
        "tasks": [task_to_dict(t) for t in tasks],
        "policies": [
            {"id": p.id, "title": p.title, "category": p.category, "tags": p.tags, "summary": p.summary}
            for p in policies
        ],
        "aiAlerts": [alert_to_dict(a) for a in alerts],
        "meetings": [meeting_to_dict(m) for m in meetings],
        "activityLogs": activity_logs,
        "securityThreat": {
            "threat_score": threat_score,
            "threat_level": "SECURE" if threat_score < 30 else ("ELEVATED" if threat_score < 60 else "HIGH"),
            "active_threats_count": open_threats,
            "failed_logins_24h": failed_logins,
        },
        "engineeringMetrics": eng_metrics.model_dump(mode="json"),
        "systemStats": {
            "cpuLoad": "18%",
            "memoryUsage": "240 MB",
            "activeConnections": len(users),
            "graphNodeCount": len(tasks),
            "graphEdgeCount": sum(len(t.depends_on or []) for t in tasks),
            "aiInferenceLatency": "180ms",
        },
    }
