from __future__ import annotations

from httpx import AsyncClient

from app.modules.auth.models import User


async def test_admin_can_access_audit(
    async_client: AsyncClient,
    users: dict[str, User],
    auth_headers: object,
) -> None:
    headers = auth_headers(users["admin@acme.com"])  # type: ignore[operator]
    resp = await async_client.get("/api/audit/", headers=headers)
    assert resp.status_code == 200


async def test_non_admin_cannot_access_audit(
    async_client: AsyncClient,
    users: dict[str, User],
    auth_headers: object,
) -> None:
    headers = auth_headers(users["rep@acme.com"])  # type: ignore[operator]
    resp = await async_client.get("/api/audit/", headers=headers)
    assert resp.status_code == 403


async def test_viewer_cannot_post(
    async_client: AsyncClient,
    users: dict[str, User],
    auth_headers: object,
) -> None:
    """Viewer should be denied access to admin-only audit endpoint."""
    headers = auth_headers(users["viewer@acme.com"])  # type: ignore[operator]
    resp = await async_client.get("/api/audit/", headers=headers)
    assert resp.status_code == 403


async def test_viewer_can_get_me(
    async_client: AsyncClient,
    users: dict[str, User],
    auth_headers: object,
) -> None:
    headers = auth_headers(users["viewer@acme.com"])  # type: ignore[operator]
    resp = await async_client.get("/api/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["role"] == "viewer"
