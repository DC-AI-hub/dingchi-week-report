"""Organization and role administration services."""

from __future__ import annotations

import logging
import re
from collections.abc import Mapping
from typing import Any

from django.db import transaction

from ..dao import (
    deactivate_role_assignments,
    find_role_by_id,
    insert_role,
    list_roles,
    role_code_exists,
    save_role,
)
from ..models import OrganizationGroup, Role

_logger = logging.getLogger(__name__)
_role_code_pattern = re.compile(r"^[a-z][a-z0-9_]*$")
_role_scopes = {"self", "team", "all"}
_role_statuses = {"active", "inactive"}


class RoleNotFoundError(ValueError):
    """The requested role is missing or has already been deleted."""

    code = "ROLE_NOT_FOUND"


class RoleConflictError(ValueError):
    """The requested role operation would make administration unsafe."""

    code = "ROLE_CONFLICT"


@transaction.atomic
def create_role(*, payload: Mapping[str, Any]) -> Role:
    role_code = str(payload.get("role_code") or "").strip()
    role_name = str(payload.get("role_name") or "").strip()
    scope = str(payload.get("scope") or "self").strip()
    description = str(payload.get("description") or "").strip()
    report_template_code = str(payload.get("report_template_code") or "general_v1").strip()
    _validate_role_fields(
        role_code=role_code,
        role_name=role_name,
        scope=scope,
        report_template_code=report_template_code,
    )
    if len(description) > 255:
        raise ValueError("角色说明不能超过 255 个字符。")
    if role_code_exists(role_code):
        raise RoleConflictError("角色编码已存在，请使用其他编码。")
    return insert_role(
        role_code=role_code,
        role_name=role_name,
        scope=scope,
        description=description,
        report_template_code=report_template_code,
        sort_order=_parse_sort_order(payload.get("sort_order", 0)),
    )


@transaction.atomic
def update_role(*, role_id: int, payload: Mapping[str, Any]) -> Role:
    role = find_role_by_id(role_id)
    if role is None:
        raise RoleNotFoundError("角色不存在或已被删除。")

    role_name = str(payload.get("role_name", role.role_name) or "").strip()
    scope = str(payload.get("scope", role.scope) or "").strip()
    report_template_code = str(
        payload.get("report_template_code", role.report_template_code) or ""
    ).strip()
    description = str(payload.get("description", role.description) or "").strip()
    _validate_role_fields(
        role_code=role.role_code,
        role_name=role_name,
        scope=scope,
        report_template_code=report_template_code,
    )
    if len(description) > 255:
        raise ValueError("角色说明不能超过 255 个字符。")

    update_fields: list[str] = []
    for field, value in (
        ("role_name", role_name),
        ("scope", scope),
        ("description", description),
        ("report_template_code", report_template_code),
    ):
        if getattr(role, field) != value:
            setattr(role, field, value)
            update_fields.append(field)
    if "status" in payload:
        status = str(payload["status"] or "").strip()
        if status not in _role_statuses:
            raise ValueError("角色状态只能是 active 或 inactive。")
        if role.status != status:
            role.status = status
            update_fields.append("status")
    if "sort_order" in payload:
        sort_order = _parse_sort_order(payload["sort_order"])
        if role.sort_order != sort_order:
            role.sort_order = sort_order
            update_fields.append("sort_order")
    return save_role(role, update_fields=update_fields) if update_fields else role


@transaction.atomic
def delete_role(*, role_id: int, acting_role_code: str) -> Role:
    """Soft-delete one role and disable its logical user assignments."""
    role = find_role_by_id(role_id)
    if role is None:
        raise RoleNotFoundError("角色不存在或已被删除。")
    if role.role_code == "system_admin":
        raise RoleConflictError("系统管理员角色是系统保留角色，不能删除。")
    if role.role_code == acting_role_code:
        raise RoleConflictError("当前正在使用的角色不能删除，请先切换到其他角色。")

    role.status = "deleted"
    save_role(role, update_fields=["status"])
    assignment_count = deactivate_role_assignments(int(role.id))
    _logger.info(
        "Role soft-deleted",
        extra={
            "action": "delete_role",
            "role_id": str(role.id),
            "role_code": role.role_code,
            "assignment_count": assignment_count,
        },
    )
    return role


def get_role_list() -> list[dict[str, Any]]:
    """Return all role configurations that have not been deleted."""
    return list_roles()


def _validate_role_fields(
    *, role_code: str, role_name: str, scope: str, report_template_code: str
) -> None:
    if not role_code or not role_name or not report_template_code:
        raise ValueError("角色编码、角色名称和模板编码不能为空。")
    if len(role_code) > 64 or not _role_code_pattern.fullmatch(role_code):
        raise ValueError("角色编码必须以小写字母开头，只能包含小写字母、数字和下划线。")
    if len(role_name) > 128 or len(report_template_code) > 64:
        raise ValueError("角色名称或模板编码超过允许长度。")
    if scope not in _role_scopes:
        raise ValueError("数据范围只能是 self、team 或 all。")


def _parse_sort_order(value: Any) -> int:
    try:
        sort_order = int(value or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("角色排序值必须是非负整数。") from exc
    if sort_order < 0:
        raise ValueError("角色排序值必须是非负整数。")
    return sort_order


@transaction.atomic
def create_group(*, payload: Mapping[str, Any]) -> OrganizationGroup:
    group_code = str(payload.get("group_code") or "").strip()
    group_name = str(payload.get("group_name") or "").strip()
    if not group_code or not group_name:
        raise ValueError("分组编码和分组名称不能为空。")
    parent_group_id = payload.get("parent_group_id")
    return OrganizationGroup.objects.create(
        group_code=group_code,
        group_name=group_name,
        description=str(payload.get("description") or "").strip(),
        parent_group_id=int(parent_group_id) if parent_group_id else None,
    )


@transaction.atomic
def update_group(*, group: OrganizationGroup, payload: Mapping[str, Any]) -> OrganizationGroup:
    for field in ("group_name", "description", "status"):
        if field in payload:
            setattr(group, field, str(payload[field] or "").strip())
    if "parent_group_id" in payload:
        group.parent_group_id = (
            int(payload["parent_group_id"]) if payload["parent_group_id"] else None
        )
    group.save()
    return group


def can_manage_directory(role_code: str) -> bool:
    return role_code in {"president", "system_admin"}


def serialize_group(group: OrganizationGroup) -> dict[str, Any]:
    return {
        "id": str(group.id),
        "group_code": group.group_code,
        "group_name": group.group_name,
        "description": group.description,
        "parent_group_id": str(group.parent_group_id) if group.parent_group_id else None,
        "status": group.status,
    }
