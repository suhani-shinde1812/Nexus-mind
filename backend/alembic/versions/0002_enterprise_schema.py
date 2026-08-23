"""Enterprise schema expansion: organizations, sessions, comments, RAG documents, audit, and security

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-22

"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Organizations
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
        sa.Column("plan", sa.String(40), server_default="enterprise"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # 2. Add Organization & MFA columns to existing users table
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id", name="fk_users_org_id"), nullable=True))
        batch_op.add_column(sa.Column("mfa_enabled", sa.Boolean, server_default=sa.false()))
        batch_op.add_column(sa.Column("mfa_secret", sa.String(255), nullable=True))
        batch_op.add_column(sa.Column("mfa_backup_codes", sa.JSON, server_default="[]"))

    # 3. Add Organization column to projects table
    with op.batch_alter_table("projects") as batch_op:
        batch_op.add_column(sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id", name="fk_projects_org_id"), nullable=True))

    # 4. Add Organization column to tasks table
    with op.batch_alter_table("tasks") as batch_op:
        batch_op.add_column(sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id", name="fk_tasks_org_id"), nullable=True))


    # 5. User Sessions
    op.create_table(
        "user_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("refresh_token_hash", sa.String(128), unique=True, nullable=False),
        sa.Column("user_agent", sa.String(300), server_default="Unknown Device"),
        sa.Column("ip_address", sa.String(60), server_default="127.0.0.1"),
        sa.Column("is_revoked", sa.Boolean, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime, nullable=False),
    )

    # 6. Task Comments
    op.create_table(
        "task_comments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("task_id", sa.String(20), sa.ForeignKey("tasks.id"), nullable=False),
        sa.Column("author_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # 7. Documents & Document Chunks (RAG Knowledge Engine)
    op.create_table(
        "documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("file_type", sa.String(20), server_default="pdf"),
        sa.Column("file_size_bytes", sa.Integer, server_default="0"),
        sa.Column("summary", sa.Text, server_default=""),
        sa.Column("uploaded_by_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "document_chunks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=True),
        sa.Column("document_id", sa.String(36), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("chunk_index", sa.Integer, server_default="0"),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("page_number", sa.Integer, server_default="1"),
        sa.Column("section_title", sa.String(200), server_default="General"),
        sa.Column("embedding_vector", sa.JSON, server_default="[]"),
    )

    # 8. Security Events & Audit Logs
    op.create_table(
        "security_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=True),
        sa.Column("event_type", sa.String(80), nullable=False),
        sa.Column("severity", sa.String(20), server_default="low"),
        sa.Column("actor_email", sa.String(255), nullable=True),
        sa.Column("ip_address", sa.String(60), server_default="127.0.0.1"),
        sa.Column("user_agent", sa.String(300), server_default=""),
        sa.Column("details", sa.JSON, server_default="{}"),
        sa.Column("resolved", sa.Boolean, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=True),
        sa.Column("action", sa.String(120), nullable=False),
        sa.Column("resource_type", sa.String(60), nullable=False),
        sa.Column("resource_id", sa.String(60), nullable=True),
        sa.Column("actor_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("actor_email", sa.String(255), server_default="system@nexusmind.ai"),
        sa.Column("ip_address", sa.String(60), server_default="127.0.0.1"),
        sa.Column("details", sa.JSON, server_default="{}"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # 9. GitHub Integration & Telemetry Events
    op.create_table(
        "github_integrations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=True),
        sa.Column("repo_name", sa.String(200), nullable=False),
        sa.Column("repo_url", sa.String(300), nullable=False),
        sa.Column("branch", sa.String(100), server_default="main"),
        sa.Column("is_active", sa.Boolean, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "github_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("integration_id", sa.String(36), sa.ForeignKey("github_integrations.id"), nullable=False),
        sa.Column("event_type", sa.String(40), nullable=False),
        sa.Column("ref_number", sa.String(60), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("author", sa.String(120), nullable=False),
        sa.Column("status", sa.String(40), server_default="merged"),
        sa.Column("details", sa.JSON, server_default="{}"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("github_events")
    op.drop_table("github_integrations")
    op.drop_table("audit_logs")
    op.drop_table("security_events")
    op.drop_table("document_chunks")
    op.drop_table("documents")
    op.drop_table("task_comments")
    op.drop_table("user_sessions")
    with op.batch_alter_table("tasks") as batch_op:
        batch_op.drop_column("org_id")
    with op.batch_alter_table("projects") as batch_op:
        batch_op.drop_column("org_id")
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("mfa_backup_codes")
        batch_op.drop_column("mfa_secret")
        batch_op.drop_column("mfa_enabled")
        batch_op.drop_column("org_id")
    op.drop_table("organizations")
