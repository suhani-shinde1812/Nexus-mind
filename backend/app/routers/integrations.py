"""
Engineering Intelligence & GitHub Integrations Router:
- Repository integration registry
- HMAC-SHA256 Webhook Receiver & Idempotent Ingestion
- PR cycle time, commit frequency, CI pass rate, and delivery telemetry
- CI Auto-Triage: pattern matching, auto task creation, PR comment draft
"""
import json
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.services import github_service, github_triage_service

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


@router.get("/github/metrics", response_model=schemas.EngineeringMetricsOut)
def get_github_metrics(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Retrieve engineering productivity KPIs and GitHub activity stream."""
    return github_service.compute_engineering_metrics(db)


@router.post("/github/connect", response_model=schemas.GithubIntegrationOut, status_code=status.HTTP_201_CREATED)
def connect_github_repo(
    payload: schemas.GithubIntegrationIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Register repository integration for continuous engineering telemetry."""
    integ = models.GithubIntegration(
        org_id=current_user.org_id,
        repo_name=payload.repo_name,
        repo_url=payload.repo_url,
        branch=payload.branch,
        is_active=True,
    )
    db.add(integ)
    db.commit()
    db.refresh(integ)
    return schemas.GithubIntegrationOut(
        id=integ.id,
        repo_name=integ.repo_name,
        repo_url=integ.repo_url,
        branch=integ.branch,
        is_active=integ.is_active,
        created_at=integ.created_at,
    )


@router.post("/github/webhook", status_code=status.HTTP_200_OK)
async def receive_github_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_hub_signature_256: str | None = Header(None),
    x_github_event: str | None = Header("ping"),
    x_github_delivery: str | None = Header("default-delivery-id"),
):
    """
    Secure GitHub Webhook Receiver:
    - Validates HMAC-SHA256 signature against settings.github_webhook_secret
    - Idempotently ingests PR, push, and CI workflow events
    """
    raw_body = await request.body()

    # Validate HMAC signature
    if not github_service.verify_github_signature(raw_body, x_hub_signature_256):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid GitHub webhook HMAC-SHA256 signature",
        )

    try:
        payload = json.loads(raw_body.decode("utf-8")) if raw_body else {}
    except Exception:
        payload = {}

    event = github_service.process_webhook_payload(
        db,
        event_name=x_github_event or "push",
        delivery_id=x_github_delivery or "delivery-1",
        payload=payload,
    )

    # Auto-triage CI build failures
    triage_report = None
    if x_github_event in ["workflow_run", "check_run"] and event and event.status == "failed":
        failure_log = json.dumps(payload.get("workflow_run", payload.get("check_run", {})))
        triage_report = github_triage_service.analyse_ci_failure(db, event, failure_log)

    return {
        "status": "processed",
        "event_type": x_github_event,
        "delivery_id": x_github_delivery,
        "recorded_id": event.id if event else None,
        "triage_report": triage_report,
    }


@router.get("/github/triage/history")
def get_triage_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Return recent auto-triage tasks for the engineering intelligence feed."""
    return github_triage_service.get_triage_history(db, limit=limit)


@router.post("/github/triage/simulate")
def simulate_ci_failure(
    payload: dict,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """
    Manually trigger CI auto-triage engine for demo/testing.
    Accepts: { "error_log": "...", "build_ref": "BUILD-XXX", "title": "..." }
    """
    integ = github_service.get_or_create_default_integration(db)
    event = models.GithubEvent(
        integration_id=integ.id,
        event_type="ci_build",
        ref_number=payload.get("build_ref", "BUILD-DEMO"),
        title=payload.get("title", "Simulated CI Failure"),
        author="GitHub Actions",
        status="failed",
        details={"simulated": True},
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    failure_log = payload.get("error_log", "ModuleNotFoundError: No module named 'requests'")
    report = github_triage_service.analyse_ci_failure(db, event, failure_log)
    return report
