from __future__ import annotations

import enum
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin


class TenantStatus(str, enum.Enum):
    ACTIVE = "active"
    DEACTIVATED = "deactivated"


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    REP = "rep"
    VIEWER = "viewer"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    DEACTIVATED = "deactivated"


class Tenant(TimestampMixin, Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid, primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    slug: Mapped[str] = mapped_column(sa.String(100), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(
        sa.Enum(TenantStatus, name="tenant_status", create_type=True),
        server_default="active",
        nullable=False,
    )

    users: Mapped[list[User]] = relationship("User", back_populates="tenant", lazy="selectin")


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid, primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(sa.String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    role: Mapped[str] = mapped_column(
        sa.Enum(UserRole, name="user_role", create_type=True),
        nullable=False,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid, sa.ForeignKey("tenants.id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        sa.Enum(UserStatus, name="user_status", create_type=True),
        server_default="active",
        nullable=False,
    )

    tenant: Mapped[Tenant] = relationship("Tenant", back_populates="users", lazy="selectin")
