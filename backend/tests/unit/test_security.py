from __future__ import annotations

from datetime import timedelta

import pytest

from app.core.exceptions import AppError
from app.core.security import create_token, decode_token, hash_password, verify_password


def test_hash_and_verify_password() -> None:
    hashed = hash_password("password123")
    assert verify_password("password123", hashed)


def test_verify_wrong_password() -> None:
    hashed = hash_password("password123")
    assert not verify_password("wrong-password", hashed)


def test_create_and_decode_token() -> None:
    data: dict[str, object] = {"sub": "user-42", "role": "admin"}
    token = create_token(data, expires_delta=timedelta(minutes=15))
    payload = decode_token(token)
    assert payload["sub"] == "user-42"
    assert payload["role"] == "admin"
    assert "exp" in payload


def test_expired_token_rejected() -> None:
    token = create_token({"sub": "user-42"}, expires_delta=timedelta(seconds=-10))
    with pytest.raises(AppError) as exc_info:
        decode_token(token)
    assert exc_info.value.status_code == 401


def test_invalid_token_rejected() -> None:
    with pytest.raises(AppError) as exc_info:
        decode_token("this.is.garbage")
    assert exc_info.value.status_code == 401
