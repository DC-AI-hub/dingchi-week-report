from __future__ import annotations

import pytest

from apps.accounts.models import Role
from apps.accounts.services.organization import (
    RoleConflictError,
    RoleNotFoundError,
    create_role,
    delete_role,
    get_role_list,
)


@pytest.mark.django_db
def test_role_list_keeps_inactive_roles_but_hides_deleted_roles() -> None:
    inactive_role = Role.objects.create(
        role_code="inactive_role",
        role_name="停用角色",
        status="inactive",
    )
    Role.objects.create(
        role_code="deleted_role",
        role_name="已删除角色",
        status="deleted",
    )

    role_ids = {str(item["id"]) for item in get_role_list()}

    assert str(inactive_role.id) in role_ids
    assert all(item["role_code"] != "deleted_role" for item in get_role_list())


@pytest.mark.django_db
def test_create_role_rejects_duplicate_code() -> None:
    Role.objects.create(role_code="duplicate_role", role_name="原角色")

    with pytest.raises(RoleConflictError):
        create_role(payload={"role_code": "duplicate_role", "role_name": "重复角色"})


@pytest.mark.django_db
def test_delete_role_rejects_current_role_and_missing_role() -> None:
    role = Role.objects.create(role_code="president", role_name="总裁", scope="all")

    with pytest.raises(RoleConflictError):
        delete_role(role_id=int(role.id), acting_role_code="president")
    with pytest.raises(RoleNotFoundError):
        delete_role(role_id=999999, acting_role_code="system_admin")
