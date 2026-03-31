from __future__ import annotations

import logging
import os
import uuid
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.modules.audit.models import AuditLog
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _get_sync_engine_url() -> str:
    """Derive a synchronous database URL from the async one."""
    url = os.getenv("DATABASE_URL", "postgresql+asyncpg://crm:crm@localhost:5432/crm")
    return url.replace("+asyncpg", "+psycopg2").replace("asyncpg://", "psycopg2://")


_sync_engine = create_engine(_get_sync_engine_url(), pool_pre_ping=True)


@celery_app.task(name="write_audit_record", bind=True, max_retries=3)  # type: ignore[misc]
def write_audit_record(
    self: Any,
    *,
    tenant_id: str | None,
    actor_id: str | None,
    actor_role: str | None,
    action_type: str,
    entity_type: str,
    entity_id: str | None,
    changes: dict[str, Any] | None = None,
    ip_address: str | None = None,
) -> None:
    if tenant_id is None:
        logger.warning("Rejecting audit record without tenant_id (TI-005)")
        return

    record = AuditLog(
        id=uuid.uuid4(),
        tenant_id=uuid.UUID(tenant_id),
        actor_id=uuid.UUID(actor_id) if actor_id else None,
        actor_role=actor_role,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=uuid.UUID(entity_id) if entity_id else None,
        changes=changes,
        ip_address=ip_address,
    )

    try:
        with Session(_sync_engine) as session:
            session.add(record)
            session.commit()
    except Exception as exc:
        logger.error("Failed to write audit record: %s", exc, exc_info=True)
        raise self.retry(exc=exc, countdown=2**self.request.retries)  # type: ignore[no-any-return]
