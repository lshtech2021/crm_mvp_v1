from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID | None
    actor_id: uuid.UUID | None
    actor_role: str | None
    entity_type: str
    entity_id: uuid.UUID | None
    action_type: str
    changes: dict[str, Any] | None
    ip_address: str | None
    timestamp: datetime

    model_config = {"from_attributes": True}


class AuditQueryParams(BaseModel):
    actor_id: uuid.UUID | None = None
    entity_type: str | None = None
    entity_id: uuid.UUID | None = None
    action_type: str | None = None
    from_date: date | None = None
    to_date: date | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=200)
