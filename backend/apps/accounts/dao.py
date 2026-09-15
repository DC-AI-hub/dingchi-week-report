"""DAO queries for organization lists.

The list endpoints intentionally use one parameterized SQL statement for the
logical user/role/group association rather than leaking joins into Views.
"""

from __future__ import annotations

from typing import Any

from django.db import connection

from .models import Role, UserAccount, UserRole


def list_roles() -> list[dict[str, Any]]:
    """Return visible role configurations with a simple single-table ORM query."""
    return list(
        Role.objects.exclude(status="deleted")
        .order_by("sort_order", "id")
        .values(
            "id",
            "role_code",
            "role_name",
            "scope",
            "description",
            "report_template_code",
            "status",
            "sort_order",
        )
    )


def find_role_by_id(role_id: int) -> Role | None:
    """Find one non-deleted role for management operations."""
    return Role.objects.exclude(status="deleted").filter(id=role_id).first()


def role_code_exists(role_code: str) -> bool:
    """Check role-code uniqueness, including previously soft-deleted rows."""
    return Role.objects.filter(role_code=role_code).exists()


def insert_role(**values: Any) -> Role:
    """Persist a validated role definition."""
    return Role.objects.create(**values)


def save_role(role: Role, *, update_fields: list[str]) -> Role:
    """Persist changed role fields and return the same entity."""
    role.save(update_fields=[*update_fields, "updated_at"])
    return role


def deactivate_role_assignments(role_id: int) -> int:
    """Disable logical user-role assignments for a soft-deleted role."""
    return UserRole.objects.filter(role_id=role_id, status="active").update(
        status="inactive",
        is_default=False,
    )


def list_groups() -> list[dict[str, Any]]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, group_code, group_name, description, parent_group_id, status
            FROM organization_group
            WHERE status = %s
            ORDER BY group_code
            """,
            ["active"],
        )
        columns = [column[0] for column in cursor.description]
        items = [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]
        for item in items:
            item["id"] = str(item["id"])
            if item.get("parent_group_id") is not None:
                item["parent_group_id"] = str(item["parent_group_id"])
        return items


def list_users(
    *, role_code: str | None = None, group_id: str | None = None
) -> list[dict[str, Any]]:
    clauses = ["u.status = %s"]
    params: list[Any] = ["active"]
    if role_code:
        clauses.append("r.role_code = %s")
        params.append(role_code)
    if group_id:
        clauses.append("CAST(u.group_id AS CHAR) = %s")
        params.append(group_id)
    where_sql = " AND ".join(clauses)
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT u.id, u.username, u.employee_no, u.display_name, u.email,
                   u.manager_id, u.group_id, g.group_name, u.avatar_color, u.status,
                   GROUP_CONCAT(r.role_code) AS role_codes_csv,
                   GROUP_CONCAT(r.role_name) AS role_names_csv
            FROM user_account u
            LEFT JOIN organization_group g ON g.id = u.group_id
            LEFT JOIN user_role ur ON ur.user_id = u.id AND ur.status = %s
            LEFT JOIN role r ON r.id = ur.role_id AND r.status = %s
            WHERE {where_sql}
            GROUP BY u.id, u.username, u.employee_no, u.display_name, u.email,
                     u.manager_id, u.group_id, g.group_name, u.avatar_color, u.status
            ORDER BY u.employee_no
            """,
            ["active", "active", *params],
        )
        columns = [column[0] for column in cursor.description]
        rows = []
        for row in cursor.fetchall():
            item = dict(zip(columns, row, strict=False))
            item["id"] = str(item["id"])
            for field in ("manager_id", "group_id"):
                if item.get(field) is not None:
                    item[field] = str(item[field])
            item["role_codes"] = _split_group_values(item.pop("role_codes_csv", None))
            item["role_names"] = _split_group_values(item.pop("role_names_csv", None))
            rows.append(item)
        return rows


def list_user_options() -> list[dict[str, Any]]:
    """查询任务责任人和协作人下拉选项；只返回在职用户基础字段。"""
    rows = list(
        UserAccount.objects.filter(status="active")
        .order_by("employee_no", "id")
        .values("id", "employee_no", "display_name", "username", "group_id")
    )
    for row in rows:
        row["id"] = str(row["id"])
        if row.get("group_id") is not None:
            row["group_id"] = str(row["group_id"])
    return rows


def _split_group_values(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    return [part for part in str(value).split(",") if part]
