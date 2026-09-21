"""Parameterized SQL read models for report lists and details.

列表查询需要同时读取员工、分组和角色名称，属于多表关联查询，因此统一
通过参数化 SQL 完成；单表写入仍由 service 层使用 Django ORM 负责。
"""

from __future__ import annotations

from datetime import date
from typing import Any

from django.db import connection


def _fetch(sql: str, params: list[Any]) -> list[dict[str, Any]]:
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]


def _report_clauses(
    *,
    employee_ids: list[int],
    role_code: str | None = None,
    status: str | None = None,
    period_start: date | str | None = None,
    period_end: date | str | None = None,
    month_key: str | None = None,
    group_id: int | None = None,
) -> tuple[list[str], list[Any]]:
    if not employee_ids:
        return ["1 = 0"], []
    placeholders = ",".join(["%s"] * len(employee_ids))
    clauses = [f"r.employee_id IN ({placeholders})"]
    params: list[Any] = [*employee_ids]
    if role_code:
        clauses.append("r.role_code = %s")
        params.append(role_code)
    if status:
        clauses.append("r.status = %s")
        params.append(status)
    if period_start:
        clauses.append("r.period_start >= %s")
        params.append(period_start)
    if period_end:
        clauses.append("r.period_end <= %s")
        params.append(period_end)
    if month_key:
        clauses.append("r.month_key = %s")
        params.append(month_key)
    if group_id is not None:
        clauses.append("r.group_id = %s")
        params.append(group_id)
    return clauses, params


def _report_select() -> str:
    return """
        SELECT r.id, r.role_code, COALESCE(ro.role_name, r.role_code) AS role_name,
               r.template_code, r.employee_id,
               r.group_id, r.period_type, r.month_key, r.period_start, r.period_end,
               r.as_of_date, r.status, r.summary, r.risk_level, r.risk_blocked,
               r.created_at, r.updated_at, u.display_name AS employee_name,
               u.employee_no, g.group_name
        FROM weekly_report r
        LEFT JOIN user_account u ON u.id = r.employee_id
        LEFT JOIN organization_group g ON g.id = r.group_id
        LEFT JOIN role ro ON ro.role_code = r.role_code AND ro.status = 'active'
    """


def list_reports(
    *,
    employee_ids: list[int],
    role_code: str | None = None,
    status: str | None = None,
    period_start: date | str | None = None,
    period_end: date | str | None = None,
    month_key: str | None = None,
    group_id: int | None = None,
) -> list[dict[str, Any]]:
    """查询不分页的周报行，供驾驶舱聚合使用。"""
    clauses, params = _report_clauses(
        employee_ids=employee_ids,
        role_code=role_code,
        status=status,
        period_start=period_start,
        period_end=period_end,
        month_key=month_key,
        group_id=group_id,
    )
    return _fetch(
        f"{_report_select()} WHERE {' AND '.join(clauses)} "
        "ORDER BY r.period_start DESC, r.updated_at DESC",
        params,
    )


def list_reports_page(
    *,
    employee_ids: list[int],
    role_code: str | None = None,
    period_start: date | str | None = None,
    period_end: date | str | None = None,
    month_key: str | None = None,
    group_id: int | None = None,
    page: int = 1,
    page_size: int = 10,
) -> dict[str, Any]:
    """按页查询周报，并返回总数，供周报列表接口使用。"""
    clauses, params = _report_clauses(
        employee_ids=employee_ids,
        role_code=role_code,
        period_start=period_start,
        period_end=period_end,
        month_key=month_key,
        group_id=group_id,
    )
    where_sql = " AND ".join(clauses)
    count_rows = _fetch(
        f"SELECT COUNT(*) AS total FROM weekly_report r WHERE {where_sql}",
        params,
    )
    total = int(count_rows[0]["total"]) if count_rows else 0
    offset = (page - 1) * page_size
    rows = _fetch(
        f"{_report_select()} WHERE {where_sql} "
        "ORDER BY r.period_start DESC, r.updated_at DESC LIMIT %s OFFSET %s",
        [*params, page_size, offset],
    )
    total_pages = (total + page_size - 1) // page_size if total else 0
    return {
        "items": rows,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
    }


def get_report_header(report_id: int) -> dict[str, Any] | None:
    rows = _fetch(
        """
        SELECT r.id, r.role_code, COALESCE(ro.role_name, r.role_code) AS role_name,
               r.template_code, r.employee_id,
               r.group_id, r.period_type, r.month_key, r.period_start, r.period_end,
               r.as_of_date, r.status, r.summary, r.risk_level, r.risk_blocked,
               r.risk_reason, r.next_action, r.support_needed, r.expected_resolve_date,
               r.created_at, r.updated_at, u.display_name AS employee_name,
               u.employee_no, g.group_name
        FROM weekly_report r
        LEFT JOIN user_account u ON u.id = r.employee_id
        LEFT JOIN organization_group g ON g.id = r.group_id
        LEFT JOIN role ro ON ro.role_code = r.role_code AND ro.status = 'active'
        WHERE r.id = %s
        """,
        [report_id],
    )
    return rows[0] if rows else None


def get_report_items(report_id: int) -> list[dict[str, Any]]:
    return _fetch(
        """
        SELECT id, report_id, scope_type, customer_id, customer_name_snapshot,
               section_code, task_code, task_name_snapshot, guidance_snapshot,
               work_content, output_description, planned_completion_date, progress_text,
               progress_percent, quality_percent, completion_rate, on_time_status,
               actual_completion_date, delay_reason, next_action,
               expected_completion_date, owner_id, owner_name_snapshot,
               collaborator_names, document_links, item_status, sort_order,
               created_at, updated_at
        FROM weekly_report_item
        WHERE report_id = %s
        ORDER BY sort_order, id
        """,
        [report_id],
    )


def get_monthly_plan(employee_id: int, role_code: str, month_key: str) -> dict[str, Any] | None:
    """查询本人当前角色指定月度计划主表。"""
    rows = _fetch(
        """
        SELECT id, role_code, employee_id, group_id, month_key, summary,
               created_at, updated_at
        FROM monthly_plan
        WHERE employee_id = %s AND role_code = %s AND month_key = %s
        """,
        [employee_id, role_code, month_key],
    )
    return rows[0] if rows else None


def get_report_metrics(report_id: int) -> list[dict[str, Any]]:
    return _fetch(
        """
        SELECT id, report_id, item_id, metric_code, metric_name_snapshot, value_type,
               target_value_decimal, actual_value_decimal, value_text, unit,
               `precision`, baseline_value_decimal, note, created_at, updated_at
        FROM weekly_report_metric
        WHERE report_id = %s
        ORDER BY id
        """,
        [report_id],
    )


def get_report_attachments(report_id: int) -> list[dict[str, Any]]:
    """查询类型为周报且关联指定周报的系统通用附件。"""
    return _fetch(
        """
        SELECT id, attachment_type, relation_id, relation_sub_id, storage_key,
               file_url, file_name, mime_type, file_size, description,
               created_at, updated_at
        FROM system_attachment
        WHERE attachment_type = 'weekly_report' AND relation_id = %s
        ORDER BY created_at, id
        """,
        [report_id],
    )
