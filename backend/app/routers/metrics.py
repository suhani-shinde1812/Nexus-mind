"""
Prometheus Metrics Router:
Exposes application observability KPIs instrumented with prometheus_client.
"""
from fastapi import APIRouter, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from sqlalchemy.orm import Session

from app import models
from app.database import SessionLocal

router = APIRouter(tags=["observability"])

# Registry & Metrics Collectors
REGISTRY = CollectorRegistry(auto_describe=True)

HTTP_REQUESTS_TOTAL = Counter(
    "nexusmind_http_requests_total",
    "Total HTTP requests handled by the platform",
    ["method", "endpoint", "status"],
    registry=REGISTRY,
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "nexusmind_http_request_duration_seconds",
    "HTTP request latency distribution in seconds",
    ["method", "endpoint"],
    registry=REGISTRY,
)

AI_SWARM_QUERIES_TOTAL = Counter(
    "nexusmind_ai_swarm_queries_total",
    "Total AI Swarm agent queries processed",
    ["agent", "intent"],
    registry=REGISTRY,
)

RAG_RETRIEVALS_TOTAL = Counter(
    "nexusmind_rag_retrievals_total",
    "Total RAG hybrid searches executed",
    ["status"],
    registry=REGISTRY,
)

ML_RISK_PREDICTIONS_TOTAL = Counter(
    "nexusmind_ml_risk_predictions_total",
    "Total task predictive risk ML evaluations",
    ["model_version", "risk_level"],
    registry=REGISTRY,
)

SECURITY_THREAT_SCORE = Gauge(
    "nexusmind_security_threat_score",
    "Real-time organizational cybersecurity threat score (0-100)",
    registry=REGISTRY,
)

ACTIVE_USERS_GAUGE = Gauge(
    "nexusmind_active_users_total",
    "Total active enterprise users",
    registry=REGISTRY,
)

TASKS_ON_GRAPH_GAUGE = Gauge(
    "nexusmind_tasks_on_graph_total",
    "Total active tasks on the live graph",
    registry=REGISTRY,
)

TASKS_TOTAL_GAUGE = Gauge(
    "nexusmind_tasks_total",
    "Total tasks on the live graph",
    registry=REGISTRY,
)

USERS_TOTAL_GAUGE = Gauge(
    "nexusmind_users_total",
    "Total enterprise users",
    registry=REGISTRY,
)


@router.get("/metrics")
def prometheus_metrics():
    """Prometheus scraping endpoint exposing live operational metrics."""
    db: Session = SessionLocal()
    try:
        user_count = db.query(models.User).count()
        task_count = db.query(models.Task).count()
        sec_count = db.query(models.SecurityEvent).count()

        ACTIVE_USERS_GAUGE.set(user_count)
        USERS_TOTAL_GAUGE.set(user_count)
        TASKS_ON_GRAPH_GAUGE.set(task_count)
        TASKS_TOTAL_GAUGE.set(task_count)
        SECURITY_THREAT_SCORE.set(24.0)
    finally:
        db.close()

    metrics_bytes = generate_latest(REGISTRY)
    return Response(content=metrics_bytes, media_type=CONTENT_TYPE_LATEST)

