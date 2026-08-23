"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-08-08

"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(80), server_default="Team Member"),
        sa.Column("app_role", sa.String(40), server_default="employee"),
        sa.Column("avatar", sa.String(8), server_default="NA"),
        sa.Column("capacity", sa.Integer, server_default="0"),
        sa.Column("active_tasks", sa.Integer, server_default="0"),
        sa.Column("skills", sa.JSON, server_default="[]"),
        sa.Column("is_active", sa.Boolean, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "projects",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("lead", sa.String(120)),
        sa.Column("deadline", sa.String(20)),
        sa.Column("progress", sa.Integer, server_default="0"),
    )

    op.create_table(
        "tasks",
        sa.Column("id", sa.String(20), primary_key=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text, server_default=""),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id"), nullable=True),
        sa.Column("assignee_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("status", sa.String(20), server_default="in_progress"),
        sa.Column("priority", sa.String(20), server_default="Medium"),
        sa.Column("depends_on", sa.JSON, server_default="[]"),
        sa.Column("x", sa.Float, server_default="400"),
        sa.Column("y", sa.Float, server_default="250"),
        sa.Column("due_date", sa.String(20), server_default=""),
        sa.Column("ai_risk_score", sa.Float, server_default="0.1"),
        sa.Column("risk_reason", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime, nullable=True),
    )

    op.create_table(
        "meetings",
        sa.Column("id", sa.String(40), primary_key=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("project", sa.String(200), server_default="General"),
        sa.Column("date", sa.String(20)),
        sa.Column("time", sa.String(10)),
        sa.Column("duration", sa.String(10), server_default="30"),
        sa.Column("attendees", sa.JSON, server_default="[]"),
        sa.Column("agenda", sa.Text, server_default=""),
        sa.Column("organizer", sa.String(120)),
        sa.Column("status", sa.String(20), server_default="scheduled"),
        sa.Column("link", sa.String(300), server_default=""),
    )

    op.create_table(
        "policies",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("category", sa.String(120)),
        sa.Column("tags", sa.JSON, server_default="[]"),
        sa.Column("summary", sa.Text, server_default=""),
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.String(40), primary_key=True),
        sa.Column("severity", sa.String(20), server_default="info"),
        sa.Column("title", sa.String(300)),
        sa.Column("message", sa.Text),
        sa.Column("task_id", sa.String(20), sa.ForeignKey("tasks.id"), nullable=True),
        sa.Column("read", sa.Boolean, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "task_history",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("task_id", sa.String(20), sa.ForeignKey("tasks.id"), nullable=False),
        sa.Column("event_type", sa.String(40)),
        sa.Column("from_value", sa.String(200), nullable=True),
        sa.Column("to_value", sa.String(200), nullable=True),
        sa.Column("actor_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "push_tokens",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token", sa.String(400), nullable=False, unique=True),
        sa.Column("platform", sa.String(20), server_default="android"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("push_tokens")
    op.drop_table("task_history")
    op.drop_table("alerts")
    op.drop_table("policies")
    op.drop_table("meetings")
    op.drop_table("tasks")
    op.drop_table("projects")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
