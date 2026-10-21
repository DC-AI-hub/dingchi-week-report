import json

from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from apps.accounts.services.auth import AuthenticationError, require_request_user
from apps.core.http import api_error, api_success, log_unhandled_exception

from .services.monthly_plans import approval_read, change_read, change_write, copy, read, write
from .services.monthly_plans.policy import PlanNotFound


def invoke(request, callback):
    try:
        user, role_code = require_request_user(request)
        return api_success(callback(user, role_code))
    except AuthenticationError as exc:
        return api_error(exc.code, str(exc), status=401)
    except PermissionError as exc:
        return api_error("FORBIDDEN", str(exc), status=403)
    except PlanNotFound as exc:
        return api_error("MONTHLY_PLAN_NOT_FOUND", str(exc), status=404)
    except IntegrityError:
        return api_error("MONTHLY_PLAN_CONFLICT", "计划已被更新，请重新加载后再操作。", status=409)
    except (ValueError, TypeError) as exc:
        return api_error("INVALID_REQUEST", str(exc), status=400)
    except Exception as exc:
        log_unhandled_exception(exc, context="monthly_plan_management")
        return api_error("INTERNAL_ERROR", "月度计划服务暂不可用。", status=500)


def payload(request):
    value = json.loads(request.body or b"{}")
    if not isinstance(value, dict):
        raise ValueError("请求体必须是 JSON 对象。")
    return value


@require_GET
def context_view(request):
    """GET /monthly-plan-management/context/：当前角色模板及有序审批人，未配置上级返回告警。"""
    return invoke(request, read.context)


@require_GET
def gate_view(request, month_key):
    """GET /monthly-plan-management/gate/{YYYY-MM}/：本人当前角色的审批状态及只读内容。"""
    return invoke(request, lambda user, role: read.gate(user, role, month_key))


@csrf_exempt
@require_http_methods(["GET", "POST"])
def list_view(request):
    """月度计划筛选分页和新增，完整参数及权限契约见 docs/monthly-plan-management-api.md。"""
    if request.method == "GET":
        return invoke(request, lambda user, role: read.list_plans(user, role, request.GET))
    return invoke(request, lambda user, role: write.save(user, role, payload(request)))


@csrf_exempt
@require_http_methods(["GET", "PATCH", "DELETE"])
def detail_view(request, plan_id):
    """月度计划查看、修改和软删除；历史与审批记录保留，审批期间锁定。"""
    callbacks = {
        "GET": lambda user, role: read.detail(user, role, int(plan_id)),
        "PATCH": lambda user, role: write.save(user, role, payload(request), int(plan_id)),
        "DELETE": lambda user, role: write.delete(user, role, int(plan_id)),
    }
    return invoke(request, callbacks[request.method])


@csrf_exempt
@require_POST
def submit_view(request, plan_id):
    """POST {id}/submit/：按独立月报审批人顺序创建审批单及不可变快照，空配置自动通过。"""
    return invoke(request, lambda user, role: write.submit(user, role, int(plan_id)))


@csrf_exempt
@require_POST
def decide_view(request, plan_id):
    """POST /monthly-plan-management/{id}/decide/：仅当前审批人可操作，驳回原因必填。"""
    return invoke(
        request, lambda user, role: write.decide(user, role, int(plan_id), payload(request))
    )


@csrf_exempt
@require_POST
def create_change_view(request, plan_id):
    """创建已生效计划的变更子流程；POST {id}/changes/，无请求体，400/403/404，统一认证及trace。"""
    return invoke(request, lambda user, role: change_write.create(user, role, int(plan_id)))


@csrf_exempt
@require_http_methods(["GET", "PATCH", "DELETE"])
def change_detail_view(request, change_id):
    """查看/编辑/删除变更草稿；原始快照不可修改，权限与月度计划一致，契约见文档。"""
    callbacks = {
        "GET": lambda user, role: change_read.detail(user, role, int(change_id)),
        "PATCH": lambda user, role: change_write.save(user, role, int(change_id), payload(request)),
        "DELETE": lambda user, role: change_write.delete(user, role, int(change_id)),
    }
    return invoke(request, callbacks[request.method])


@csrf_exempt
@require_POST
def change_submit_view(request, change_id):
    """POST changes/{id}/submit/，按独立月报审批人顺序提交变更，未改变或旧版本返回400。"""
    return invoke(request, lambda user, role: change_write.submit(user, role, int(change_id)))


@csrf_exempt
@require_POST
def change_decide_view(request, change_id):
    """POST changes/{id}/decide/；最终通过原子发布，驳回保留主流程数据，400/403，统一trace。"""
    return invoke(
        request,
        lambda user, role: change_write.decide(user, role, int(change_id), payload(request)),
    )


@require_GET
def approval_detail_view(request, approval_id):
    """GET approvals/{id}/，本人审批快照、基线及can_approve。

    字符串ID，Bearer/trace，400/401/403，完整契约见月度计划API。
    """
    return invoke(
        request, lambda user, role: approval_read.detail_assigned(user, role, int(approval_id))
    )


@csrf_exempt
@require_POST
def copy_view(request, plan_id):
    """POST {id}/copy/：无请求体，仅本人当前职位已通过主计划可复制。

    返回下月草稿完整详情（字符串ID）；复制最新生效内容及模板元数据，不包含未通过变更。
    目标月份已存在返回400；401未认证、403无权、404不存在、409并发冲突；统一包络及trace。
    """
    return invoke(request, lambda user, role: copy.copy_next_month(user, role, int(plan_id)))
