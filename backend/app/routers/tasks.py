from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.serializers import task_to_dict
from app.services import ai_service
from app.services.push import send_push_to_user
from app.services.realtime import manager

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def _next_task_id(db: Session) -> str:
    count = db.query(models.Task).count()
    candidate = f"TASK-{100 + count + 1}"
    while db.get(models.Task, candidate):
        count += 1
        candidate = f"TASK-{100 + count + 1}"
    return candidate


def _log_history(db: Session, task_id: str, event_type: str, from_value, to_value, actor_id: str):
    db.add(
        models.TaskHistory(
            task_id=task_id,
            event_type=event_type,
            from_value=str(from_value) if from_value is not None else None,
            to_value=str(to_value) if to_value is not None else None,
            actor_id=actor_id,
        )
    )


@router.get("", response_model=list[schemas.TaskOut])
def list_tasks(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    query = db.query(models.Task)
    if current_user.org_id:
        query = query.filter(models.Task.org_id == current_user.org_id)
    return [task_to_dict(t) for t in query.all()]


@router.post("", response_model=schemas.TaskOut, status_code=201)
async def create_task(
    payload: schemas.TaskCreateIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    project = db.query(models.Project).filter(models.Project.name == payload.project).first() if payload.project else None
    assignee = db.query(models.User).filter(models.User.name == payload.assignee).first() if payload.assignee else None

    task = models.Task(
        id=_next_task_id(db),
        org_id=current_user.org_id,
        title=payload.title,
        description=payload.description,
        project_id=project.id if project else None,
        assignee_id=assignee.id if assignee else None,
        status=payload.status,
        priority=payload.priority,
        depends_on=payload.dependsOn,
        due_date=payload.dueDate or "",
        x=400.0,
        y=250.0,
        ai_risk_score=0.1,
    )
    db.add(task)
    _log_history(db, task.id, "created", None, task.title, current_user.id)
    db.commit()
    db.refresh(task)

    score, reason, _factors = ai_service.compute_risk_score(db, task)
    task.ai_risk_score, task.risk_reason = score, reason
    db.commit()
    db.refresh(task)

    data = task_to_dict(task)
    await manager.publish("task_created", data)
    return data


@router.patch("/{task_id}/status", response_model=schemas.TaskOut)
async def update_status(
    task_id: str,
    payload: schemas.TaskStatusIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    old_status = task.status
    task.status = payload.status
    if payload.status == "done":
        task.ai_risk_score = 0.05
        task.risk_reason = None
        task.completed_at = datetime.utcnow()
    _log_history(db, task.id, "status_change", old_status, payload.status, current_user.id)

    unblocked_ids: list[str] = []
    if payload.status == "done":
        dependents = db.query(models.Task).filter(models.Task.status == "blocked").all()
        for t in dependents:
            if task_id in (t.depends_on or []):
                t.status = "in_progress"
                score, reason, _ = ai_service.compute_risk_score(db, t)
                t.ai_risk_score, t.risk_reason = score, reason or "Unblocked by prerequisite completion!"
                unblocked_ids.append(t.id)

    db.commit()
    db.refresh(task)

    data = task_to_dict(task)
    await manager.publish("task_updated", data)
    for uid in unblocked_ids:
        u = db.get(models.Task, uid)
        if u:
            await manager.publish("task_updated", task_to_dict(u))
    return data


@router.patch("/{task_id}/deadline", response_model=schemas.TaskOut)
async def update_deadline(
    task_id: str,
    payload: schemas.TaskDeadlineIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    old_date = task.due_date
    task.due_date = payload.dueDate
    _log_history(db, task.id, "deadline_change", old_date, payload.dueDate, current_user.id)

    score, reason, _ = ai_service.compute_risk_score(db, task)
    task.ai_risk_score, task.risk_reason = score, reason
    db.commit()
    db.refresh(task)

    db.add(
        models.Alert(
            severity="info",
            title="📅 Deadline Updated",
            message=f"{task.id} deadline changed from {old_date} to {payload.dueDate}.",
            task_id=task.id,
        )
    )
    db.commit()

    data = task_to_dict(task)
    await manager.publish("task_updated", data)
    return data


@router.get("/{task_id}/reassignment-candidates", response_model=list[schemas.ReassignmentCandidate])
def reassignment_candidates(
    task_id: str, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)
):
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return ai_service.find_reassignment_candidates(db, task)


@router.post("/{task_id}/reassign", response_model=schemas.TaskOut)
async def reassign_task(
    task_id: str,
    payload: schemas.TaskReassignIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    new_user = db.query(models.User).filter(models.User.name == payload.assignee).first()
    if not new_user:
        raise HTTPException(status_code=404, detail="Target user not found")

    old_user = task.assignee
    old_name = old_user.name if old_user else None
    if old_user:
        old_user.active_tasks = max(0, old_user.active_tasks - 1)
        old_user.capacity = max(0, old_user.capacity - 20)
    new_user.active_tasks += 1
    new_user.capacity += 20

    task.assignee_id = new_user.id
    _log_history(db, task.id, "reassigned", old_name, new_user.name, current_user.id)

    score, reason, _ = ai_service.compute_risk_score(db, task)
    task.ai_risk_score = max(0.15, round(score - 0.1, 2))
    task.risk_reason = f"Reassigned from {old_name} to {new_user.name} (skill match & workload rebalance)."
    db.commit()
    db.refresh(task)

    db.add(
        models.Alert(
            severity="info",
            title="🔄 Task Reassigned",
            message=f"{task.id} was reassigned from {old_name} to {new_user.name}.",
            task_id=task.id,
        )
    )
    db.commit()

    data = task_to_dict(task)
    await manager.publish("task_updated", data)
    await manager.publish("user_updated", {"id": new_user.id})
    if old_user:
        await manager.publish("user_updated", {"id": old_user.id})
    await send_push_to_user(db, new_user.id, "New task assigned", f"{task.id}: {task.title}")
    return data


@router.patch("/{task_id}/position", response_model=schemas.TaskOut)
async def update_position(
    task_id: str,
    payload: schemas.TaskPositionIn,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Persists node drag position on the live task graph so layout stays
    consistent across tabs/users (broadcast over the same WS channel)."""
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.x, task.y = payload.x, payload.y
    db.commit()
    db.refresh(task)
    data = task_to_dict(task)
    await manager.publish("task_updated", data)
    return data


@router.post("/{task_id}/rescan-risk", response_model=schemas.RiskScoreOut)
async def rescan_risk(task_id: str, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    score, reason, factors = ai_service.compute_risk_score(db, task)
    task.ai_risk_score, task.risk_reason = score, reason
    db.commit()
    await manager.publish("task_updated", task_to_dict(task))
    return schemas.RiskScoreOut(taskId=task.id, aiRiskScore=score, riskReason=reason, factors=factors)


@router.post("/{task_id}/dependency/{dep_id}", response_model=schemas.TaskOut)
async def add_dependency(
    task_id: str,
    dep_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.get(models.Task, task_id)
    dep = db.get(models.Task, dep_id)
    if not task or not dep:
        raise HTTPException(status_code=404, detail="Task or dependency not found")
    if task_id == dep_id:
        raise HTTPException(status_code=400, detail="Cannot depend on self")

    deps = list(task.depends_on or [])
    if dep_id not in deps:
        deps.append(dep_id)
        task.depends_on = deps
        _log_history(db, task.id, "dependency_added", None, dep_id, current_user.id)
        score, reason, _ = ai_service.compute_risk_score(db, task)
        task.ai_risk_score, task.risk_reason = score, reason
        db.commit()
        db.refresh(task)
        data = task_to_dict(task)
        await manager.publish("task_updated", data)
        return data
    return task_to_dict(task)


@router.delete("/{task_id}/dependency/{dep_id}", response_model=schemas.TaskOut)
async def remove_dependency(
    task_id: str,
    dep_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    deps = list(task.depends_on or [])
    if dep_id in deps:
        deps.remove(dep_id)
        task.depends_on = deps
        _log_history(db, task.id, "dependency_removed", dep_id, None, current_user.id)
        score, reason, _ = ai_service.compute_risk_score(db, task)
        task.ai_risk_score, task.risk_reason = score, reason
        db.commit()
        db.refresh(task)
        data = task_to_dict(task)
        await manager.publish("task_updated", data)
        return data
    return task_to_dict(task)


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Remove from other tasks that depend on it
    downstream = db.query(models.Task).all()
    for d in downstream:
        if d.depends_on and task_id in d.depends_on:
            new_deps = [x for x in d.depends_on if x != task_id]
            d.depends_on = new_deps

    db.delete(task)
    db.commit()
    await manager.publish("task_deleted", {"id": task_id})
    return None


@router.get("/{task_id}/comments", response_model=list[schemas.TaskCommentOut])
def get_task_comments(
    task_id: str,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    comments = (
        db.query(models.TaskComment)
        .filter(models.TaskComment.task_id == task_id)
        .order_by(models.TaskComment.created_at.asc())
        .all()
    )
    out = []
    for c in comments:
        out.append(
            schemas.TaskCommentOut(
                id=c.id,
                task_id=c.task_id,
                author_id=c.author_id,
                author_name=c.author.name if c.author else "Unknown",
                author_avatar=c.author.avatar if c.author else "US",
                content=c.content,
                created_at=c.created_at,
            )
        )
    return out


@router.post("/{task_id}/comments", response_model=schemas.TaskCommentOut, status_code=201)
async def add_task_comment(
    task_id: str,
    payload: schemas.TaskCommentIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    comment = models.TaskComment(
        task_id=task.id,
        author_id=current_user.id,
        content=payload.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    res = schemas.TaskCommentOut(
        id=comment.id,
        task_id=comment.task_id,
        author_id=comment.author_id,
        author_name=current_user.name,
        author_avatar=current_user.avatar,
        content=comment.content,
        created_at=comment.created_at,
    )

    await manager.publish("comment_added", res.model_dump(mode="json"))
    return res


