from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.models import AuditLog
from app.modules.auth.models import Tenant, User


async def test_user_sees_only_own_tenant_data(
    async_client: AsyncClient,
    db_session: AsyncSession,
    users: dict[str, User],
    tenants: dict[str, Tenant],
    auth_headers: object,
) -> None:
    acme = tenants["acme"]

    log = AuditLog(
        id=uuid.uuid4(),
        tenant_id=acme.id,
        actor_id=users["admin@acme.com"].id,
        actor_role="admin",
        action_type="test_isolation",
        entity_type="test",
        entity_id=uuid.uuid4(),
    )
    db_session.add(log)
    await db_session.commit()

    globex_admin = users["admin@globex.com"]
    headers = auth_headers(globex_admin)  # type: ignore[operator]
    resp = await async_client.get("/api/audit/", headers=headers)
    assert resp.status_code == 200
    for entry in resp.json():
        assert entry["tenant_id"] != str(acme.id)


async def test_url_id_injection(
    async_client: AsyncClient,
    db_session: AsyncSession,
    users: dict[str, User],
    tenants: dict[str, Tenant],
    auth_headers: object,
) -> None:
    """Auth as tenant B, attempt to filter audit logs by a tenant-A entity_id."""
    acme = tenants["acme"]
    entity_id = uuid.uuid4()

    log = AuditLog(
        id=uuid.uuid4(),
        tenant_id=acme.id,
        actor_id=users["admin@acme.com"].id,
        actor_role="admin",
        action_type="test_injection",
        entity_type="test",
        entity_id=entity_id,
    )
    db_session.add(log)
    await db_session.commit()

    globex_admin = users["admin@globex.com"]
    headers = auth_headers(globex_admin)  # type: ignore[operator]
    resp = await async_client.get(
        f"/api/audit/?entity_id={entity_id}",
        headers=headers,
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 0
