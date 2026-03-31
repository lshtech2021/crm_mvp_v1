from __future__ import annotations

import uuid
from types import SimpleNamespace

from app.core.permissions import ROLE_PERMISSIONS, check_ownership, check_permission


def test_admin_has_all_permissions() -> None:
    for perm in ROLE_PERMISSIONS["admin"]:
        assert check_permission("admin", perm), f"admin should have {perm}"


def test_manager_has_all_except_manage_users() -> None:
    for perm in ROLE_PERMISSIONS["manager"]:
        assert check_permission("manager", perm), f"manager should have {perm}"
    assert not check_permission("manager", "manage_users")


def test_rep_can_read_all() -> None:
    assert check_permission("rep", "read_all")


def test_rep_can_create() -> None:
    assert check_permission("rep", "create")


def test_rep_can_update_own() -> None:
    assert check_permission("rep", "update_own")


def test_rep_cannot_archive() -> None:
    assert not check_permission("rep", "archive")


def test_rep_cannot_update_any() -> None:
    assert not check_permission("rep", "update_any")


def test_viewer_read_only() -> None:
    assert check_permission("viewer", "read_all")
    assert check_permission("viewer", "view_reports")
    assert not check_permission("viewer", "create")
    assert not check_permission("viewer", "update_own")
    assert not check_permission("viewer", "update_any")
    assert not check_permission("viewer", "archive")
    assert not check_permission("viewer", "manage_users")


def test_check_ownership_contact_by_created_by() -> None:
    uid = uuid.uuid4()
    entity = SimpleNamespace(created_by=uid)
    assert check_ownership(uid, entity, "contact")


def test_check_ownership_deal_by_owner_id() -> None:
    uid = uuid.uuid4()
    entity = SimpleNamespace(owner_id=uid)
    assert check_ownership(uid, entity, "deal")


def test_check_ownership_task_by_assignee_id() -> None:
    uid = uuid.uuid4()
    entity = SimpleNamespace(assignee_id=uid)
    assert check_ownership(uid, entity, "task")


def test_check_ownership_fails_for_non_owner() -> None:
    uid = uuid.uuid4()
    other_uid = uuid.uuid4()
    entity = SimpleNamespace(created_by=other_uid)
    assert not check_ownership(uid, entity, "contact")
