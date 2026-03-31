from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response
from slowapi import Limiter  # type: ignore[import-untyped]
from slowapi.util import get_remote_address  # type: ignore[import-untyped]
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.modules.auth.models import User
from app.modules.auth.schemas import (
    LoginRequest,
    RefreshRequest,
    TokenPairResponse,
    TokenResponse,
    UserResponse,
)
from app.modules.auth.service import (
    authenticate,
    create_access_token,
    create_refresh_token,
    rotate_refresh,
)

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    user = await authenticate(db, body.email, body.password)
    access = create_access_token(user)
    refresh = create_refresh_token(user)
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenPairResponse)
@limiter.limit("5/minute")
async def refresh(
    request: Request,
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenPairResponse:
    access, new_refresh = await rotate_refresh(db, body.refresh_token)
    return TokenPairResponse(access_token=access, refresh_token=new_refresh)


@router.post("/logout", status_code=204)
async def logout(
    current_user: User = Depends(get_current_user),
) -> Response:
    return Response(status_code=204)


@router.get("/me", response_model=UserResponse)
async def me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)
