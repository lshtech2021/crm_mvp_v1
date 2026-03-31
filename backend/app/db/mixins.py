from __future__ import annotations

import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, declared_attr, mapped_column


class TenantMixin:
    @declared_attr
    @classmethod
    def tenant_id(cls) -> Mapped[uuid.UUID]:
        return mapped_column(sa.Uuid, nullable=False, index=True)


class TimestampMixin:
    @declared_attr
    @classmethod
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        )

    @declared_attr
    @classmethod
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        )


class SoftDeleteMixin:
    @declared_attr
    @classmethod
    def archived(cls) -> Mapped[bool]:
        return mapped_column(sa.Boolean, server_default=sa.text("false"), nullable=False)
