"""月度计划任务只读查询接口；写入在月度计划管理中完成。"""

from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET

from apps.accounts.services.auth import AuthenticationError, require_request_user
from apps.core.http import api_error, api_success, log_unhandled_exception

from .services.monthly_plan_tasks import list_monthly_plan_tasks


@require_GET
def monthly_plan_task_list_view(request: HttpRequest, month_key: str) -> JsonResponse:
    """查询本人当前角色指定月份的月度计划任务。

    GET /api/v1/monthly-plan-tasks/{month_key}/；Bearer 认证；幂等：是。
    month_key 为 YYYY-MM，有效年份 0001–9999；无请求体，不接受其他员工或角色参数。
    响应 data.items 按 sort_order 升序，字段 id（字符串）、scope_name（客户/维度）、
    work_task（长文本）、
    task_source/task_template/task_values（可选模板来源及占位值，旧数据默认自定义）、
    sort_order、updated_at。
    无记录返回空数组；失败 400 INVALID_REQUEST、401 AUTHENTICATION_FAILED；统一 X-Trace-ID。
    保留独立只读接口；写入改用 monthly-plan-management，不允许周报修改审批内容。
    """
    try:
        user, role_code = require_request_user(request)
        return api_success({"items": list_monthly_plan_tasks(
            employee_id=int(user.id), role_code=role_code, month_key=month_key
        )})
    except AuthenticationError as exc:
        return api_error("AUTHENTICATION_FAILED", str(exc), status=401)
    except ValueError as exc:
        return api_error("INVALID_REQUEST", str(exc), status=400)
    except Exception as exc:
        log_unhandled_exception(exc, context="monthly_plan_tasks")
        return api_error("INTERNAL_ERROR", "月度计划暂时无法加载，请稍后重试。", status=500)
