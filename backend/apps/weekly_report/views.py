"""HTTP controllers for role-based weekly reports."""

from __future__ import annotations

import json
from typing import Any

from django.core.files.storage import default_storage
from django.http import FileResponse, HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from apps.accounts.services.auth import AuthenticationError, require_request_user
from apps.core.http import api_error, api_success, log_unhandled_exception

from .services.daily_tasks import (
    create_daily_task,
    delete_daily_task,
    list_daily_tasks,
    update_daily_task,
)
from .services.reports import (
    ReportConflictError,
    ReportError,
    ReportNotFoundError,
    ReportPermissionError,
    create_or_update_report,
    dashboard_next_week,
    dashboard_summary,
    delete_report,
    delete_report_attachment,
    get_monthly_plan,
    get_report_attachment_for_download,
    get_report_detail,
    get_template_by_code,
    list_visible_reports,
    save_monthly_plan,
    submit_report,
    upload_pending_report_attachment,
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
    if isinstance(exc, ReportNotFoundError):
        return api_error(exc.code, str(exc), status=404)
    if isinstance(exc, ReportPermissionError):
        return api_error(exc.code, str(exc), status=403)
    if isinstance(exc, ReportConflictError):
        return api_error(exc.code, str(exc), status=409)
    if isinstance(exc, ReportError):
        return api_error(exc.code, str(exc), status=400)
    if isinstance(exc, json.JSONDecodeError):
        return api_error("INVALID_JSON", "请求体不是有效的 JSON。", status=400)
    if isinstance(exc, ValueError):
        return api_error("INVALID_REQUEST", str(exc), status=400)
    log_unhandled_exception(exc, context="weekly_report")
    return api_error("INTERNAL_ERROR", "服务暂时不可用。", status=500)


@require_GET
def dashboard_view(request: HttpRequest) -> JsonResponse:
    """按当前激活角色返回驾驶舱 KPI、趋势、状态分布和可见周报。

    方法/路径：GET /api/v1/dashboard/summary/；认证：Bearer；幂等：是。
    参数：period_start（可选，YYYY-MM-DD，必须为周一）。
    权限：个人仅自己，经理含下属，总裁/系统管理员含全部；成功响应为 dashboard JSON。
    失败：401 AUTHENTICATION_FAILED；追踪：响应带 X-Trace-ID；字段只增不改。
    """
    try:
        user, role_code = require_request_user(request)
        return api_success(
            dashboard_summary(
                user=user,
                role_code=role_code,
                period_start=request.GET.get("period_start"),
            )
        )
    except Exception as exc:
        return _error(exc)


@require_GET
def dashboard_next_week_view(request: HttpRequest) -> JsonResponse:
    """获取所选周期紧邻下一周的计划数据。

    方法/路径：GET /api/v1/dashboard/next-week/；认证：Bearer；参数：period_start
    （可选，YYYY-MM-DD，必须为周一）。接口只查询 period_start 后第 7 天开始的周期；
    该周期没有周报时返回空数组，不会读取更远周期的数据。
    """
    try:
        user, role_code = require_request_user(request)
        return api_success(
            dashboard_next_week(
                user=user,
                role_code=role_code,
                period_start=request.GET.get("period_start"),
            )
        )
    except Exception as exc:
        return _error(exc)


@require_GET
def template_view(request: HttpRequest, template_code: str) -> JsonResponse:
    """获取指定模板编码的可配置周报任务、指标、字段顺序和校验规则。

    方法/路径：GET /api/v1/weekly-report-templates/{template_code}/；认证：Bearer；
    参数：路径模板编码（编码已包含版本号）。成功响应：模板信息、模块、fields、tasks、metrics；
    fields 按周报列表展示顺序返回；
    失败：401；响应带 X-Trace-ID，模板新增字段向后兼容。
    """
    try:
        require_request_user(request)
        return api_success(get_template_by_code(template_code))
    except Exception as exc:
        return _error(exc)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def report_list_view(request: HttpRequest) -> JsonResponse:
    """查询当前角色可见的周报列表或创建当前角色的一份周报。

    方法/路径：GET/POST /api/v1/weekly-reports/；认证：Bearer；
    GET 参数：page、page_size、month_key（YYYY-MM）、period_start、period_end
    （周期范围上下限）、group_id；
    team 角色额外支持 employee_scope=self/team。POST 参数为周报 JSON。
    可选 monthly_plan_tasks 随周报保存当月共用工作任务；详见 docs/monthly-plan-tasks-api.md。
    交付专员和招聘模板允许草稿 items 的 output_description 为空、planned_completion_date 为 null；
    正式提交前必须补齐；其他模板保留原必填规则。
    GET 成功响应：data.items、page、page_size、total、total_pages；
    POST 成功响应：201 周报详情；权限按角色作用域过滤。
    失败：400/401/403/404/409；响应带 X-Trace-ID。
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
        try:
            page = int(request.GET.get("page") or "1")
            page_size = int(request.GET.get("page_size") or "10")
        except ValueError as exc:
            raise ReportError("分页参数必须是整数。") from exc
        return api_success(
            list_visible_reports(
                user=user,
                role_code=role_code,
                page=page,
                page_size=page_size,
                period_start=request.GET.get("period_start"),
                period_end=request.GET.get("period_end"),
                month_key=request.GET.get("month_key"),
                group_id=request.GET.get("group_id"),
                employee_id=request.GET.get("employee_id"),
                employee_scope=request.GET.get("employee_scope"),
            )
        )
    except Exception as exc:
        return _error(exc)


@csrf_exempt
@require_http_methods(["GET", "PUT"])
def monthly_plan_view(request: HttpRequest, month_key: str) -> JsonResponse:
    """查询或保存当前用户当前角色指定月度的单一月度计划。

    方法/路径：GET/PUT /api/v1/monthly-plans/{month_key}/；认证：Bearer。
    GET 路径参数 month_key 使用 YYYY-MM，未填写时 data=null；PUT 请求体为 {summary}。
    成功响应为月度计划；失败：400/401/403；响应带 X-Trace-ID，逻辑 ID 均序列化为字符串。
    """
    try:
        user, role_code = require_request_user(request)
        if request.method == "PUT":
            payload = _json_payload(request)
            return api_success(
                save_monthly_plan(
                    user=user,
                    role_code=role_code,
                    month_key=month_key,
                    summary=payload.get("summary"),
                )
            )
        return api_success(
            get_monthly_plan(
                user=user,
                access_role_code=role_code,
                month_key=month_key,
            )
        )
    except Exception as exc:
        return _error(exc)


@csrf_exempt
@require_http_methods(["GET", "PATCH", "DELETE"])
def report_detail_view(request: HttpRequest, report_id: str) -> JsonResponse:
    """获取、修改或删除周报。

    方法/路径：GET/PATCH/DELETE /api/v1/weekly-reports/{id}/；认证：Bearer；参数：路径 report_id。
    PATCH/DELETE 仅允许操作本人且未完成的周报；提交请调用独立的 submit 接口。
    成功响应：report/template/monthly_plan/monthly_plan_tasks/items/metrics/attachments/daily_tasks，
    monthly_plan_tasks 随周报保存本人当前角色当月计划；详见 docs/monthly-plan-tasks-api.md，
    或 id/deleted=true；
    失败：400/401/403/404/409；响应带 X-Trace-ID。
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
        if request.method == "DELETE":
            return api_success(
                delete_report(user=user, role_code=role_code, report_id=int(report_id))
            )
        return api_success(
            get_report_detail(user=user, role_code=role_code, report_id=int(report_id))
        )
    except Exception as exc:
        return _error(exc)


@csrf_exempt
@require_POST
def report_submit_view(request: HttpRequest, report_id: str) -> JsonResponse:
    """提交本人当前角色的周报。

    方法/路径：POST /api/v1/weekly-reports/{id}/submit/；认证：Bearer；参数：路径 report_id。
    只有周报本人可以提交处于进行中状态的周报；提交后周报、任务、日报和附件均只读，
    不会再因周期结束自动变更状态。成功响应为 {id, status, submitted}。
    交付专员和招聘模板提交前校验输出成果和计划完成日期，缺失返回 400 INVALID_REQUEST。
    """
    try:
        user, role_code = require_request_user(request)
        return api_success(
            submit_report(user=user, role_code=role_code, report_id=int(report_id))
        )
    except Exception as exc:
        return _error(exc)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def daily_task_list_view(request: HttpRequest, report_id: str) -> JsonResponse:
    """查询或新增指定周报的每日工作任务。

    方法/路径：GET/POST /api/v1/weekly-reports/{report_id}/daily-tasks/；认证：Bearer。
    GET 无分页参数，成功响应 data.items 为按日期升序排列的日报数组；字段为 id、report_id、
    work_date（YYYY-MM-DD）、work_content、created_at、updated_at，逻辑 ID 序列化为字符串。
    POST 请求体为 {work_date: YYYY-MM-DD, work_content: string}，日期必须位于周报周期内，
    且一个周报日期只能保存一条；仅进行中状态周报本人可新增。失败：400/401/403/404/409；
    响应带 X-Trace-ID，页面不依赖数据库实现细节。
    """
    try:
        user, role_code = require_request_user(request)
        parsed_report_id = int(report_id)
        if request.method == "POST":
            return api_success(
                create_daily_task(
                    user=user,
                    role_code=role_code,
                    report_id=parsed_report_id,
                    payload=_json_payload(request),
                ),
                status=201,
            )
        return api_success(
            list_daily_tasks(user=user, role_code=role_code, report_id=parsed_report_id)
        )
    except Exception as exc:
        return _error(exc)


@csrf_exempt
@require_http_methods(["PATCH", "DELETE"])
def daily_task_detail_view(
    request: HttpRequest, report_id: str, daily_task_id: str
) -> JsonResponse:
    """修改或删除指定周报的一条日报。

    方法/路径：PATCH/DELETE /api/v1/weekly-reports/{report_id}/daily-tasks/{daily_task_id}/；
    认证：Bearer。PATCH 请求体为 {work_date: YYYY-MM-DD, work_content: string}，日期必须在周报
    范围且不能与同周报已有日期重复；DELETE 无请求体。仅进行中状态周报本人可操作；成功响应为
    日报记录或 {id, deleted: true}。失败：400/401/403/404/409；响应带 X-Trace-ID。
    """
    try:
        user, role_code = require_request_user(request)
        parsed_report_id = int(report_id)
        parsed_task_id = int(daily_task_id)
        if request.method == "PATCH":
            return api_success(
                update_daily_task(
                    user=user,
                    role_code=role_code,
                    report_id=parsed_report_id,
                    daily_task_id=parsed_task_id,
                    payload=_json_payload(request),
                )
            )
        return api_success(
            delete_daily_task(
                user=user,
                role_code=role_code,
                report_id=parsed_report_id,
                daily_task_id=parsed_task_id,
            )
        )
    except Exception as exc:
        return _error(exc)


@csrf_exempt
@require_POST
def pending_attachment_upload_view(request: HttpRequest) -> JsonResponse:
    """上传尚未绑定工作任务的周报附件。

    方法/路径：POST /api/v1/attachments/；认证：Bearer；幂等：否。
    请求体：multipart/form-data，file 必填，description 可选。附件先绑定当前上传人，
    成功响应：201，data 返回附件 ID；保存周报工作任务时通过附件 ID 完成业务绑定。
    失败：400/401；响应带 X-Trace-ID，不要求周报或工作任务预先存在。
    """
    try:
        user, _role_code = require_request_user(request)
        return api_success(
            upload_pending_report_attachment(
                user=user,
                uploaded_file=request.FILES.get("file"),
                description=request.POST.get("description") or "",
            ),
            status=201,
        )
    except Exception as exc:
        return _error(exc)


@require_GET
def attachment_download_view(
    request: HttpRequest, attachment_id: str
) -> FileResponse | JsonResponse:
    """鉴权下载系统附件。

    方法/路径：GET /api/v1/attachments/{attachment_id}/download/；认证：Bearer；
    参数：路径 attachment_id 为附件逻辑 ID。当前支持周报附件，登录用户当前角色必须
    对附件所属周报具有查看权限。成功响应为二进制文件流并保留原始文件名；
    失败：401/403/404；响应带 X-Trace-ID，不暴露宿主机存储路径。
    """
    try:
        user, role_code = require_request_user(request)
        attachment = get_report_attachment_for_download(
            user=user,
            role_code=role_code,
            attachment_id=int(attachment_id),
        )
        response = FileResponse(
            default_storage.open(attachment.storage_key, "rb"),
            as_attachment=True,
            filename=attachment.file_name,
            content_type=attachment.mime_type or "application/octet-stream",
        )
        response["Cache-Control"] = "private, no-store"
        response["X-Content-Type-Options"] = "nosniff"
        if attachment.file_size:
            response["Content-Length"] = str(attachment.file_size)
        return response
    except Exception as exc:
        return _error(exc)


@csrf_exempt
@require_http_methods(["DELETE"])
def attachment_delete_view(request: HttpRequest, attachment_id: str) -> JsonResponse:
    """删除本人未提交周报的附件。

    方法/路径：DELETE /api/v1/attachments/{attachment_id}/；认证：Bearer；幂等：否。
    无请求体；成功后物理删除附件表记录与宿主机磁盘文件，返回
    {id, deleted:true}；仅周报本人且周报未提交时允许操作。
    """
    try:
        user, role_code = require_request_user(request)
        return api_success(
            delete_report_attachment(
                user=user,
                role_code=role_code,
                attachment_id=int(attachment_id),
            )
        )
    except Exception as exc:
        return _error(exc)
