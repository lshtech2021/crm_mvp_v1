from __future__ import annotations

import logging
from unittest.mock import patch

from app.modules.audit.service import emit_audit_event


def test_emit_audit_event_dispatches_celery_task() -> None:
    with patch("app.modules.audit.tasks.write_audit_record") as mock_task:
        emit_audit_event(
            tenant_id="aaaa-bbbb",
            actor_id="cccc-dddd",
            actor_role="admin",
            action_type="create",
            entity_type="contact",
            entity_id="eeee-ffff",
            changes={"name": "new"},
            ip_address="127.0.0.1",
        )
        mock_task.delay.assert_called_once_with(
            tenant_id="aaaa-bbbb",
            actor_id="cccc-dddd",
            actor_role="admin",
            action_type="create",
            entity_type="contact",
            entity_id="eeee-ffff",
            changes={"name": "new"},
            ip_address="127.0.0.1",
        )


def test_emit_audit_event_graceful_on_failure() -> None:
    with patch("app.modules.audit.tasks.write_audit_record") as mock_task:
        mock_task.delay.side_effect = Exception("Broker unavailable")
        emit_audit_event(
            tenant_id="aaaa-bbbb",
            actor_id="cccc-dddd",
            actor_role="admin",
            action_type="create",
            entity_type="contact",
            entity_id="eeee-ffff",
        )


def test_write_audit_record_rejects_none_tenant_id(caplog: logging.LogCaptureFixture) -> None:
    from app.modules.audit.tasks import write_audit_record

    with caplog.at_level(logging.WARNING):
        write_audit_record(
            tenant_id=None,
            actor_id=None,
            actor_role=None,
            action_type="test_action",
            entity_type="test_entity",
            entity_id=None,
        )
    assert "tenant_id" in caplog.text.lower()
