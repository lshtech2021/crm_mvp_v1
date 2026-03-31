"""Initial schema — tenants, users, audit_logs, dashboard_snapshots

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-03-31
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "001_initial_schema"
down_revision: str | None = None
branch_labels: tuple[str, ...] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    tenant_status = sa.Enum("active", "deactivated", name="tenant_status")
    tenant_status.create(op.get_bind(), checkfirst=True)  # type: ignore[arg-type]

    user_role = sa.Enum("admin", "manager", "rep", "viewer", name="user_role")
    user_role.create(op.get_bind(), checkfirst=True)  # type: ignore[arg-type]

    user_status = sa.Enum("active", "deactivated", name="user_status")
    user_status.create(op.get_bind(), checkfirst=True)  # type: ignore[arg-type]

    deal_stage = sa.Enum(
        "qualification", "proposal", "negotiation", "closed_won", "closed_lost",
        name="deal_stage",
    )
    deal_stage.create(op.get_bind(), checkfirst=True)  # type: ignore[arg-type]

    task_priority = sa.Enum("low", "medium", "high", name="task_priority")
    task_priority.create(op.get_bind(), checkfirst=True)  # type: ignore[arg-type]

    task_status = sa.Enum("to_do", "in_progress", "done", name="task_status")
    task_status.create(op.get_bind(), checkfirst=True)  # type: ignore[arg-type]

    # --- tenants ---
    op.create_table(
        "tenants",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column(
            "status",
            sa.Enum("active", "deactivated", name="tenant_status", create_type=False),
            server_default="active",
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("tenants_slug_key", "tenants", ["slug"], unique=True)

    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column(
            "role",
            sa.Enum("admin", "manager", "rep", "viewer", name="user_role", create_type=False),
            nullable=False,
        ),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column(
            "status",
            sa.Enum("active", "deactivated", name="user_status", create_type=False),
            server_default="active",
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("users_email_key", "users", ["email"], unique=True)
    op.create_index("idx_users_tenant_email", "users", ["tenant_id", "email"])
    op.create_index("idx_users_tenant_role", "users", ["tenant_id", "role"])

    # --- audit_logs ---
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("actor_id", sa.Uuid(), nullable=True),
        sa.Column("actor_role", sa.String(20), nullable=True),
        sa.Column("tenant_id", sa.Uuid(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("action_type", sa.String(50), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.Uuid(), nullable=True),
        sa.Column("changes", JSONB(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
    )
    op.create_index("idx_audit_logs_tenant_timestamp", "audit_logs", ["tenant_id", "timestamp"])
    op.create_index("idx_audit_logs_tenant_entity", "audit_logs", ["tenant_id", "entity_type", "entity_id"])
    op.create_index("idx_audit_logs_tenant_actor", "audit_logs", ["tenant_id", "actor_id"])

    # --- dashboard_snapshots ---
    op.create_table(
        "dashboard_snapshots",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data", JSONB(), nullable=False),
    )
    op.create_index(
        "dashboard_snapshots_tenant_id_key", "dashboard_snapshots", ["tenant_id"], unique=True
    )


def downgrade() -> None:
    op.drop_table("dashboard_snapshots")
    op.drop_table("audit_logs")
    op.drop_table("users")
    op.drop_table("tenants")

    op.execute("DROP TYPE IF EXISTS task_status")
    op.execute("DROP TYPE IF EXISTS task_priority")
    op.execute("DROP TYPE IF EXISTS deal_stage")
    op.execute("DROP TYPE IF EXISTS user_status")
    op.execute("DROP TYPE IF EXISTS user_role")
    op.execute("DROP TYPE IF EXISTS tenant_status")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
