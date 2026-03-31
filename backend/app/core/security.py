from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt  # type: ignore[import-untyped]
from passlib.context import CryptContext  # type: ignore[import-untyped]

from app.core.config import get_settings
from app.core.exceptions import AppError

_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def create_token(data: dict[str, object], expires_delta: timedelta) -> str:
    to_encode: dict[str, object] = {**data}
    to_encode["exp"] = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(to_encode, get_settings().JWT_SECRET_KEY, algorithm=ALGORITHM)  # type: ignore[no-any-return]


def decode_token(token: str) -> dict[str, object]:
    try:
        payload: dict[str, object] = jwt.decode(
            token, get_settings().JWT_SECRET_KEY, algorithms=[ALGORITHM]
        )
    except JWTError as exc:
        raise AppError(status_code=401, detail="Invalid or expired token") from exc
    return payload


def hash_password(password: str) -> str:
    return _pwd_ctx.hash(password)  # type: ignore[no-any-return]


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_ctx.verify(plain, hashed)  # type: ignore[no-any-return]
