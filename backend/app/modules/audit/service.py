from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def emit_audit_event(
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
    """Dispatch an audit event to the Celery task queue.

    Gracefully degrades if the broker is unavailable (FR-017).
    """
    try:
        from app.modules.audit.tasks import write_audit_record

        write_audit_record.delay(
            tenant_id=tenant_id,
            actor_id=actor_id,
            actor_role=actor_role,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            changes=changes,
            ip_address=ip_address,
        )
    except Exception:
        logger.warning(
            "Failed to dispatch audit event %s to queue — graceful degradation",
            action_type,
            exc_info=True,
        )
