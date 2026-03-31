from __future__ import annotations

from typing import Any
from uuid import UUID

ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "admin": frozenset(
        {
            "create",
            "read_all",
            "update_any",
            "archive",
            "manage_users",
            "view_reports",
        }
    ),
    "manager": frozenset(
        {
            "create",
            "read_all",
            "update_any",
            "archive",
            "view_reports",
        }
    ),
    "rep": frozenset(
        {
            "create",
            "read_all",
            "update_own",
        }
    ),
    "viewer": frozenset(
        {
            "read_all",
            "view_reports",
        }
    ),
}

_OWNERSHIP_FIELDS: dict[str, str] = {
    "deal": "owner_id",
    "task": "assignee_id",
    "contact": "created_by",
    "company": "created_by",
}


def check_permission(role: str, operation: str) -> bool:
    allowed = ROLE_PERMISSIONS.get(role)
    if allowed is None:
        return False
    return operation in allowed


def check_ownership(user_id: UUID, entity: Any, entity_type: str) -> bool:
    field = _OWNERSHIP_FIELDS.get(entity_type)
    if field is None:
        return False
    owner_value = getattr(entity, field, None)
    if owner_value is None:
        return False
    return UUID(str(owner_value)) == user_id
