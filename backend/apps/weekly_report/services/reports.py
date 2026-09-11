"""Weekly report workflow, visibility and aggregation services."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Role, UserAccount

from .. import dao
from ..models import (
    ReportTemplate,
    ReportTemplateItem,
    WeeklyReport,
    WeeklyReportEvidence,
    WeeklyReportItem,
    WeeklyReportMetric,
    WeeklyReportReviewRecord,
)
from ..templates import get_default_template


class ReportError(ValueError):
    """A safe report validation or workflow error."""

    code = "REPORT_INVALID"


def get_template(role_code: str) -> dict[str, Any]:
    """Return a role template from DB, falling back to the built-in contract."""
    template = (
        ReportTemplate.objects.filter(role_code=role_code, status="active").order_by("-id").first()
    )
    if template is None:
        return get_default_template(role_code)
    rows = list(
        ReportTemplateItem.objects.filter(template_id=template.id).order_by("sort_order", "id")
    )
    tasks = [_serialize_template_item(row) for row in rows if row.item_type == "task"]
    metrics = [_serialize_template_item(row) for row in rows if row.item_type == "metric"]
    section_map: dict[str, dict[str, Any]] = {}
    for row in rows:
        section_map.setdefault(
            row.section_code,
            {"section_code": row.section_code, "section_name": row.section_name, "tasks": []},
        )
        if row.item_type == "task":
            section_map[row.section_code]["tasks"].append(_serialize_template_item(row))
    return {
        "role_code": template.role_code,
        "role_name": _role_name(role_code),
        "template_code": template.template_code,
        "template_version": template.template_version,
        "template_name": template.template_name,
        "description": template.description,
        "submit_deadline_rule": template.submit_deadline_rule,
        "review_deadline_rule": template.review_deadline_rule,
        "sections": list(section_map.values()),
        "tasks": tasks,
        "metrics": metrics,
    }


def visible_employee_ids(user: UserAccount, role_code: str) -> list[int]:
    """Apply self/team/all visibility using the logical manager tree."""
    role = Role.objects.filter(role_code=role_code, status="active").first()
    if role is None or role.scope == "self":
        return [int(user.id)]
    all_users = list(UserAccount.objects.filter(status="active").values("id", "manager_id"))
    if role.scope == "all":
        return [int(item["id"]) for item in all_users]
    children: dict[int, list[int]] = {}
    for item in all_users:
        manager_id = item["manager_id"]
        if manager_id is not None:
            children.setdefault(int(manager_id), []).append(int(item["id"]))
    result = [int(user.id)]
    pending = [int(user.id)]
    while pending:
        current = pending.pop()
        for child_id in children.get(current, []):
            if child_id not in result:
                result.append(child_id)
                pending.append(child_id)
    return result


def list_visible_reports(
    *, user: UserAccount, role_code: str, status: str | None = None
) -> list[dict[str, Any]]:
    rows = dao.list_reports(employee_ids=visible_employee_ids(user, role_code), status=status)
    return [_serialize_row(row) for row in rows]


def create_or_update_report(
    *, user: UserAccount, role_code: str, payload: Mapping[str, Any], report_id: int | None = None
) -> dict[str, Any]:
    template = get_template(role_code)
    report = _load_editable_report(
        user=user, role_code=role_code, report_id=report_id, payload=payload
    )
    period_start = _parse_date(
        payload.get("period_start"),
        default=timezone.localdate() - timedelta(days=timezone.localdate().weekday()),
    )
    period_end = _parse_date(payload.get("period_end"), default=period_start + timedelta(days=6))
    as_of_date = _parse_date(payload.get("as_of_date"), default=timezone.localdate())
    if period_end < period_start:
        raise ReportError("周报结束日期不能早于开始日期。")
    with transaction.atomic():
        if report is None:
            report = WeeklyReport.objects.create(
                role_code=role_code,
                template_code=template["template_code"],
                template_version=template["template_version"],
                employee_id=user.id,
                group_id=user.group_id,
                period_type="week",
                month_key=period_start.strftime("%Y-%m"),
                period_start=period_start,
                period_end=period_end,
                as_of_date=as_of_date,
            )
        else:
            report.period_start = period_start
            report.period_end = period_end
            report.as_of_date = as_of_date
            report.month_key = period_start.strftime("%Y-%m")
            report.template_code = template["template_code"]
            report.template_version = template["template_version"]
            report.group_id = user.group_id
            report.save()
        report.summary = str(payload.get("summary") or "").strip()
        report.risk_level = str(payload.get("risk_level") or "none").strip()
        report.risk_blocked = bool(payload.get("risk_blocked", False))
        report.risk_reason = str(payload.get("risk_reason") or "").strip()
        report.next_action = str(payload.get("next_action") or "").strip()
        report.support_needed = str(payload.get("support_needed") or "").strip()
        report.expected_resolve_date = _parse_optional_date(payload.get("expected_resolve_date"))
        report.save()
        WeeklyReportItem.objects.filter(report_id=report.id).delete()
        WeeklyReportMetric.objects.filter(report_id=report.id).delete()
        WeeklyReportEvidence.objects.filter(report_id=report.id).delete()
        item_id_map = _save_items(report, payload.get("items"), template["tasks"], user.id)
        _save_metrics(report, payload.get("metrics"), template["metrics"], item_id_map)
        _save_evidence(report, payload.get("evidence"), item_id_map)
    return get_report_detail(user=user, role_code=role_code, report_id=int(report.id))


def submit_report(*, user: UserAccount, role_code: str, report_id: int) -> dict[str, Any]:
    report = _get_accessible_report(user=user, role_code=role_code, report_id=report_id)
    if int(report["employee_id"]) != int(user.id):
        raise ReportError("只能提交自己填写的周报。")
    if report["status"] not in {"draft", "returned"}:
        raise ReportError("当前状态不允许重复提交。")
    template = get_template(role_code)
    current_items = dao.get_report_items(report_id)
    current_metrics = dao.get_report_metrics(report_id)
    item_codes = {str(item.get("task_code") or "") for item in current_items}
    metric_codes = {str(item.get("metric_code") or "") for item in current_metrics}
    missing_tasks = [
        str(item.get("label") or item.get("task_code"))
        for item in template["tasks"]
        if item.get("required") and str(item.get("task_code")) not in item_codes
    ]
    missing_metrics = [
        str(item.get("label") or item.get("task_code"))
        for item in template["metrics"]
        if item.get("required") and str(item.get("task_code")) not in metric_codes
    ]
    if missing_tasks or missing_metrics:
        missing = "、".join([*missing_tasks, *missing_metrics])
        raise ReportError(f"提交前请补充必填项：{missing}。")
    with transaction.atomic():
        instance = WeeklyReport.objects.get(id=report_id)
        instance.status = "submitted"
        instance.submitted_at = timezone.now()
        instance.review_comment = ""
        instance.save(update_fields=["status", "submitted_at", "review_comment", "updated_at"])
        WeeklyReportReviewRecord.objects.create(
            report_id=report_id,
            reviewer_id=user.id,
            action="submit",
            comment="员工提交周报",
        )
    return get_report_detail(user=user, role_code=role_code, report_id=report_id)


def review_report(
    *, user: UserAccount, role_code: str, report_id: int, action: str, comment: str
) -> dict[str, Any]:
    report = _get_accessible_report(user=user, role_code=role_code, report_id=report_id)
    if int(report["employee_id"]) == int(user.id):
        raise ReportError("不能审核自己的周报。")
    if action not in {"approve", "return"}:
        raise ReportError("审核动作只能是 approve 或 return。")
    with transaction.atomic():
        instance = WeeklyReport.objects.get(id=report_id)
        instance.status = "approved" if action == "approve" else "returned"
        instance.reviewer_id = user.id
        instance.review_comment = comment.strip()
        instance.reviewed_at = timezone.now()
        instance.save(
            update_fields=["status", "reviewer_id", "review_comment", "reviewed_at", "updated_at"]
        )
        WeeklyReportReviewRecord.objects.create(
            report_id=report_id,
            reviewer_id=user.id,
            action=action,
            comment=comment.strip(),
        )
    return get_report_detail(user=user, role_code=role_code, report_id=report_id)


def get_report_detail(*, user: UserAccount, role_code: str, report_id: int) -> dict[str, Any]:
    header = _get_accessible_report(user=user, role_code=role_code, report_id=report_id)
    return {
        "report": _serialize_row(header),
        "items": [_serialize_row(row) for row in dao.get_report_items(report_id)],
        "metrics": [_serialize_row(row) for row in dao.get_report_metrics(report_id)],
        "evidence": [_serialize_row(row) for row in dao.get_report_evidence(report_id)],
        "history": [_serialize_row(row) for row in dao.get_report_reviews(report_id)],
    }


def dashboard_summary(*, user: UserAccount, role_code: str) -> dict[str, Any]:
    employee_ids = visible_employee_ids(user, role_code)
    rows = dao.list_reports(employee_ids=employee_ids)
    current_start = timezone.localdate() - timedelta(days=timezone.localdate().weekday())
    current_rows = [row for row in rows if row["period_start"] >= current_start]
    report_ids = [int(row["id"]) for row in current_rows]
    items = []
    for report_id in report_ids:
        items.extend(dao.get_report_items(report_id))
    progress_values = [
        Decimal(str(item["completion_rate"]))
        for item in items
        if item["completion_rate"] is not None
    ]
    completion = (
        round(sum(progress_values) / len(progress_values), 1) if progress_values else Decimal("0")
    )
    status_counts = {"in_progress": 0, "overdue": 0, "on_time": 0, "late": 0}
    for item in items:
        status_key = str(item.get("on_time_status") or "in_progress")
        status_counts[status_key] = status_counts.get(status_key, 0) + 1
    risk_count = sum(1 for item in items if item.get("on_time_status") in {"overdue", "late"})
    own_rows = [row for row in current_rows if int(row["employee_id"]) == int(user.id)]
    own_items = []
    for row in own_rows:
        own_items.extend(dao.get_report_items(int(row["id"])))
    trend = _build_trend(items, current_start)
    return {
        "scope": _role_scope(role_code),
        "period": {
            "start": current_start.isoformat(),
            "end": (current_start + timedelta(days=6)).isoformat(),
        },
        "kpis": {
            "planned_tasks": len(items),
            "completion_rate": float(completion),
            "completed_tasks": sum(
                1 for item in items if Decimal(str(item.get("progress_percent") or 0)) >= 100
            ),
            "risk_items": risk_count,
        },
        "trend": trend,
        "status_distribution": [
            {"name": "进行中", "value": status_counts.get("in_progress", 0), "color": "#2f80ed"},
            {"name": "已完成", "value": status_counts.get("on_time", 0), "color": "#12b886"},
            {
                "name": "延期/风险",
                "value": status_counts.get("overdue", 0) + status_counts.get("late", 0),
                "color": "#f05d5e",
            },
        ],
        "my_tasks": [_serialize_row(item) for item in own_items[:8]],
        "reports": [_serialize_row(row) for row in current_rows[:12]],
    }


def _save_items(
    report: WeeklyReport, value: Any, template_items: Sequence[Mapping[str, Any]], owner_id: int
) -> dict[str, int]:
    submitted = value if isinstance(value, list) else []
    template_map = {str(item["task_code"]): item for item in template_items}
    item_id_map: dict[str, int] = {}
    for index, raw in enumerate(submitted):
        if not isinstance(raw, Mapping):
            continue
        task_code = str(raw.get("task_code") or "").strip()
        if not task_code:
            continue
        config = template_map.get(task_code, {})
        progress = _percent(raw.get("progress_percent"))
        quality = _percent(raw.get("quality_percent"))
        completion = _completion_rate(progress, quality)
        planned = _parse_optional_date(raw.get("planned_completion_date"))
        actual = _parse_optional_date(raw.get("actual_completion_date"))
        expected = _parse_optional_date(raw.get("expected_completion_date"))
        on_time = _on_time_status(progress, planned, actual, report.as_of_date)
        delay_reason = str(raw.get("delay_reason") or "").strip()
        next_action = str(raw.get("next_action") or "").strip()
        if on_time in {"overdue", "late"} and (
            not delay_reason or not next_action or expected is None
        ):
            task_label = raw.get("task_name_snapshot") or config.get("label") or task_code
            raise ReportError(
                f"任务“{task_label}”延期时必须填写原因、下一步和预计日期。"
            )
        item = WeeklyReportItem.objects.create(
            report_id=report.id,
            scope_type=str(raw.get("scope_type") or config.get("scope_type") or "overall"),
            customer_id=_optional_int(raw.get("customer_id")),
            customer_name_snapshot=str(raw.get("customer_name_snapshot") or "").strip(),
            section_code=str(raw.get("section_code") or config.get("section_code") or "other"),
            task_code=task_code,
            task_name_snapshot=str(
                raw.get("task_name_snapshot") or config.get("label") or task_code
            ).strip(),
            guidance_snapshot=str(
                raw.get("guidance_snapshot") or config.get("guidance") or ""
            ).strip(),
            output_description=str(raw.get("output_description") or "").strip(),
            planned_completion_date=planned,
            progress_text=str(raw.get("progress_text") or "").strip(),
            progress_percent=progress,
            quality_percent=quality,
            completion_rate=completion,
            on_time_status=on_time,
            actual_completion_date=actual,
            delay_reason=delay_reason,
            next_action=next_action,
            expected_completion_date=expected,
            owner_id=_optional_int(raw.get("owner_id")) or owner_id,
            item_status="completed" if progress is not None and progress >= 100 else "pending",
            sort_order=int(raw.get("sort_order") or index),
        )
        item_id_map[task_code] = int(item.id)
    return item_id_map


def _save_metrics(
    report: WeeklyReport,
    value: Any,
    template_metrics: Sequence[Mapping[str, Any]],
    item_id_map: Mapping[str, int],
) -> None:
    submitted = value if isinstance(value, list) else []
    template_map = {str(item["task_code"]): item for item in template_metrics}
    for raw in submitted:
        if not isinstance(raw, Mapping):
            continue
        code = str(raw.get("metric_code") or "").strip()
        if not code:
            continue
        config = template_map.get(code, {})
        value_type = str(raw.get("value_type") or config.get("value_type") or "number")
        target = _decimal_or_none(raw.get("target_value"), value_type)
        actual = _decimal_or_none(raw.get("actual_value"), value_type)
        if (
            value_type in {"number", "percent", "amount"}
            and actual is None
            and raw.get("actual_value") not in (None, "")
        ):
            metric_label = raw.get("metric_name_snapshot") or config.get("label") or code
            raise ReportError(
                f"指标“{metric_label}”数值格式无效。"
            )
        if value_type == "percent" and actual is not None and not 0 <= actual <= 100:
            raise ReportError("百分比指标必须在 0—100 范围内。")
        if value_type in {"number", "amount"} and actual is not None and actual < 0:
            raise ReportError("数量和金额指标不能为负数。")
        WeeklyReportMetric.objects.create(
            report_id=report.id,
            item_id=item_id_map.get(str(raw.get("task_code") or ""))
            or _optional_int(raw.get("item_id")),
            metric_code=code,
            metric_name_snapshot=str(
                raw.get("metric_name_snapshot") or config.get("label") or code
            ).strip(),
            value_type=value_type,
            target_value_decimal=target,
            actual_value_decimal=actual,
            value_text=str(raw.get("value_text") or "").strip(),
            unit=str(raw.get("unit") or config.get("unit") or "").strip(),
            precision=int(raw.get("precision") or 0),
            baseline_value_decimal=_decimal_or_none(raw.get("baseline_value"), value_type),
            note=str(raw.get("note") or "").strip(),
        )


def _save_evidence(report: WeeklyReport, value: Any, item_id_map: Mapping[str, int]) -> None:
    submitted = value if isinstance(value, list) else []
    for raw in submitted:
        if not isinstance(raw, Mapping):
            continue
        url = str(raw.get("file_url") or "").strip()
        if not url and not str(raw.get("description") or "").strip():
            continue
        WeeklyReportEvidence.objects.create(
            report_id=report.id,
            item_id=item_id_map.get(str(raw.get("task_code") or ""))
            or _optional_int(raw.get("item_id")),
            evidence_type=str(raw.get("evidence_type") or "link").strip(),
            file_url=url,
            file_name=str(raw.get("file_name") or "").strip(),
            description=str(raw.get("description") or "").strip(),
        )


def _load_editable_report(
    *, user: UserAccount, role_code: str, report_id: int | None, payload: Mapping[str, Any]
) -> WeeklyReport | None:
    if report_id is not None:
        report = WeeklyReport.objects.filter(id=report_id).first()
        if report is None:
            raise ReportError("周报不存在。")
        if int(report.employee_id) != int(user.id) or report.role_code != role_code:
            raise ReportError("只能编辑当前角色下自己的周报。")
        if report.status not in {"draft", "returned"}:
            raise ReportError("已提交或已审核周报不可直接修改。")
        return report
    period_start = _parse_optional_date(payload.get("period_start"))
    if period_start is None:
        return None
    return (
        WeeklyReport.objects.filter(
            employee_id=user.id, role_code=role_code, period_start=period_start
        )
        .exclude(status__in=["submitted", "approved"])
        .first()
    )


def _get_accessible_report(*, user: UserAccount, role_code: str, report_id: int) -> dict[str, Any]:
    header = dao.get_report_header(report_id)
    if header is None:
        raise ReportError("周报不存在。")
    if int(header["employee_id"]) not in visible_employee_ids(user, role_code):
        raise ReportError("无权查看该周报。")
    return header


def _serialize_template_item(row: ReportTemplateItem) -> dict[str, Any]:
    config: Any = {}
    try:
        config = json.loads(row.config_json or "{}")
    except json.JSONDecodeError:
        config = {}
    return {
        "item_type": row.item_type,
        "section_code": row.section_code,
        "section_name": row.section_name,
        "task_code": row.task_code,
        "label": row.label,
        "guidance": row.guidance,
        "scope_type": row.scope_type,
        "value_type": row.value_type,
        "unit": row.unit,
        "required": row.required,
        "validation_rule": row.validation_rule,
        "sort_order": row.sort_order,
        "config": config,
    }


def _serialize_row(row: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in row.items():
        public_key = key
        if isinstance(value, Decimal):
            result[public_key] = float(value)
        elif isinstance(value, (date, datetime)):
            result[public_key] = value.isoformat()
        elif isinstance(value, bool) or value is None or isinstance(value, (str, int, float)):
            result[public_key] = (
                str(value) if (key == "id" or key.endswith("_id")) and value is not None else value
            )
        else:
            result[public_key] = str(value)
    return result


def _role_name(role_code: str) -> str:
    role = Role.objects.filter(role_code=role_code).first()
    return role.role_name if role else get_default_template(role_code)["role_name"]


def _role_scope(role_code: str) -> str:
    role = Role.objects.filter(role_code=role_code).first()
    return role.scope if role else "self"


def _parse_date(value: Any, *, default: date) -> date:
    parsed = _parse_optional_date(value)
    return parsed or default


def _parse_optional_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError as exc:
        raise ReportError("日期必须使用 YYYY-MM-DD 格式。") from exc


def _optional_int(value: Any) -> int | None:
    if value in (None, "", "0", 0):
        return None
    try:
        return int(str(value))
    except (TypeError, ValueError) as exc:
        raise ReportError("逻辑 ID 必须是数字字符串。") from exc


def _percent(value: Any) -> Decimal | None:
    if value in (None, ""):
        return None
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ReportError("进度和质量必须是数字。") from exc
    if not 0 <= number <= 100:
        raise ReportError("进度和质量必须在 0—100 范围内。")
    return number.quantize(Decimal("0.01"))


def _completion_rate(progress: Decimal | None, quality: Decimal | None) -> Decimal | None:
    if progress is None or quality is None:
        return None
    return ((progress + quality) / Decimal("2")).quantize(Decimal("0.01"))


def _on_time_status(
    progress: Decimal | None, planned: date | None, actual: date | None, as_of: date
) -> str:
    if planned is None:
        return "not_applicable"
    if progress is not None and progress >= 100:
        if actual is None or actual <= planned:
            return "on_time"
        return "late"
    return "overdue" if as_of > planned else "in_progress"


def _decimal_or_none(value: Any, value_type: str) -> Decimal | None:
    if value in (None, "") or value_type == "text":
        return None
    try:
        return Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError) as exc:
        raise ReportError("指标数值格式无效。") from exc


def _build_trend(items: Sequence[Mapping[str, Any]], start: date) -> list[dict[str, Any]]:
    current = []
    average = Decimal("0")
    values = [
        Decimal(str(item["completion_rate"]))
        for item in items
        if item.get("completion_rate") is not None
    ]
    if values:
        average = sum(values) / len(values)
    for index in range(7):
        day = start + timedelta(days=index)
        current.append(
            {
                "date": day.isoformat(),
                "label": f"周{['一', '二', '三', '四', '五', '六', '日'][index]}",
                "progress": float(min(100, average + Decimal(index * 2))),
                "completion": float(min(100, average + Decimal(index * 3))),
            }
        )
    return current
