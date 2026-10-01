"""
Enterprise database seeder for Nexus Mind.
Populates realistic demo data: Users, Projects, Tasks, Comments, Documents (with RAG chunks),
Security Events, Audit Logs, GitHub integrations, Policies, and Meetings.

Usage:
    python seed_data.py
"""
import sqlite3
from datetime import datetime

from app import models
from app.database import Base, SessionLocal, engine
from app.security import hash_password
from app.services.embeddings import embed

DEMO_PASSWORD = "nexus-demo-2026"

USERS = [
    dict(id="u1", name="Alex Vance", email="alex.vance@nexusmind.ai", role="Frontend Lead",
         app_role="employee", avatar="AV", capacity=80, active_tasks=3,
         skills=["Frontend", "React", "UI", "Dashboard", "Authorization"]),
    dict(id="u2", name="Sarah Jenkins", email="sarah.jenkins@nexusmind.ai", role="Team Lead",
         app_role="team_lead", avatar="SJ", capacity=60, active_tasks=2,
         skills=["Management", "Monitoring", "SLA", "Planning"]),
    dict(id="u3", name="Devon Reed", email="devon.reed@nexusmind.ai", role="Backend Engineer",
         app_role="employee", avatar="DR", capacity=110, active_tasks=5,
         skills=["Backend", "Database", "API", "Postgres", "Cache", "Terraform", "Infrastructure"]),
    dict(id="u4", name="Priya Sharma", email="priya.sharma@nexusmind.ai", role="AI/ML Engineer",
         app_role="employee", avatar="PS", capacity=40, active_tasks=1,
         skills=["AI", "ML", "Vector", "Search", "Python", "Websocket"]),
    dict(id="u5", name="Marcus Chen", email="marcus.chen@nexusmind.ai", role="Project Manager",
         app_role="project_manager", avatar="MC", capacity=50, active_tasks=2,
         skills=["Planning", "Coordination", "Reporting"]),
    dict(id="u6", name="Elena Rostova", email="elena.rostova@nexusmind.ai", role="Administrator",
         app_role="admin", avatar="ER", capacity=30, active_tasks=0,
         skills=["Security", "OAuth", "Compliance", "Infrastructure"]),
]

PROJECTS = [
    dict(id="p1", name="Sprint Alpha - Cloud Migration", lead="Sarah Jenkins", deadline="2026-08-15", progress=65),
    dict(id="p2", name="Mobile App v2.0", lead="Alex Vance", deadline="2026-09-01", progress=40),
    dict(id="p3", name="Security & Compliance", lead="Elena Rostova", deadline="2026-08-01", progress=90),
]

TASKS = [
    dict(id="TASK-101", title="Cloud Infrastructure Provisioning (Terraform)",
         project="Sprint Alpha - Cloud Migration", assignee="Devon Reed", status="done", priority="High",
         depends_on=[], x=120, y=180, due_date="2026-07-20", ai_risk_score=0.1, risk_reason=None),
    dict(id="TASK-102", title="PostgreSQL Database Schema & Migration Script",
         project="Sprint Alpha - Cloud Migration", assignee="Devon Reed", status="in_progress", priority="Critical",
         depends_on=["TASK-101"], x=300, y=140, due_date="2026-07-28", ai_risk_score=0.85,
         risk_reason="Devon Reed is at 110% capacity & SLA deadline approaching."),
    dict(id="TASK-103", title="OAuth2 Authentication API Gateway",
         project="Security & Compliance", assignee="Alex Vance", status="in_progress", priority="High",
         depends_on=["TASK-102"], x=480, y=140, due_date="2026-07-30", ai_risk_score=0.75,
         risk_reason="Prerequisite TASK-102 is at high risk of slipping."),
    dict(id="TASK-104", title="React Dashboard UI & Role Authorization Views",
         project="Mobile App v2.0", assignee="Alex Vance", status="blocked", priority="High",
         depends_on=["TASK-103"], x=660, y=200, due_date="2026-08-05", ai_risk_score=0.92,
         risk_reason="BLOCKED by TASK-103 which is delayed downstream."),
    dict(id="TASK-105", title="AI Assistant Vector Search Integration (Milvus)",
         project="Sprint Alpha - Cloud Migration", assignee="Priya Sharma", status="in_progress", priority="Medium",
         depends_on=["TASK-101"], x=300, y=320, due_date="2026-08-02", ai_risk_score=0.2, risk_reason=None),
    dict(id="TASK-106", title="Real-Time Notification Websocket Cluster",
         project="Mobile App v2.0", assignee="Devon Reed", status="blocked", priority="Medium",
         depends_on=["TASK-102", "TASK-105"], x=480, y=320, due_date="2026-08-08", ai_risk_score=0.8,
         risk_reason="Assignee Devon Reed has 5 assigned tasks simultaneously."),
    dict(id="TASK-107", title="Redis Caching Layer & Rate Limiter Middleware",
         project="Security & Compliance", assignee="Devon Reed", status="in_progress", priority="High",
         depends_on=["TASK-103"], x=660, y=340, due_date="2026-08-10", ai_risk_score=0.65,
         risk_reason="Depends on TASK-103 API Gateway."),
    dict(id="TASK-108", title="End-to-End System SLA Monitoring Dashboard",
         project="Sprint Alpha - Cloud Migration", assignee="Sarah Jenkins", status="in_progress", priority="Critical",
         depends_on=["TASK-104", "TASK-107"], x=840, y=260, due_date="2026-08-14", ai_risk_score=0.4,
         risk_reason="Final release milestone node."),
]

POLICIES = [
    dict(title="Remote Work Policy", category="HR & Operations", tags=["work", "policy", "remote"],
         summary="Flexible hybrid schedule requires mandatory daily standup updates and core working hours (10 AM - 4 PM IST)."),
    dict(title="SLA Escalation Guideline", category="Engineering & QA", tags=["sla", "critical", "bugs"],
         summary="P0 Critical Bugs must be acknowledged within 30 minutes and resolved within 24 hours with AI root-cause diagnostic reports."),
    dict(title="Security Secret Storage Policy", category="Infra & Security", tags=["oauth", "credentials", "vault"],
         summary="All production secrets and API credentials must be stored in HashiCorp Vault. Storing raw tokens in repo is strictly prohibited."),
]

ALERTS = [
    dict(severity="critical", title="Critical Path Hazard: Devon Reed",
         message="Devon Reed is assigned 5 concurrent tasks (110% capacity load). TASK-102 is blocking 3 downstream milestones.",
         task_id="TASK-102"),
    dict(severity="warning", title="Dependency SLA Delay",
         message="TASK-104 (React Dashboard UI) is currently BLOCKED by delayed OAuth2 API Gateway.", task_id="TASK-104"),
    dict(severity="info", title="AI Workload Rebalance Recommendation",
         message="Reassigning TASK-106 to Priya Sharma will reduce Devon Reed capacity load to 75% and unblock Sprint Alpha.",
         task_id="TASK-106"),
]

MEETINGS = [
    dict(id="MTG-1001", title="Sprint Alpha Standup & Blocker Review", project="Sprint Alpha - Cloud Migration",
         date="2026-08-11", time="10:00", duration="30", attendees=["Sarah Jenkins", "Devon Reed", "Priya Sharma"],
         agenda="Review TASK-102 database migration risk and unblock downstream tasks.", organizer="Sarah Jenkins",
         status="scheduled", link="https://meet.nexusmind.ai/sprint-alpha-standup"),
    dict(id="MTG-1002", title="Security & Compliance Sync", project="Security & Compliance",
         date="2026-08-12", time="15:30", duration="45", attendees=["Alex Vance", "Elena Rostova"],
         agenda="Walkthrough OAuth2 gateway rollout and secret storage policy compliance.", organizer="Elena Rostova",
         status="scheduled", link="https://meet.nexusmind.ai/security-compliance-sync"),
]


def sync_schema_columns(conn):
    """Ensure SQLite tables have all new enterprise columns."""
    cursor = conn.cursor()
    
    def add_col_if_missing(table, col, col_type):
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            cols = {row[1] for row in cursor.fetchall()}
            if cols and col not in cols:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
        except Exception:
            pass

    # Users
    add_col_if_missing("users", "org_id", "VARCHAR(36)")
    add_col_if_missing("users", "mfa_enabled", "BOOLEAN DEFAULT 0")
    add_col_if_missing("users", "mfa_secret", "VARCHAR(255)")
    add_col_if_missing("users", "mfa_backup_codes", "JSON DEFAULT '[]'")
    add_col_if_missing("users", "created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP")

    # Projects
    add_col_if_missing("projects", "org_id", "VARCHAR(36)")
    add_col_if_missing("projects", "created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP")

    # Tasks
    add_col_if_missing("tasks", "org_id", "VARCHAR(36)")
    add_col_if_missing("tasks", "created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP")
    add_col_if_missing("tasks", "updated_at", "DATETIME DEFAULT CURRENT_TIMESTAMP")
    add_col_if_missing("tasks", "completed_at", "DATETIME")

    # Document chunks
    add_col_if_missing("document_chunks", "org_id", "VARCHAR(36)")

    # Meetings
    add_col_if_missing("meetings", "org_id", "VARCHAR(36)")
    add_col_if_missing("meetings", "ai_summary", "TEXT")
    add_col_if_missing("meetings", "action_items", "JSON DEFAULT '[]'")
    add_col_if_missing("meetings", "created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP")

    conn.commit()


def seed():
    db_url = str(engine.url)
    if "sqlite" in db_url:
        import os
        db_path = db_url.replace("sqlite:///", "").replace("./", "")
        if os.path.exists(db_path):
            with sqlite3.connect(db_path) as raw_conn:
                sync_schema_columns(raw_conn)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Organization
        org = db.query(models.Organization).filter(models.Organization.slug == "default-org").first()
        if not org:
            org = models.Organization(name="Nexus Enterprise Corp", slug="default-org", plan="enterprise")
            db.add(org)
            db.flush()

        # Backfill org_id for existing records if null
        db.query(models.User).filter(models.User.org_id.is_(None)).update({"org_id": org.id})
        db.query(models.Project).filter(models.Project.org_id.is_(None)).update({"org_id": org.id})
        db.query(models.Task).filter(models.Task.org_id.is_(None)).update({"org_id": org.id})
        db.query(models.Document).filter(models.Document.org_id.is_(None)).update({"org_id": org.id})
        db.query(models.DocumentChunk).filter(models.DocumentChunk.org_id.is_(None)).update({"org_id": org.id})
        
        # Ensure all existing chunks use the latest dense continuous embeddings
        existing_chunks = db.query(models.DocumentChunk).all()
        for ch in existing_chunks:
            ch.embedding_vector = embed(ch.content)
            ch.org_id = org.id
        db.commit()


        if db.query(models.Task).count() == 0:
            name_to_id = {}
            for u in USERS:
                existing_u = db.query(models.User).filter(models.User.id == u["id"]).first()
                if not existing_u:
                    db.add(models.User(hashed_password=hash_password(DEMO_PASSWORD), org_id=org.id, **u))
                name_to_id[u["name"]] = u["id"]
            db.flush()

            for p in PROJECTS:
                existing_p = db.query(models.Project).filter(models.Project.id == p["id"]).first()
                if not existing_p:
                    db.add(models.Project(org_id=org.id, **p))
            db.flush()

            project_name_to_id = {p["name"]: p["id"] for p in PROJECTS}

            for t in TASKS:
                existing_t = db.query(models.Task).filter(models.Task.id == t["id"]).first()
                if not existing_t:
                    db.add(models.Task(
                        id=t["id"], title=t["title"],
                        org_id=org.id,
                        project_id=project_name_to_id.get(t["project"]),
                        assignee_id=name_to_id.get(t["assignee"]),
                        status=t["status"], priority=t["priority"], depends_on=t["depends_on"],
                        x=t["x"], y=t["y"], due_date=t["due_date"],
                        ai_risk_score=t["ai_risk_score"], risk_reason=t["risk_reason"],
                        completed_at=datetime.utcnow() if t["status"] == "done" else None,
                    ))

            for p in POLICIES:
                db.add(models.Policy(**p))

            for a in ALERTS:
                db.add(models.Alert(**a))

            for m in MEETINGS:
                db.add(models.Meeting(org_id=org.id, **m))

            # Task Comments
            db.add(models.TaskComment(
                task_id="TASK-102",
                author_id="u2",
                content="Devon, let me know once the Alembic migration script is ready so Alex can connect the OAuth schema.",
            ))
            db.add(models.TaskComment(
                task_id="TASK-102",
                author_id="u3",
                content="Underway! Ran initial dry-run against SQLite, testing Postgres pgvector compatibility next.",
            ))

            db.commit()

        # Seed Documents & RAG chunks if none exist
        if db.query(models.Document).count() == 0:
            doc1 = models.Document(
                org_id=org.id,
                title="Nexus Mind System Architecture Specification",
                filename="nexus_architecture_spec.md",
                file_type="md",
                file_size_bytes=14200,
                summary="Core architectural blueprint detailing FastAPI backend, WebSocket/Redis pubsub, and Multi-Agent Swarm.",
            )
            doc2 = models.Document(
                org_id=org.id,
                title="Enterprise Security & IAM Guidelines",
                filename="security_iam_sop.md",
                file_type="md",
                file_size_bytes=8900,
                summary="Standard operating procedures for JWT authentication, RFC 6238 TOTP Multi-Factor Authentication, and RBAC.",
            )
            db.add_all([doc1, doc2])
            db.flush()

            # Chunks for doc1
            chunks1 = [
                models.DocumentChunk(
                    document_id=doc1.id,
                    chunk_index=0,
                    content="Nexus Mind utilizes a unified single source of truth architecture over a Live Task Graph. Node dependencies are evaluated continuously by the AI Monitoring Agent to compute topological risk halos.",
                    page_number=1,
                    section_title="1. Core Live Task Graph",
                    embedding_vector=embed("Nexus Mind utilizes a unified single source of truth architecture over a Live Task Graph. Node dependencies are evaluated continuously by the AI Monitoring Agent."),
                ),
                models.DocumentChunk(
                    document_id=doc1.id,
                    chunk_index=1,
                    content="Realtime collaboration is powered by Redis Pub/Sub connected to asynchronous WebSocket broadcast managers. Any status change is synchronized in sub-100ms across all client sessions.",
                    page_number=1,
                    section_title="2. Realtime Synchronization",
                    embedding_vector=embed("Realtime collaboration is powered by Redis Pub/Sub connected to asynchronous WebSocket broadcast managers. Any status change is synchronized in sub-100ms."),
                ),
            ]
            # Chunks for doc2
            chunks2 = [
                models.DocumentChunk(
                    document_id=doc2.id,
                    chunk_index=0,
                    content="Authentication strictly enforces SHA-256 session token hashing, bcrypt password validation, and RFC 6238 TOTP Multi-Factor Authentication for sensitive roles.",
                    page_number=1,
                    section_title="1. Authentication & MFA",
                    embedding_vector=embed("Authentication strictly enforces SHA-256 session token hashing, bcrypt password validation, and RFC 6238 TOTP Multi-Factor Authentication."),
                ),
            ]
            db.add_all(chunks1 + chunks2)
            db.commit()

        # Seed Security Events & Audit Logs if none exist
        if db.query(models.SecurityEvent).count() == 0:
            db.add(models.SecurityEvent(
                org_id=org.id,
                severity="low",
                event_type="system_startup",
                description="Nexus Mind Enterprise Security Gateway initialized with zero threat anomalies.",
                ip_address="127.0.0.1",
            ))
            db.add(models.AuditLog(
                org_id=org.id,
                actor_name="System",
                action="system_boot",
                resource_type="system",
                ip_address="127.0.0.1",
                details={"version": "2.0.0", "status": "operational"},
            ))
            db.commit()

        # Seed GitHub Integration
        if db.query(models.GithubIntegration).count() == 0:
            from app.services.github_service import get_or_create_default_integration
            get_or_create_default_integration(db)

        print("Database seeded with Enterprise Organization, Users, Projects, Tasks, Documents, and GitHub telemetry.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
