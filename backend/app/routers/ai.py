from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.services import ai_service

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/decompose", response_model=list[schemas.SubtaskOut])
def decompose(
    payload: schemas.DecomposeIn, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)
):
    """LLM-backed subtask decomposition (falls back to heuristics offline)."""
    subtasks = ai_service.decompose_task(payload.title, payload.description)
    return subtasks


@router.post("/decompose/{task_id}/apply", response_model=list[schemas.TaskOut])
def decompose_and_create(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Decompose an existing task with the LLM and persist the subtasks as
    new dependent Task rows (so they show up on the live graph)."""
    from app.routers.tasks import _next_task_id
    from app.serializers import task_to_dict

    parent = db.get(models.Task, task_id)
    if not parent:
        return []

    subtasks = ai_service.decompose_task(parent.title, parent.description or "")
    created = []
    for st in subtasks:
        t = models.Task(
            id=_next_task_id(db),
            title=st.get("title", "Subtask"),
            description="",
            project_id=parent.project_id,
            assignee_id=parent.assignee_id,
            status="in_progress",
            priority=st.get("priority", "Medium"),
            depends_on=[],
            due_date=parent.due_date,
            x=parent.x + 40,
            y=parent.y + 40,
            ai_risk_score=0.1,
        )
        db.add(t)
        db.flush()
        created.append(t)
    db.commit()
    for t in created:
        db.refresh(t)
    return [task_to_dict(t) for t in created]


@router.post("/forecast")
def forecast_sprint(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Run Monte Carlo simulation over the task graph to predict on-time delivery & SLA risks."""
    return ai_service.run_monte_carlo_sprint_forecast(db)


@router.post("/rebalance")
def get_rebalance_plan(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Compute optimal team workload rebalancing plan based on skill vectors & capacity."""
    return ai_service.compute_workload_rebalancing_plan(db)


@router.post("/query")
def query_agent_swarm(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Route natural language queries to specialized agents in the AI Swarm with decision trace."""
    from app.services.agent_orchestrator import swarm_orchestrator

    query_text = payload.get("query", "").strip()
    return swarm_orchestrator.route_query(query_text, current_user, db)


@router.get("/proposals")
def list_ai_proposals(
    status: str | None = None,
    _: models.User = Depends(get_current_user),
):
    """List pending or executed AI safe action proposals."""
    from app.services.agent_orchestrator import proposal_store

    return proposal_store.list_proposals(status=status)


@router.post("/proposals/{proposal_id}/approve")
def approve_ai_proposal(
    proposal_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Approve a pending action proposal, executing the database mutation safely."""
    from app.services.agent_orchestrator import proposal_store

    try:
        updated = proposal_store.approve_proposal(proposal_id, current_user, db)
        return {"status": "approved", "proposal": updated}
    except ValueError as e:
        return {"status": "error", "message": str(e)}


@router.post("/proposals/{proposal_id}/reject")
def reject_ai_proposal(
    proposal_id: str,
    current_user: models.User = Depends(get_current_user),
):
    """Reject and dismiss a pending action proposal without database changes."""
    from app.services.agent_orchestrator import proposal_store

    try:
        updated = proposal_store.reject_proposal(proposal_id, current_user)
        return {"status": "rejected", "proposal": updated}
    except ValueError as e:
        return {"status": "error", "message": str(e)}



