"""HTTP controllers for role-based weekly reports."""

from __future__ import annotations

import json
from typing import Any

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from apps.accounts.services.auth import AuthenticationError, require_request_user
from apps.core.http import api_error, api_success

from .services.reports import (
    ReportError,
    create_or_update_report,
    dashboard_summary,
    get_report_detail,
    get_template,
    list_visible_reports,
    review_report,
    submit_report,
)


def _json_payload(request: HttpRequest) -> dict[str, Any]:
    if not request.body:
        return {}
    value = json.loads(request.body)
    if not isinstance(value, dict):
        raise ValueError("请求体必须是 JSON 对象。")
    return value


def _error(exc: Exception) -> JsonResponse:
    if isinstance(exc, AuthenticationError):
        return api_error(exc.code, str(exc), status=401)
    if isinstance(exc, ReportError):
        return api_error(exc.code, str(exc), status=400)
    if isinstance(exc, json.JSONDecodeError):
        return api_error("INVALID_JSON", "请求体不是有效的 JSON。", status=400)
    if isinstance(exc, ValueError):
        return api_error("INVALID_REQUEST", str(exc), status=400)
    return api_error("INTERNAL_ERROR", "服务暂时不可用。", status=500)


@require_GET
def dashboard_view(request: HttpRequest) -> JsonResponse:
    """按当前激活角色返回驾驶舱 KPI、趋势、状态分布和可见周报。

    方法/路径：GET /api/v1/dashboard/summary/；认证：Bearer；参数：无；幂等：是。
    权限：个人仅自己，经理含下属，总裁/系统管理员含全部；成功响应为 dashboard JSON。
    失败：401 AUTHENTICATION_FAILED；追踪：响应带 X-Trace-ID；字段只增不改。
    """
    try:
        user, role_code = require_request_user(request)
        return api_success(dashboard_summary(user=user, role_code=role_code))
    except Exception as exc:
        return _error(exc)


@require_GET
def template_view(request: HttpRequest, role_code: str) -> JsonResponse:
    """获取某角色的可配置周报任务、指标和校验规则。

    方法/路径：GET /api/v1/weekly-report-templates/{role_code}/；认证：Bearer；参数：路径角色编码。
    成功响应：模板版本、模块、tasks、metrics；失败：401；响应带 X-Trace-ID，模板新增字段向后兼容。
    """
    try:
        require_request_user(request)
        return api_success(get_template(role_code))
    except Exception as exc:
        return _error(exc)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def report_list_view(request: HttpRequest) -> JsonResponse:
    """查询当前角色可见的周报列表或创建一份当前角色草稿。

    方法/路径：GET/POST /api/v1/weekly-reports/；认证：Bearer；
    GET 参数为可选 status，POST 参数为周报 JSON。
    GET 成功响应：data.items 为周报摘要数组；POST 成功响应：201 周报详情；权限按角色作用域过滤。
    失败：400/401；响应带 X-Trace-ID。
    """
    try:
        user, role_code = require_request_user(request)
        if request.method == "POST":
            return api_success(
                create_or_update_report(
                    user=user, role_code=role_code, payload=_json_payload(request)
                ),
                status=201,
            )
        return api_success(
            {
                "items": list_visible_reports(
                    user=user, role_code=role_code, status=request.GET.get("status")
                )
            }
        )
    except Exception as exc:
        return _error(exc)


@csrf_exempt
@require_POST
def report_create_view(request: HttpRequest) -> JsonResponse:
    """创建当前用户当前角色的周报草稿。

    方法/路径：POST /api/v1/weekly-reports/（兼容 /api/v1/weekly-reports/new/）；认证：Bearer；
    参数：周期、摘要、items、metrics、evidence JSON。
    成功响应：201 周报详情；失败：400 校验错误/401；响应带 X-Trace-ID，ID 为字符串。
    """
    try:
        user, role_code = require_request_user(request)
        return api_success(
            create_or_update_report(user=user, role_code=role_code, payload=_json_payload(request)),
            status=201,
        )
    except Exception as exc:
        return _error(exc)


@require_http_methods(["GET", "PATCH"])
def report_detail_view(request: HttpRequest, report_id: str) -> JsonResponse:
    """获取周报详情、任务、指标、佐证和审核历史。

    方法/路径：GET /api/v1/weekly-reports/{id}/；认证：Bearer；参数：路径 report_id；幂等：是。
    成功响应：report/items/metrics/evidence/history；失败：400/401；响应带 X-Trace-ID。
    """
    try:
        user, role_code = require_request_user(request)
        if request.method == "PATCH":
            return api_success(
                create_or_update_report(
                    user=user,
                    role_code=role_code,
                    payload=_json_payload(request),
                    report_id=int(report_id),
                )
            )
        return api_success(
            get_report_detail(user=user, role_code=role_code, report_id=int(report_id))
        )
    except Exception as exc:
        return _error(exc)


@csrf_exempt
@require_http_methods(["PATCH"])
def report_update_view(request: HttpRequest, report_id: str) -> JsonResponse:
    """保存自己草稿或退回周报的内容，系统重算完成率与按时状态。

    方法/路径：PATCH /api/v1/weekly-reports/{id}/；认证：Bearer；参数：部分/完整周报 JSON。
    成功响应：更新后的详情；失败：400/401；已提交或已审核周报不可修改；响应带 X-Trace-ID。
    """
    try:
        user, role_code = require_request_user(request)
        return api_success(
            create_or_update_report(
                user=user,
                role_code=role_code,
                payload=_json_payload(request),
                report_id=int(report_id),
            )
        )
    except Exception as exc:
        return _error(exc)


@csrf_exempt
@require_POST
def report_submit_view(request: HttpRequest, report_id: str) -> JsonResponse:
    """提交自己的周报进入负责人审核队列。

    方法/路径：POST /api/v1/weekly-reports/{id}/submit/；认证：Bearer；
    参数：路径 report_id；幂等：否。
    成功响应：提交后的详情；失败：400/401；响应带 X-Trace-ID，系统记录提交历史。
    """
    try:
        user, role_code = require_request_user(request)
        return api_success(submit_report(user=user, role_code=role_code, report_id=int(report_id)))
    except Exception as exc:
        return _error(exc)


@csrf_exempt
@require_POST
def report_review_view(request: HttpRequest, report_id: str) -> JsonResponse:
    """由经理、总裁或系统管理员审核周报并通过或退回。

    方法/路径：POST /api/v1/weekly-reports/{id}/review/；认证：Bearer；
    参数：action=approve/return、comment。
    成功响应：审核后的详情；失败：400/401；权限由角色可见范围控制；响应带 X-Trace-ID。
    """
    try:
        user, role_code = require_request_user(request)
        payload = _json_payload(request)
        return api_success(
            review_report(
                user=user,
                role_code=role_code,
                report_id=int(report_id),
                action=str(payload.get("action") or "").strip(),
                comment=str(payload.get("comment") or "").strip(),
            )
        )
    except Exception as exc:
        return _error(exc)


@require_GET
def report_history_view(request: HttpRequest, report_id: str) -> JsonResponse:
    """查询周报提交、退回和审核历史。

    方法/路径：GET /api/v1/weekly-reports/{id}/history/；认证：Bearer；
    参数：路径 report_id；幂等：是。
    成功响应：data.items 为历史记录数组；失败：400/401；响应带 X-Trace-ID。
    """
    try:
        user, role_code = require_request_user(request)
        detail = get_report_detail(user=user, role_code=role_code, report_id=int(report_id))
        return api_success({"items": detail["history"]})
    except Exception as exc:
        return _error(exc)
