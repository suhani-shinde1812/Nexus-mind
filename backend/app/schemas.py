"""
Pydantic request/response schemas for Nexus Mind — Enterprise AI Engineering Operations Platform.
"""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field


# --------------------------------------------------------------------------
# Auth & MFA
# --------------------------------------------------------------------------
class RegisterIn(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)
    role: str = "Team Member"
    app_role: str = "employee"
    avatar: Optional[str] = None
    skills: list[str] = []


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    mfa_required: bool = False
    temp_token: Optional[str] = None


class RefreshIn(BaseModel):
    refresh_token: str


class MfaSetupOut(BaseModel):
    secret: str
    provisioning_uri: str


class MfaVerifyIn(BaseModel):
    code: str
    secret: Optional[str] = None
    temp_token: Optional[str] = None


class MfaEnableOut(BaseModel):
    status: str
    message: str
    backup_codes: list[str] = []



class UserSessionOut(BaseModel):
    id: str
    user_id: str
    user_agent: str
    ip_address: str
    is_revoked: bool
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


# --------------------------------------------------------------------------
# User
# --------------------------------------------------------------------------
class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str
    app_role: str
    avatar: str
    capacity: int
    active_tasks: int
    skills: list[str]
    mfa_enabled: bool = False

    class Config:
        from_attributes = True


class UserUpdateIn(BaseModel):
    capacity: Optional[int] = None
    active_tasks: Optional[int] = None
    role: Optional[str] = None
    skills: Optional[list[str]] = None


# --------------------------------------------------------------------------
# Project
# --------------------------------------------------------------------------
class ProjectOut(BaseModel):
    id: str
    name: str
    lead: str
    deadline: str
    progress: int

    class Config:
        from_attributes = True


class ProjectIn(BaseModel):
    name: str
    lead: str
    deadline: str
    progress: int = 0


# --------------------------------------------------------------------------
# Task & Comments
# --------------------------------------------------------------------------
class TaskCommentOut(BaseModel):
    id: str
    task_id: str
    author_id: str
    author_name: str
    author_avatar: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class TaskCommentIn(BaseModel):
    content: str


class TaskOut(BaseModel):
    id: str
    title: str
    description: str = ""
    project: Optional[str] = None
    assignee: Optional[str] = None
    status: str
    priority: str
    dependsOn: list[str] = Field(default_factory=list, alias="depends_on")
    x: float
    y: float
    dueDate: str = Field(default="", alias="due_date")
    aiRiskScore: float = Field(default=0.1, alias="ai_risk_score")
    riskReason: Optional[str] = Field(default=None, alias="risk_reason")
    comments_count: int = 0

    class Config:
        populate_by_name = True
        from_attributes = True


class TaskCreateIn(BaseModel):
    title: str
    description: str = ""
    project: Optional[str] = None
    assignee: Optional[str] = None
    status: str = "in_progress"
    priority: str = "Medium"
    dependsOn: list[str] = []
    dueDate: Optional[str] = None


class TaskStatusIn(BaseModel):
    status: str


class TaskDeadlineIn(BaseModel):
    dueDate: str


class TaskReassignIn(BaseModel):
    assignee: str


class TaskPositionIn(BaseModel):
    x: float
    y: float


class ReassignmentCandidate(BaseModel):
    id: str
    name: str
    role: str
    avatar: str
    capacity: int
    activeTasks: int
    skills: list[str]
    matchedSkills: list[str]
    skillMatch: bool
    similarity: float


# --------------------------------------------------------------------------
# AI & Decomposition
# --------------------------------------------------------------------------
class DecomposeIn(BaseModel):
    title: str
    description: str = ""
    project: Optional[str] = None


class SubtaskOut(BaseModel):
    title: str
    estimatedHours: float
    suggestedSkills: list[str] = []
    priority: str = "Medium"


class RiskScoreOut(BaseModel):
    taskId: str
    aiRiskScore: float
    riskReason: Optional[str]
    factors: dict[str, Any] = {}


# --------------------------------------------------------------------------
# RAG Knowledge Base & Documents
# --------------------------------------------------------------------------
class Citation(BaseModel):
    document_id: str
    document_title: str
    section: str
    page: int
    snippet: str
    score: float


class RagQueryIn(BaseModel):
    query: str
    top_k: int = 4
    category: Optional[str] = None


class RagQueryOut(BaseModel):
    query: str
    answer: str
    citations: list[Citation] = []
    agent: str = "Knowledge Agent"


class DocumentChunkOut(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    content: str
    page_number: int
    section_title: str

    class Config:
        from_attributes = True


class DocumentOut(BaseModel):
    id: str
    title: str
    filename: str
    file_type: str
    file_size_bytes: int
    summary: str
    uploaded_by: Optional[str] = None
    created_at: datetime
    chunk_count: int = 0

    class Config:
        from_attributes = True


# --------------------------------------------------------------------------
# Machine Learning & Simulation
# --------------------------------------------------------------------------
class SimulationIn(BaseModel):
    unavailable_members: list[str] = []
    scope_increase_tasks: int = 0
    added_developers: int = 0
    priority_shift_task_id: Optional[str] = None
    priority_shift_level: Optional[str] = None


class SimulationOut(BaseModel):
    baseline_days: float
    simulated_days: float
    delta_days: float
    on_time_probability: float
    new_bottlenecks: list[str] = []
    recommendations: list[str] = []


class MlRiskPredictionOut(BaseModel):
    task_id: str
    predicted_risk: float
    risk_level: str  # Low | Moderate | High | Critical
    confidence: float
    contributing_factors: dict[str, float]
    recommendation: str


# --------------------------------------------------------------------------
# Cybersecurity & Audit Logs
# --------------------------------------------------------------------------
class AuditLogOut(BaseModel):
    id: str
    actor_id: Optional[str] = None
    actor_name: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    ip_address: str
    user_agent: str
    details: dict[str, Any] = {}
    created_at: datetime

    class Config:
        from_attributes = True


class SecurityEventOut(BaseModel):
    id: str
    severity: str
    event_type: str
    description: str
    ip_address: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ThreatRadarOut(BaseModel):
    threat_score: int  # 0 - 100
    threat_level: str  # SECURE | ELEVATED | HIGH | CRITICAL
    active_threats_count: int
    failed_logins_24h: int
    recent_anomalies: list[SecurityEventOut] = []


# --------------------------------------------------------------------------
# GitHub / Engineering Intelligence
# --------------------------------------------------------------------------
class GithubIntegrationIn(BaseModel):
    repo_name: str
    repo_url: str
    branch: str = "main"


class GithubIntegrationOut(BaseModel):
    id: str
    repo_name: str
    repo_url: str
    branch: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class GithubEventOut(BaseModel):
    id: str
    integration_id: str
    event_type: str
    ref_number: Optional[str] = None
    title: str
    author: str
    status: str
    details: dict[str, Any] = {}
    created_at: datetime

    class Config:
        from_attributes = True


class EngineeringMetricsOut(BaseModel):
    repo_count: int
    open_prs_count: int
    avg_pr_cycle_time_hours: float
    commits_last_7d: int
    ci_success_rate: float
    deployment_frequency: str
    recent_events: list[GithubEventOut] = []


# --------------------------------------------------------------------------
# Meeting
# --------------------------------------------------------------------------
class MeetingOut(BaseModel):
    id: str
    title: str
    project: str
    date: str
    time: str
    duration: str
    attendees: list[str]
    agenda: str
    organizer: str
    status: str
    link: str
    ai_summary: Optional[str] = None
    action_items: list[str] = []

    class Config:
        from_attributes = True


class MeetingIn(BaseModel):
    title: str
    project: str = "General"
    date: str
    time: str
    duration: str = "30"
    attendees: list[str] = []
    agenda: str = ""


# --------------------------------------------------------------------------
# Policy & Alert
# --------------------------------------------------------------------------
class PolicyOut(BaseModel):
    id: str
    title: str
    category: str
    tags: list[str]
    summary: str

    class Config:
        from_attributes = True


class AlertOut(BaseModel):
    id: str
    severity: str
    title: str
    message: str
    taskId: Optional[str] = Field(default=None, alias="task_id")
    read: bool
    timestamp: datetime = Field(alias="created_at")

    class Config:
        populate_by_name = True
        from_attributes = True


class AlertIn(BaseModel):
    severity: str = "info"
    title: str
    message: str
    taskId: Optional[str] = None


# --------------------------------------------------------------------------
# Bootstrap
# --------------------------------------------------------------------------
class BootstrapOut(BaseModel):
    currentUser: UserOut
    users: list[UserOut]
    projects: list[ProjectOut]
    tasks: list[TaskOut]
    policies: list[PolicyOut]
    aiAlerts: list[AlertOut]
    meetings: list[MeetingOut]
    activityLogs: list[dict[str, Any]] = []
    systemStats: dict[str, Any]
    securityThreat: Optional[ThreatRadarOut] = None
    engineeringMetrics: Optional[EngineeringMetricsOut] = None
