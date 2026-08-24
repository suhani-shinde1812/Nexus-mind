"""
SQLAlchemy ORM models for Nexus Mind — Enterprise AI Engineering Operations Platform.
Supports PostgreSQL (with JSON & vector-ready fields) and SQLite seamlessly.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _uuid() -> str:
    return uuid.uuid4().hex


# --------------------------------------------------------------------------
# Multi-Tenancy / Organization
# --------------------------------------------------------------------------
class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, default="default-org")
    plan: Mapped[str] = mapped_column(String(40), default="enterprise")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    users: Mapped[list["User"]] = relationship(back_populates="organization")
    projects: Mapped[list["Project"]] = relationship(back_populates="organization")


# --------------------------------------------------------------------------
# User & Authentication
# --------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    org_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(80), default="Team Member")
    app_role: Mapped[str] = mapped_column(
        String(40), default="employee"
    )  # employee | team_lead | project_manager | admin
    avatar: Mapped[str] = mapped_column(String(8), default="NA")
    capacity: Mapped[int] = mapped_column(default=0)
    active_tasks: Mapped[int] = mapped_column(default=0)
    skills: Mapped[list] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    mfa_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Fernet encrypted
    mfa_backup_codes: Mapped[list] = mapped_column(JSON, default=list)  # SHA-256 hashed recovery codes
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    organization: Mapped["Organization | None"] = relationship(back_populates="users")
    fcm_tokens: Mapped[list["PushToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    sessions: Mapped[list["UserSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class UserSession(Base):
    """Tracks active login sessions for remote revocation & device audit."""
    __tablename__ = "user_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    refresh_token_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    user_agent: Mapped[str] = mapped_column(String(300), default="Unknown Device")
    ip_address: Mapped[str] = mapped_column(String(60), default="127.0.0.1")
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    user: Mapped["User"] = relationship(back_populates="sessions")


class PushToken(Base):
    """Firebase Cloud Messaging device tokens registered from the mobile app."""
    __tablename__ = "push_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    token: Mapped[str] = mapped_column(String(400), unique=True, nullable=False)
    platform: Mapped[str] = mapped_column(String(20), default="android")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="fcm_tokens")


# --------------------------------------------------------------------------
# Projects, Milestones & Tasks
# --------------------------------------------------------------------------
class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    org_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    lead: Mapped[str] = mapped_column(String(120))
    deadline: Mapped[str] = mapped_column(String(20))
    progress: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    organization: Mapped["Organization | None"] = relationship(back_populates="projects")
    tasks: Mapped[list["Task"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)  # e.g. TASK-101
    org_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    assignee_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="in_progress")
    priority: Mapped[str] = mapped_column(String(20), default="Medium")
    depends_on: Mapped[list] = mapped_column(JSON, default=list)  # list[str] task ids
    x: Mapped[float] = mapped_column(Float, default=400.0)
    y: Mapped[float] = mapped_column(Float, default=250.0)
    due_date: Mapped[str] = mapped_column(String(20), default="")
    ai_risk_score: Mapped[float] = mapped_column(Float, default=0.1)
    risk_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    project: Mapped["Project | None"] = relationship(back_populates="tasks")
    assignee: Mapped["User | None"] = relationship(foreign_keys=[assignee_id])
    comments: Mapped[list["TaskComment"]] = relationship(back_populates="task", cascade="all, delete-orphan")


class TaskComment(Base):
    """Realtime threaded comments with @mentions on tasks."""
    __tablename__ = "task_comments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    author_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    task: Mapped["Task"] = relationship(back_populates="comments")
    author: Mapped["User"] = relationship(foreign_keys=[author_id])


class TaskHistory(Base):
    """Append-only log of task lifecycle events."""
    __tablename__ = "task_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(40))  # created|status_change|reassigned|deadline_change|completed
    from_value: Mapped[str | None] = mapped_column(String(200), nullable=True)
    to_value: Mapped[str | None] = mapped_column(String(200), nullable=True)
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# --------------------------------------------------------------------------
# RAG Knowledge Base & Documents
# --------------------------------------------------------------------------
class Document(Base):
    """Uploaded technical architecture, SOP, or requirements docs."""
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    org_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), default="pdf")  # pdf | md | txt
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    summary: Mapped[str] = mapped_column(Text, default="")
    uploaded_by_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    chunks: Mapped[list["DocumentChunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    """Chunked passages with semantic embeddings for hybrid RAG search."""
    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    org_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, default=1)
    section_title: Mapped[str] = mapped_column(String(200), default="General")
    embedding_vector: Mapped[list] = mapped_column(JSON, default=list)

    document: Mapped["Document"] = relationship(back_populates="chunks")



# --------------------------------------------------------------------------
# Meetings & Video Collaboration
# --------------------------------------------------------------------------
class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: f"MTG-{_uuid()[:10]}")
    org_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    project: Mapped[str] = mapped_column(String(200), default="General")
    date: Mapped[str] = mapped_column(String(20))
    time: Mapped[str] = mapped_column(String(10))
    duration: Mapped[str] = mapped_column(String(10), default="30")
    attendees: Mapped[list] = mapped_column(JSON, default=list)
    agenda: Mapped[str] = mapped_column(Text, default="")
    organizer: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(20), default="scheduled")
    link: Mapped[str] = mapped_column(String(300), default="")
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_items: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# --------------------------------------------------------------------------
# Policies & Alerts
# --------------------------------------------------------------------------
class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(120))
    tags: Mapped[list] = mapped_column(JSON, default=list)
    summary: Mapped[str] = mapped_column(Text, default="")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=lambda: f"alt-{_uuid()[:10]}")
    org_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="info")
    title: Mapped[str] = mapped_column(String(300))
    message: Mapped[str] = mapped_column(Text)
    task_id: Mapped[str | None] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)



# --------------------------------------------------------------------------
# Cybersecurity, Audit & Anomaly Logs
# --------------------------------------------------------------------------
class AuditLog(Base):
    """Immutable log of organizational security and administrative actions."""
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    org_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    actor_name: Mapped[str] = mapped_column(String(120), default="System")
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(80), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(60), default="127.0.0.1")
    user_agent: Mapped[str] = mapped_column(String(300), default="API Client")
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SecurityEvent(Base):
    """Security events (brute force alerts, token anomalies, privilege escalations)."""
    __tablename__ = "security_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    org_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="warning")  # low | medium | high | critical
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    ip_address: Mapped[str] = mapped_column(String(60), default="127.0.0.1")
    status: Mapped[str] = mapped_column(String(20), default="open")  # open | resolved | dismissed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# --------------------------------------------------------------------------
# GitHub / GitLab Engineering Intelligence
# --------------------------------------------------------------------------
class GithubIntegration(Base):
    __tablename__ = "github_integrations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    org_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    repo_name: Mapped[str] = mapped_column(String(200), nullable=False)
    repo_url: Mapped[str] = mapped_column(String(300), nullable=False)
    branch: Mapped[str] = mapped_column(String(100), default="main")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    events: Mapped[list["GithubEvent"]] = relationship(back_populates="integration", cascade="all, delete-orphan")


class GithubEvent(Base):
    __tablename__ = "github_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    integration_id: Mapped[str] = mapped_column(ForeignKey("github_integrations.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(40))  # pr | commit | ci_build | issue
    ref_number: Mapped[str | None] = mapped_column(String(40), nullable=True)
    title: Mapped[str] = mapped_column(String(300))
    author: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(40), default="open")  # open | merged | passed | failed
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    integration: Mapped["GithubIntegration"] = relationship(back_populates="events")
