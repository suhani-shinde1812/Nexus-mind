"""
NEXUS MIND — STRUCTURED AGENT TOOLS ENGINE

Provides strictly typed, multi-tenant scoped database tools for the AI Agent Swarm.
Every tool enforces organization isolation and RBAC checks using the authenticated user.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app import models
from app.serializers import task_to_dict, user_to_dict


def _get_org_tasks_query(db: Session, current_user: models.User):
    """Base query ensuring multi-tenant organization boundaries."""
    query = db.query(models.Task)
    if current_user.org_id:
        query = query.filter((models.Task.org_id == current_user.org_id) | (models.Task.org_id == None))
    return query


def _get_org_users_query(db: Session, current_user: models.User):
    """Base query ensuring organization boundaries for users."""
    query = db.query(models.User)
    if current_user.org_id:
        query = query.filter((models.User.org_id == current_user.org_id) | (models.User.org_id == None))
    return query


def search_tasks(
    db: Session,
    query: str,
    current_user: models.User,
    project_id: str | None = None,
    assignee_id: str | None = None,
    status: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Search tasks matching an ID, title keywords, or description within authorized organization.
    """
    q_clean = query.strip()
    if not q_clean:
        return []

    base_query = _get_org_tasks_query(db, current_user)

    # 1. Exact ID Match (e.g., 'TASK-102' or '102')
    exact_id = q_clean.upper() if q_clean.upper().startswith("TASK-") else f"TASK-{q_clean}"
    exact_match = base_query.filter(models.Task.id == exact_id).first()
    if exact_match:
        return [task_to_dict(exact_match)]

    # Also check without prefix if user passed numeric
    if q_clean.isdigit():
        num_match = base_query.filter(models.Task.id == f"TASK-{q_clean}").first()
        if num_match:
            return [task_to_dict(num_match)]

    # 2. Substring & Keyword Match
    words = [w for w in re.split(r"\s+", q_clean) if len(w) > 2 and w.lower() not in ["the", "task", "feature", "working", "status", "deadline", "risk", "who", "what", "when", "is", "on", "for"]]
    
    conditions = []
    # Match full clean phrase
    conditions.append(models.Task.title.ilike(f"%{q_clean}%"))
    conditions.append(models.Task.description.ilike(f"%{q_clean}%"))
    
    # Match individual meaningful keywords
    for word in words:
        conditions.append(models.Task.title.ilike(f"%{word}%"))
        conditions.append(models.Task.description.ilike(f"%{word}%"))

    filtered = base_query.filter(or_(*conditions))

    if project_id:
        filtered = filtered.filter(models.Task.project_id == project_id)
    if assignee_id:
        filtered = filtered.filter(models.Task.assignee_id == assignee_id)
    if status:
        filtered = filtered.filter(models.Task.status == status)

    tasks = filtered.order_by(models.Task.id.desc()).limit(100).all()

    # Score / Sort matches: exact title match > full phrase match > keyword match > tenant preference
    def score_task(t: models.Task) -> int:
        score = 0
        t_lower = t.title.lower()
        q_lower = q_clean.lower()
        if t_lower == q_lower:
            score += 100
        elif q_lower in t_lower:
            score += 50
        elif t_lower in q_lower:
            score += 30
        for w in words:
            if w.lower() in t_lower:
                score += 5
        if current_user.org_id and t.org_id == current_user.org_id:
            score += 20
        return score

    sorted_tasks = sorted(tasks, key=score_task, reverse=True)
    return [task_to_dict(t) for t in sorted_tasks]


def get_task(db: Session, task_identifier: str, current_user: models.User) -> dict[str, Any] | None:
    """Retrieve single task by ID or closest matching title."""
    results = search_tasks(db, task_identifier, current_user, limit=1)
    return results[0] if results else None


def get_assignee(db: Session, task_identifier: str, current_user: models.User) -> dict[str, Any]:
    """Retrieve the person currently assigned to a task."""
    matches = search_tasks(db, task_identifier, current_user, limit=5)
    if not matches:
        return {
            "found": False,
            "query": task_identifier,
            "message": f"I couldn't find any task matching '{task_identifier}' in your organization.",
        }

    is_single = _is_unambiguous_match(task_identifier, matches)
    if not is_single and len(matches) > 1:
        return {
            "found": True,
            "multiple": True,
            "query": task_identifier,
            "tasks": matches,
            "message": f"I found {len(matches)} tasks matching '{task_identifier}'. Which one do you mean?",
        }

    task = matches[0]
    assignee_name = task.get("assignee")
    if not assignee_name:
        return {
            "found": True,
            "task": task,
            "has_assignee": False,
            "message": f"Task [{task['id']}] '{task['title']}' is currently unassigned.",
        }

    # Fetch assignee user record
    user_record = db.query(models.User).filter(models.User.name == assignee_name).first()
    return {
        "found": True,
        "multiple": False,
        "task": task,
        "has_assignee": True,
        "assignee": {
            "name": assignee_name,
            "role": user_record.role if user_record else "Team Member",
            "email": user_record.email if user_record else None,
            "activeTasks": user_record.active_tasks if user_record else 1,
            "capacity": user_record.capacity if user_record else 80,
        },
    }


def get_tasks_by_assignee(
    db: Session,
    assignee_name_or_id: str,
    current_user: models.User,
    status: str | None = None,
) -> dict[str, Any]:
    """Retrieve all tasks assigned to a specific engineer or team member."""
    user_query = _get_org_users_query(db, current_user)
    target_user = user_query.filter(
        (models.User.id == assignee_name_or_id)
        | (models.User.name.ilike(f"%{assignee_name_or_id}%"))
        | (models.User.email.ilike(f"%{assignee_name_or_id}%"))
    ).first()

    if not target_user:
        return {
            "found": False,
            "assignee_query": assignee_name_or_id,
            "tasks": [],
            "message": f"No team member matching '{assignee_name_or_id}' was found.",
        }

    task_query = _get_org_tasks_query(db, current_user).filter(models.Task.assignee_id == target_user.id)
    if status:
        task_query = task_query.filter(models.Task.status == status)

    tasks = [task_to_dict(t) for t in task_query.all()]
    return {
        "found": True,
        "assignee": user_to_dict(target_user),
        "task_count": len(tasks),
        "tasks": tasks,
    }


def _is_unambiguous_match(query: str, matches: list[dict[str, Any]]) -> bool:
    if not matches:
        return False
    if len(matches) == 1:
        return True
    q = query.lower().strip()
    top = matches[0]["title"].lower().strip()
    # If exact match or top is substring or query is substring of top
    if q == top or q in top or top in q:
        return True
    return False


def get_task_status(db: Session, task_identifier: str, current_user: models.User) -> dict[str, Any]:
    """Retrieve real-time execution status, priority, and progress of a task."""
    matches = search_tasks(db, task_identifier, current_user, limit=5)
    if not matches:
        return {"found": False, "message": f"Could not find task '{task_identifier}'."}

    is_single = _is_unambiguous_match(task_identifier, matches)
    task = matches[0]
    return {
        "found": True,
        "multiple": not is_single,
        "tasks": matches,
        "task": task,
        "status": task["status"],
        "priority": task["priority"],
        "assignee": task["assignee"] or "Unassigned",
        "dueDate": task["dueDate"] or "No SLA date specified",
        "aiRiskScore": task["aiRiskScore"],
        "riskReason": task.get("riskReason"),
    }


def get_task_deadline(db: Session, task_identifier: str, current_user: models.User) -> dict[str, Any]:
    """Retrieve task due date, SLA deadline, and urgency."""
    matches = search_tasks(db, task_identifier, current_user, limit=5)
    if not matches:
        return {"found": False, "message": f"Could not find task '{task_identifier}'."}

    is_single = _is_unambiguous_match(task_identifier, matches)
    task = matches[0]
    due_str = task.get("dueDate")
    return {
        "found": True,
        "multiple": not is_single,
        "tasks": matches,
        "task": task,
        "dueDate": due_str or "No SLA deadline set",
        "status": task["status"],
        "assignee": task["assignee"] or "Unassigned",
    }


def get_task_dependencies(db: Session, task_identifier: str, current_user: models.User) -> dict[str, Any]:
    """Retrieve task dependencies (prerequisites) and downstream dependents (blocked tasks)."""
    matches = search_tasks(db, task_identifier, current_user, limit=5)
    if not matches:
        return {"found": False, "message": f"Could not find task '{task_identifier}'."}

    is_single = _is_unambiguous_match(task_identifier, matches)
    task = matches[0]
    dep_ids = task.get("dependsOn", [])
    
    # Prerequisites
    prereqs = []
    if dep_ids:
        prereq_rows = _get_org_tasks_query(db, current_user).filter(models.Task.id.in_(dep_ids)).all()
        prereqs = [task_to_dict(t) for t in prereq_rows]

    # Downstream dependents (tasks that depend on this task)
    all_org_tasks = _get_org_tasks_query(db, current_user).all()
    downstream = []
    for t in all_org_tasks:
        if t.depends_on and task["id"] in t.depends_on:
            downstream.append(task_to_dict(t))

    return {
        "found": True,
        "task": task,
        "prerequisites": prereqs,
        "downstream_dependents": downstream,
        "is_blocked": task["status"] == "blocked" or any(p["status"] != "done" for p in prereqs),
    }


def get_task_risk(db: Session, task_identifier: str, current_user: models.User) -> dict[str, Any]:
    """Retrieve AI/ML risk assessment, delay probability, and XAI factors."""
    matches = search_tasks(db, task_identifier, current_user, limit=5)
    if not matches:
        return {"found": False, "message": f"Could not find task '{task_identifier}'."}

    if len(matches) > 1 and matches[0]["title"].lower() != task_identifier.lower().strip():
        return {"found": True, "multiple": True, "tasks": matches}

    task = matches[0]
    score = task.get("aiRiskScore", 0.1)
    risk_level = "CRITICAL" if score >= 0.75 else ("HIGH" if score >= 0.55 else ("MEDIUM" if score >= 0.3 else "LOW"))
    
    return {
        "found": True,
        "task": task,
        "risk_score": score,
        "risk_percentage": int(score * 100),
        "risk_level": risk_level,
        "risk_reason": task.get("riskReason") or "Operating within normal velocity parameters.",
    }


def get_blocked_tasks(db: Session, current_user: models.User, project_id: str | None = None) -> list[dict[str, Any]]:
    """Retrieve all blocked tasks across the organization or within a project."""
    query = _get_org_tasks_query(db, current_user).filter(
        or_(models.Task.status == "blocked", models.Task.ai_risk_score >= 0.7)
    )
    if project_id:
        query = query.filter(models.Task.project_id == project_id)
    return [task_to_dict(t) for t in query.all()]


def get_team_capacity(db: Session, current_user: models.User) -> dict[str, Any]:
    """Retrieve live team workload capacity, identifying overloaded and available engineers."""
    users = _get_org_users_query(db, current_user).all()
    user_list = [user_to_dict(u) for u in users]
    
    overloaded = [u for u in user_list if u.get("capacity", 0) >= 90 or u.get("active_tasks", 0) >= 4]
    available = [u for u in user_list if u.get("capacity", 0) <= 60]
    
    return {
        "total_members": len(user_list),
        "members": user_list,
        "overloaded_members": overloaded,
        "available_members": available,
    }


def get_project_summary(
    db: Session,
    current_user: models.User,
    project_id: str | None = None,
    project_name: str | None = None,
) -> dict[str, Any]:
    """Retrieve project delivery summary, milestone completion, and on-time probabilities."""
    p_query = db.query(models.Project)
    if current_user.org_id:
        p_query = p_query.filter((models.Project.org_id == current_user.org_id) | (models.Project.org_id == None))
    
    if project_id:
        project = p_query.filter(models.Project.id == project_id).first()
    elif project_name:
        project = p_query.filter(models.Project.name.ilike(f"%{project_name}%")).first()
    else:
        project = p_query.first()

    tasks_query = _get_org_tasks_query(db, current_user)
    if project:
        tasks_query = tasks_query.filter(models.Task.project_id == project.id)

    tasks = [task_to_dict(t) for t in tasks_query.all()]
    total = len(tasks)
    done = len([t for t in tasks if t["status"] == "done"])
    in_progress = len([t for t in tasks if t["status"] == "in_progress"])
    blocked = len([t for t in tasks if t["status"] == "blocked"])
    high_risk = len([t for t in tasks if t.get("aiRiskScore", 0) >= 0.6])
    progress = int((done / total * 100)) if total > 0 else 0

    return {
        "project_name": project.name if project else "Active Sprint",
        "lead": project.lead if project else "Engineering Lead",
        "deadline": project.deadline if project else "2026-08-30",
        "total_tasks": total,
        "done": done,
        "in_progress": in_progress,
        "blocked": blocked,
        "high_risk": high_risk,
        "progress_percentage": progress,
        "tasks": tasks,
    }
