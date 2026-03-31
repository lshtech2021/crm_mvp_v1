from __future__ import annotations

from httpx import AsyncClient

from app.modules.auth.models import User


async def test_login_success(async_client: AsyncClient) -> None:
    resp = await async_client.post(
        "/api/auth/login",
        json={"email": "admin@acme.com", "password": "password123"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["user"]["email"] == "admin@acme.com"
    assert body["user"]["role"] == "admin"


async def test_login_invalid_password(async_client: AsyncClient) -> None:
    resp = await async_client.post(
        "/api/auth/login",
        json={"email": "admin@acme.com", "password": "wrong-password"},
    )
    assert resp.status_code == 401


async def test_login_invalid_email(async_client: AsyncClient) -> None:
    resp = await async_client.post(
        "/api/auth/login",
        json={"email": "nobody@acme.com", "password": "password123"},
    )
    assert resp.status_code == 401


async def test_refresh_success(async_client: AsyncClient) -> None:
    login_resp = await async_client.post(
        "/api/auth/login",
        json={"email": "admin@acme.com", "password": "password123"},
    )
    tokens = login_resp.json()

    resp = await async_client.post(
        "/api/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body


async def test_refresh_invalid_token(async_client: AsyncClient) -> None:
    resp = await async_client.post(
        "/api/auth/refresh",
        json={"refresh_token": "garbage.token.value"},
    )
    assert resp.status_code == 401


async def test_me_success(
    async_client: AsyncClient,
    users: dict[str, User],
    auth_headers: object,
) -> None:
    user = users["admin@acme.com"]
    headers = auth_headers(user)  # type: ignore[operator]
    resp = await async_client.get("/api/auth/me", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "admin@acme.com"
    assert body["role"] == "admin"
    assert body["tenant_id"] == str(user.tenant_id)


async def test_me_no_token(async_client: AsyncClient) -> None:
    resp = await async_client.get("/api/auth/me")
    assert resp.status_code == 401


async def test_logout_success(
    async_client: AsyncClient,
    users: dict[str, User],
    auth_headers: object,
) -> None:
    user = users["admin@acme.com"]
    headers = auth_headers(user)  # type: ignore[operator]
    resp = await async_client.post("/api/auth/logout", headers=headers)
    assert resp.status_code == 204
