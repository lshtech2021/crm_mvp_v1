from __future__ import annotations

from datetime import datetime, time

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_role
from app.modules.audit.models import AuditLog
from app.modules.audit.schemas import AuditLogResponse, AuditQueryParams
from app.modules.auth.models import User

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/", response_model=list[AuditLogResponse])
async def list_audit_logs(
    params: AuditQueryParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> list[AuditLogResponse]:
    stmt = select(AuditLog).where(AuditLog.tenant_id == current_user.tenant_id)

    if params.actor_id is not None:
        stmt = stmt.where(AuditLog.actor_id == params.actor_id)
    if params.entity_type is not None:
        stmt = stmt.where(AuditLog.entity_type == params.entity_type)
    if params.entity_id is not None:
        stmt = stmt.where(AuditLog.entity_id == params.entity_id)
    if params.action_type is not None:
        stmt = stmt.where(AuditLog.action_type == params.action_type)
    if params.from_date is not None:
        stmt = stmt.where(AuditLog.timestamp >= datetime.combine(params.from_date, time.min))
    if params.to_date is not None:
        stmt = stmt.where(AuditLog.timestamp <= datetime.combine(params.to_date, time.max))

    stmt = (
        stmt.order_by(AuditLog.timestamp.desc())
        .offset((params.page - 1) * params.page_size)
        .limit(params.page_size)
    )

    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [AuditLogResponse.model_validate(r) for r in rows]
