"""Weekly report workflow, visibility and aggregation services."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from uuid import uuid4

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.db import IntegrityError, transaction
from django.db.utils import OperationalError, ProgrammingError
from django.utils import timezone
from django.utils.text import get_valid_filename

from apps.accounts.models import Role, UserAccount
from apps.core.models import Attachment
from apps.dictionary.public import list_active_dictionary_items

from .. import dao
from ..models import (
    MonthlyPlan,
    ReportTemplate,
    ReportTemplateItem,
    WeeklyReport,
    WeeklyReportEvidence,
    WeeklyReportItem,
    WeeklyReportMetric,
)
from ..templates import get_default_task_fields, get_default_template


class ReportError(ValueError):
    """A safe report validation or workflow error."""

    code = "REPORT_INVALID"


class ReportNotFoundError(ReportError):
    """The requested report does not exist."""

    code = "REPORT_NOT_FOUND"


class ReportConflictError(ReportError):
    """The requested report operation conflicts with an existing period."""

    code = "REPORT_CONFLICT"


class ReportPermissionError(ReportError):
    """The current role cannot access or mutate the report."""

    code = "FORBIDDEN"


REPORT_STATUS_ACTIVE = "active"
REPORT_STATUS_PENDING = "pending_activation"
REPORT_STATUS_ARCHIVED = "archived"


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
        "sections": list(section_map.values()),
        "tasks": tasks,
        "metrics": metrics,
        "fields": _get_template_fields(role_code),
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
    *,
    user: UserAccount,
    role_code: str,
    page: int = 1,
    page_size: int = 10,
    period_start: Any = None,
    period_end: Any = None,
    month_key: Any = None,
    group_id: Any = None,
    employee_scope: str | None = None,
) -> dict[str, Any]:
    """按当前角色作用域分页查询周报。

    self 角色只能查询本人；team 角色可切换本人或下属团队；all 角色查询
    全部人员。周期和分组筛选由接口统一转成逻辑 ID/日期后交给 DAO。
    """
    scope = _role_scope(role_code)
    employee_ids = visible_employee_ids(user, role_code)
    if employee_scope:
        if scope != "team" or employee_scope not in {"self", "team"}:
            raise ReportError("当前角色不支持该人员范围筛选。")
        if employee_scope == "self":
            employee_ids = [int(user.id)]
        else:
            employee_ids = [item for item in employee_ids if item != int(user.id)]
    if scope == "self" and group_id not in (None, ""):
        raise ReportError("个人周报不支持按分组筛选。")
    parsed_group_id = _optional_int(group_id)
    parsed_period_start = _parse_optional_date(period_start)
    parsed_period_end = _parse_optional_date(period_end)
    parsed_month_key = _parse_month_key(month_key)
    role_filter = role_code if scope == "self" or employee_scope == "self" else None
    if page < 1:
        raise ReportError("页码必须是大于 0 的整数。")
    if page_size < 1 or page_size > 100:
        raise ReportError("每页条数必须在 1—100 范围内。")
    result = dao.list_reports_page(
        employee_ids=employee_ids,
        role_code=role_filter,
        period_start=parsed_period_start,
        period_end=parsed_period_end,
        month_key=parsed_month_key,
        group_id=parsed_group_id,
        page=page,
        page_size=page_size,
    )
    result["items"] = [_serialize_report_row(row) for row in result["items"]]
    return result


def create_or_update_report(
    *, user: UserAccount, role_code: str, payload: Mapping[str, Any], report_id: int | None = None
) -> dict[str, Any]:
    if _role_scope(role_code) == "all":
        raise ReportPermissionError("全员数据角色仅支持查看周报。")
    template = get_template(role_code)
    current_start = _current_period_start()
    period_start = _parse_date(payload.get("period_start"), default=current_start)
    period_end = _parse_date(payload.get("period_end"), default=period_start + timedelta(days=6))
    as_of_date = _parse_date(payload.get("as_of_date"), default=timezone.localdate())
    if period_end < period_start:
        raise ReportError("周报结束日期不能早于开始日期。")
    if period_start.weekday() != 0:
        raise ReportError("周报周期必须从周一开始。")
    if period_end != period_start + timedelta(days=6):
        raise ReportError("周报周期结束日期必须是开始日期后的周日。")
    if period_start < current_start:
        raise ReportError("只能新增当前周报周期或未来周报周期。")
    report = _load_editable_report(
        user=user,
        role_code=role_code,
        report_id=report_id,
        period_start=period_start,
    )
    period_status = _period_status(period_start, period_end)
    with transaction.atomic():
        existing_attachments: list[Attachment] = []
        if report is not None:
            existing_attachments = list(
                Attachment.objects.filter(
                    attachment_type="weekly_report", relation_id=report.id
                ).order_by("created_at", "id")
            )
        if report is None:
            try:
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
                    status=period_status,
                )
            except IntegrityError as exc:
                raise ReportConflictError(
                    "该角色在此周报周期已有记录，请直接查看或编辑已有周报。"
                ) from exc
        else:
            # 当前周期可编辑，但周期本身不能被改成另一份周报。
            if report.period_start != period_start:
                raise ReportError("编辑周报时不能修改周报周期。")
            report.period_end = period_end
            report.as_of_date = as_of_date
            report.month_key = period_start.strftime("%Y-%m")
            report.template_code = template["template_code"]
            report.template_version = template["template_version"]
            report.group_id = user.group_id
            report.status = period_status
        report.summary = str(payload.get("summary") or "").strip()
        report.risk_level = str(payload.get("risk_level") or "none").strip()
        report.risk_blocked = bool(payload.get("risk_blocked", False))
        report.risk_reason = str(payload.get("risk_reason") or "").strip()
        report.next_action = str(payload.get("next_action") or "").strip()
        report.support_needed = str(payload.get("support_needed") or "").strip()
        report.expected_resolve_date = _parse_optional_date(payload.get("expected_resolve_date"))
        report.save()
        if isinstance(payload.get("monthly_plan"), Mapping):
            _save_monthly_plan(
                user=user,
                role_code=role_code,
                month_key=report.month_key,
                value=payload["monthly_plan"],
            )
        WeeklyReportItem.objects.filter(report_id=report.id).delete()
        WeeklyReportMetric.objects.filter(report_id=report.id).delete()
        WeeklyReportEvidence.objects.filter(report_id=report.id).delete()
        item_id_map = _save_items(report, payload.get("items"), template["tasks"], user.id)
        _save_metrics(report, payload.get("metrics"), template["metrics"], item_id_map)
        _save_evidence(report, payload.get("evidence"), item_id_map)
        _sync_attachments(
            value=payload.get("attachments"),
            item_id_map=item_id_map,
            existing=existing_attachments,
        )
    return get_report_detail(user=user, role_code=role_code, report_id=int(report.id))


def delete_report(*, user: UserAccount, role_code: str, report_id: int) -> dict[str, Any]:
    """删除本人当前周期周报及其逻辑关联明细。未来和历史周报只读。"""
    report = WeeklyReport.objects.filter(id=report_id).first()
    if _role_scope(role_code) == "all":
        raise ReportPermissionError("全员数据角色仅支持查看周报。")
    if report is None:
        raise ReportNotFoundError("周报不存在。")
    if int(report.employee_id) != int(user.id) or report.role_code != role_code:
        raise ReportPermissionError("只能删除当前角色下自己的周报。")
    if _period_status(report.period_start, report.period_end) != REPORT_STATUS_ACTIVE:
        raise ReportError("仅当前周报周期可以删除。")
    with transaction.atomic():
        WeeklyReportItem.objects.filter(report_id=report.id).delete()
        WeeklyReportMetric.objects.filter(report_id=report.id).delete()
        WeeklyReportEvidence.objects.filter(report_id=report.id).delete()
        for attachment in Attachment.objects.filter(
            attachment_type="weekly_report", relation_id=report.id
        ):
            _delete_attachment_record(attachment)
        report_id_text = str(report.id)
        report.delete()
    return {"id": report_id_text, "deleted": True}


def get_report_detail(*, user: UserAccount, role_code: str, report_id: int) -> dict[str, Any]:
    header = _get_accessible_report(user=user, role_code=role_code, report_id=report_id)
    return {
        "report": _serialize_report_row(header),
        "monthly_plan": get_monthly_plan(
            user=user,
            access_role_code=role_code,
            plan_role_code=str(header["role_code"]),
            month_key=str(header["month_key"]),
            employee_id=int(header["employee_id"]),
        ),
        "items": [_serialize_row(row) for row in dao.get_report_items(report_id)],
        "metrics": [_serialize_row(row) for row in dao.get_report_metrics(report_id)],
        "evidence": [_serialize_row(row) for row in dao.get_report_evidence(report_id)],
        "attachments": [_serialize_row(row) for row in dao.get_report_attachments(report_id)],
    }


def upload_report_attachment(
    *,
    user: UserAccount,
    role_code: str,
    report_id: int,
    uploaded_file: UploadedFile | None,
    item_id: Any = None,
    description: Any = "",
    attachment_type: Any = "weekly_report",
) -> dict[str, Any]:
    """上传本人当前或未来周报的附件，并写入系统通用附件表。"""
    if uploaded_file is None:
        raise ReportError("请选择附件。")
    report = WeeklyReport.objects.filter(id=report_id).first()
    if report is None:
        raise ReportNotFoundError("周报不存在。")
    if int(report.employee_id) != int(user.id) or report.role_code != role_code:
        raise ReportPermissionError("只能上传当前角色下自己的周报附件。")
    if _period_status(report.period_start, report.period_end) == REPORT_STATUS_ARCHIVED:
        raise ReportPermissionError("历史周报不能上传附件。")

    max_size = int(settings.ATTACHMENT_MAX_SIZE_BYTES)
    if uploaded_file.size is not None and uploaded_file.size > max_size:
        raise ReportError(f"附件大小不能超过 {max_size // (1024 * 1024)} MB。")
    original_name = Path(uploaded_file.name or "附件").name
    safe_name = get_valid_filename(original_name) or "attachment"
    extension = Path(safe_name).suffix.lower()
    allowed = {
        str(item).strip().lower()
        for item in settings.ATTACHMENT_ALLOWED_EXTENSIONS
        if str(item).strip()
    }
    if allowed and extension not in allowed:
        raise ReportError("附件类型不在允许范围内。")

    parsed_item_id = _optional_int(item_id)
    if parsed_item_id is not None and not WeeklyReportItem.objects.filter(
        id=parsed_item_id, report_id=report.id
    ).exists():
        raise ReportError("附件关联的任务不存在。")

    normalized_type = str(attachment_type or "weekly_report").strip()[:64] or "weekly_report"
    if normalized_type != "weekly_report":
        raise ReportError("当前接口只支持周报附件类型。")
    upload_dir = f"{str(settings.ATTACHMENT_UPLOAD_DIR).strip('/')}/{report.id}"
    storage_name = default_storage.save(
        f"{upload_dir}/{uuid4().hex}_{safe_name}",
        uploaded_file,
    )
    file_url = f"{str(settings.MEDIA_URL).rstrip('/')}/{storage_name}"
    try:
        attachment = Attachment.objects.create(
            attachment_type=normalized_type,
            relation_id=report.id,
            relation_sub_id=parsed_item_id,
            storage_key=storage_name,
            file_url=file_url,
            file_name=original_name,
            mime_type=str(uploaded_file.content_type or "application/octet-stream")[:128],
            file_size=int(uploaded_file.size or 0),
            description=str(description or "").strip(),
        )
    except Exception:
        # 数据库写入失败时删除已落盘文件，避免产生无法追踪的孤儿文件。
        default_storage.delete(storage_name)
        raise
    return _serialize_row(
        {
            "id": attachment.id,
            "attachment_type": attachment.attachment_type,
            "relation_id": attachment.relation_id,
            "relation_sub_id": attachment.relation_sub_id,
            "storage_key": attachment.storage_key,
            "file_url": attachment.file_url,
            "file_name": attachment.file_name,
            "mime_type": attachment.mime_type,
            "file_size": attachment.file_size,
            "description": attachment.description,
            "created_at": attachment.created_at,
            "updated_at": attachment.updated_at,
        }
    )


def get_monthly_plan(
    *,
    user: UserAccount,
    access_role_code: str,
    month_key: Any,
    employee_id: int | None = None,
    plan_role_code: str | None = None,
) -> dict[str, Any] | None:
    """返回指定月份计划；本人可读写，管理角色可随周报详情只读查看。"""
    parsed_month_key = _parse_month_key(month_key, required=True)
    target_employee_id = employee_id or int(user.id)
    if target_employee_id not in visible_employee_ids(user, access_role_code):
        raise ReportPermissionError("无权查看该员工的月度计划。")
    role_code = plan_role_code or access_role_code
    plan = dao.get_monthly_plan(target_employee_id, role_code, parsed_month_key)
    if plan is None:
        return None
    return _serialize_row(plan)


def save_monthly_plan(
    *, user: UserAccount, role_code: str, month_key: Any, summary: Any
) -> dict[str, Any]:
    """保存本人当前角色指定月份的单一月度计划文本。"""
    if _role_scope(role_code) == "all":
        raise ReportPermissionError("全员数据角色不支持编写月度计划。")
    parsed_month_key = _parse_month_key(month_key, required=True)
    with transaction.atomic():
        _save_monthly_plan(
            user=user,
            role_code=role_code,
            month_key=parsed_month_key,
            value={"summary": summary},
        )
    return get_monthly_plan(
        user=user,
        access_role_code=role_code,
        plan_role_code=role_code,
        month_key=parsed_month_key,
    ) or {
        "month_key": parsed_month_key,
        "summary": str(summary or "").strip(),
    }


def dashboard_summary(*, user: UserAccount, role_code: str) -> dict[str, Any]:
    employee_ids = visible_employee_ids(user, role_code)
    rows = dao.list_reports(employee_ids=employee_ids)
    current_start = timezone.localdate() - timedelta(days=timezone.localdate().weekday())
    current_rows = [
        _with_period_status(row)
        for row in rows
        if (_as_date(row.get("period_start")) or current_start) >= current_start
    ]
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


def _save_monthly_plan(
    *, user: UserAccount, role_code: str, month_key: str, value: Mapping[str, Any]
) -> None:
    summary = str(value.get("summary") or "").strip()
    plan, _ = MonthlyPlan.objects.get_or_create(
        employee_id=user.id,
        role_code=role_code,
        month_key=month_key,
        defaults={"group_id": user.group_id},
    )
    plan.group_id = user.group_id
    plan.summary = summary
    plan.save()


def _save_items(
    report: WeeklyReport, value: Any, template_items: Sequence[Mapping[str, Any]], owner_id: int
) -> dict[str, int]:
    submitted = value if isinstance(value, list) else []
    if report.role_code == "delivery_specialist" and not submitted:
        raise ReportError("本周工作至少需要一条任务。")
    template_map = {str(item["task_code"]): item for item in template_items}
    item_id_map: dict[str, int] = {}
    for index, raw in enumerate(submitted):
        if not isinstance(raw, Mapping):
            continue
        task_code = str(raw.get("task_code") or f"task_{index + 1}").strip()
        config = template_map.get(task_code, {})
        customer_name = str(raw.get("customer_name_snapshot") or "").strip()
        task_name = str(raw.get("task_name_snapshot") or config.get("label") or "").strip()
        if report.role_code == "delivery_specialist":
            if not customer_name:
                raise ReportError(f"本周工作第 {index + 1} 条任务客户不能为空。")
            if not task_name:
                raise ReportError(f"本周工作第 {index + 1} 条任务名称不能为空。")
        progress = _percent(raw.get("progress_percent"))
        quality = _percent(raw.get("quality_percent"))
        completion = _completion_rate(progress, quality)
        planned = _parse_optional_date(raw.get("planned_completion_date"))
        actual = _parse_optional_date(raw.get("actual_completion_date"))
        expected = _parse_optional_date(raw.get("expected_completion_date"))
        calculated_on_time = _on_time_status(progress, planned, actual, report.as_of_date)
        requested_on_time = str(raw.get("on_time_status") or "").strip()
        on_time = (
            requested_on_time
            if requested_on_time in {"in_progress", "on_time", "late", "overdue", "not_applicable"}
            else calculated_on_time
        )
        delay_reason = str(raw.get("delay_reason") or "").strip()
        next_action = str(raw.get("next_action") or "").strip()
        if on_time in {"overdue", "late"} and not delay_reason:
            task_label = raw.get("task_name_snapshot") or config.get("label") or task_code
            raise ReportError(f"任务“{task_label}”进度缓慢或延期时必须填写原因说明。")
        item = WeeklyReportItem.objects.create(
            report_id=report.id,
            scope_type=str(raw.get("scope_type") or config.get("scope_type") or "overall"),
            customer_id=_optional_int(raw.get("customer_id")),
            customer_name_snapshot=customer_name,
            section_code=str(raw.get("section_code") or config.get("section_code") or "other"),
            task_code=task_code,
            task_name_snapshot=task_name or task_code,
            guidance_snapshot=str(
                raw.get("guidance_snapshot") or config.get("guidance") or ""
            ).strip(),
            work_content=str(raw.get("work_content") or "").strip(),
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
            owner_name_snapshot=str(raw.get("owner_name_snapshot") or "").strip(),
            collaborator_names=str(raw.get("collaborator_names") or "").strip(),
            document_links=str(raw.get("document_links") or "").strip(),
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


def _sync_attachments(
    *, value: Any, item_id_map: Mapping[str, int], existing: Sequence[Attachment]
) -> None:
    """同步周报附件的任务关联和删除操作。

    文件上传由独立的 multipart 接口完成；周报保存只接收已有附件 ID，确保
    删除任务或移除附件时可以同步清理附件表中的逻辑关联。
    """
    # 兼容没有附件字段的旧客户端：不改变已有附件记录。
    if value is None:
        return
    submitted = value if isinstance(value, list) else []
    requested: dict[int, str] = {}
    for raw in submitted:
        if not isinstance(raw, Mapping):
            continue
        attachment_id = _optional_int(raw.get("id") or raw.get("attachment_id"))
        if attachment_id is None:
            continue
        requested[attachment_id] = str(raw.get("task_code") or "").strip()

    existing_by_id = {int(attachment.id): attachment for attachment in existing}
    unknown_ids = set(requested) - set(existing_by_id)
    if unknown_ids:
        raise ReportError("附件不存在或不属于当前周报。")

    for attachment in existing:
        attachment_id = int(attachment.id)
        if attachment_id not in requested:
            _delete_attachment_record(attachment)
            continue
        task_code = requested[attachment_id]
        if task_code:
            if task_code not in item_id_map:
                raise ReportError("附件关联的任务不存在。")
            attachment.relation_sub_id = item_id_map[task_code]
        else:
            attachment.relation_sub_id = None
        attachment.save(update_fields=["relation_sub_id", "updated_at"])


def _delete_attachment_record(attachment: Attachment) -> None:
    """删除附件记录并在事务提交后清理实际存储文件。"""
    storage_key = str(attachment.storage_key or "").strip()
    attachment.delete()
    if storage_key:
        transaction.on_commit(lambda: default_storage.delete(storage_key))


def _load_editable_report(
    *,
    user: UserAccount,
    role_code: str,
    report_id: int | None,
    period_start: date,
) -> WeeklyReport | None:
    if report_id is not None:
        report = WeeklyReport.objects.filter(id=report_id).first()
        if report is None:
            raise ReportNotFoundError("周报不存在。")
        if int(report.employee_id) != int(user.id) or report.role_code != role_code:
            raise ReportPermissionError("只能编辑当前角色下自己的周报。")
        if _period_status(report.period_start, report.period_end) != REPORT_STATUS_ACTIVE:
            raise ReportError("仅当前周报周期可以编辑。")
        return report
    if WeeklyReport.objects.filter(
        employee_id=user.id,
        role_code=role_code,
        period_start=period_start,
    ).exists():
        raise ReportConflictError("该角色在此周报周期已有记录，请直接查看或编辑已有周报。")
    return None


def _get_accessible_report(*, user: UserAccount, role_code: str, report_id: int) -> dict[str, Any]:
    header = dao.get_report_header(report_id)
    if header is None:
        raise ReportNotFoundError("周报不存在。")
    if _role_scope(role_code) == "self" and header.get("role_code") != role_code:
        raise ReportPermissionError("无权查看当前角色之外的周报。")
    if int(header["employee_id"]) not in visible_employee_ids(user, role_code):
        raise ReportPermissionError("无权查看该周报。")
    return _with_period_status(header)


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


def _serialize_report_row(row: Mapping[str, Any]) -> dict[str, Any]:
    """序列化周报并按周期动态计算三种业务状态。"""
    return _serialize_row(_with_period_status(row))


def _with_period_status(row: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(row)
    period_start = _as_date(result.get("period_start"))
    period_end = _as_date(result.get("period_end"))
    if period_start is not None and period_end is not None:
        result["status"] = _period_status(period_start, period_end)
    return result


def _current_period_start(value: date | None = None) -> date:
    current = value or timezone.localdate()
    return current - timedelta(days=current.weekday())


def _period_status(period_start: date, period_end: date) -> str:
    current_start = _current_period_start()
    if period_start > current_start:
        return REPORT_STATUS_PENDING
    if period_end < current_start:
        return REPORT_STATUS_ARCHIVED
    return REPORT_STATUS_ACTIVE


def _as_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if value in (None, ""):
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _role_name(role_code: str) -> str:
    role = Role.objects.filter(role_code=role_code).first()
    return role.role_name if role else get_default_template(role_code)["role_name"]


def _get_template_fields(role_code: str) -> list[dict[str, Any]]:
    """Load task-list columns from the role dictionary, with a safe fallback.

    ``system_dictionary`` is deliberately used instead of adding a schema
    table: each role gets an independent dictionary type, so its available
    columns, order and default visibility can evolve without coupling role
    templates.  The report API remains usable before the optional seed rows
    are loaded by returning the built-in Excel order.
    """
    fallback = get_default_task_fields(role_code)
    dict_type = f"weekly_report_fields_{role_code}"
    try:
        values = list_active_dictionary_items(dict_type)
    except (OperationalError, ProgrammingError, ValueError):
        return fallback
    if not values:
        return fallback
    fields: list[dict[str, Any]] = []
    for row in values:
        code = str(row.get("dict_code") or "").strip()
        label = str(row.get("dict_name") or "").strip()
        if not code or not label:
            continue
        value = str(row.get("dict_value") or "").strip().lower()
        fields.append(
            {
                "field_code": code,
                "label": label,
                "sort_order": int(row.get("sort_order") or len(fields) + 1),
                "default_visible": value not in {"0", "false", "no", "off"},
            }
        )
    return fields or fallback


def _role_scope(role_code: str) -> str:
    role = Role.objects.filter(role_code=role_code).first()
    return role.scope if role else "self"


def _parse_date(value: Any, *, default: date) -> date:
    parsed = _parse_optional_date(value)
    return parsed or default


def _parse_optional_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError as exc:
        raise ReportError("日期必须使用 YYYY-MM-DD 格式。") from exc


def _parse_month_key(value: Any, *, required: bool = False) -> str | None:
    if value in (None, ""):
        if required:
            raise ReportError("月度不能为空。")
        return None
    text = str(value).strip()
    try:
        datetime.strptime(text, "%Y-%m")
    except ValueError as exc:
        raise ReportError("月度必须使用 YYYY-MM 格式。") from exc
    return text


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
    if progress is None:
        return None
    if quality is None:
        return progress
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
