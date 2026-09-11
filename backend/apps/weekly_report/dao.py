"""Parameterized SQL read models for report lists and details."""

from __future__ import annotations

from typing import Any

from django.db import connection


def _fetch(sql: str, params: list[Any]) -> list[dict[str, Any]]:
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]


def list_reports(
    *, employee_ids: list[int], role_code: str | None = None, status: str | None = None
) -> list[dict[str, Any]]:
    if not employee_ids:
        return []
    placeholders = ",".join(["%s"] * len(employee_ids))
    clauses = [f"r.employee_id IN ({placeholders})"]
    params: list[Any] = [*employee_ids]
    if role_code:
        clauses.append("r.role_code = %s")
        params.append(role_code)
    if status:
        clauses.append("r.status = %s")
        params.append(status)
    return _fetch(
        f"""
        SELECT r.id, r.role_code, r.template_code, r.template_version, r.employee_id,
               r.group_id, r.period_type, r.month_key, r.period_start, r.period_end,
               r.as_of_date, r.status, r.summary, r.risk_level, r.risk_blocked,
               r.reviewer_id, r.review_comment, r.submitted_at, r.reviewed_at,
               r.created_at, r.updated_at, u.display_name AS employee_name,
               u.employee_no, g.group_name
        FROM weekly_report r
        LEFT JOIN user_account u ON u.id = r.employee_id
        LEFT JOIN organization_group g ON g.id = r.group_id
        WHERE {" AND ".join(clauses)}
        ORDER BY r.period_start DESC, r.updated_at DESC
        """,
        params,
    )


def get_report_header(report_id: int) -> dict[str, Any] | None:
    rows = _fetch(
        """
        SELECT r.id, r.role_code, r.template_code, r.template_version, r.employee_id,
               r.group_id, r.period_type, r.month_key, r.period_start, r.period_end,
               r.as_of_date, r.status, r.summary, r.risk_level, r.risk_blocked,
               r.risk_reason, r.next_action, r.support_needed, r.expected_resolve_date,
               r.reviewer_id, r.review_comment, r.submitted_at, r.reviewed_at,
               r.created_at, r.updated_at, u.display_name AS employee_name,
               u.employee_no, g.group_name
        FROM weekly_report r
        LEFT JOIN user_account u ON u.id = r.employee_id
        LEFT JOIN organization_group g ON g.id = r.group_id
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
               output_description, planned_completion_date, progress_text,
               progress_percent, quality_percent, completion_rate, on_time_status,
               actual_completion_date, delay_reason, next_action,
               expected_completion_date, owner_id, item_status, sort_order,
               created_at, updated_at
        FROM weekly_report_item
        WHERE report_id = %s
        ORDER BY sort_order, id
        """,
        [report_id],
    )


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


def get_report_evidence(report_id: int) -> list[dict[str, Any]]:
    return _fetch(
        """
        SELECT id, report_id, item_id, evidence_type, file_url, file_name,
               description, created_at
        FROM weekly_report_evidence
        WHERE report_id = %s
        ORDER BY id
        """,
        [report_id],
    )


def get_report_reviews(report_id: int) -> list[dict[str, Any]]:
    return _fetch(
        """
        SELECT rr.id, rr.report_id, rr.reviewer_id, rr.action, rr.comment,
               rr.created_at, u.display_name AS reviewer_name
        FROM weekly_report_review_record rr
        LEFT JOIN user_account u ON u.id = rr.reviewer_id
        WHERE rr.report_id = %s
        ORDER BY rr.created_at
        """,
        [report_id],
    )
