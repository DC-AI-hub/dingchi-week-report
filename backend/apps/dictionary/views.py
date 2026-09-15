"""JSON views for static dictionary options."""

from __future__ import annotations

from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET

from apps.accounts.public import require_user
from apps.core.http import api_error, api_success

from .services.items import InvalidDictionaryTypeError, get_active_items


@require_GET
def dictionary_items_view(request: HttpRequest, dict_type: str) -> JsonResponse:
    """查询指定类型的启用字典项，供页面下拉框和配置校验使用。

    方法/路径：GET /api/v1/dictionaries/{dict_type}/；认证：Bearer；幂等：是。
    路径参数：dict_type 为小写 snake_case 类型，如 role_scope、report_template；无请求体。
    成功响应：data.items 为选项数组，每项包含字符串 id、dict_type、dict_code、dict_name、
    dict_value、description、status 和非负 sort_order；未知类型返回空数组。
    失败响应：401 AUTHENTICATION_FAILED；400 INVALID_DICTIONARY_TYPE；响应带 X-Trace-ID。
    兼容性：字典编码稳定，新增选项向后兼容；下游不得依赖数据库表结构。
    """
    try:
        require_user(request)
        return api_success({"items": get_active_items(dict_type=dict_type)})
    except InvalidDictionaryTypeError as exc:
        return api_error(exc.code, str(exc), status=400)
    except Exception as exc:
        if hasattr(exc, "code") and str(exc.code) == "AUTHENTICATION_FAILED":
            return api_error("AUTHENTICATION_FAILED", str(exc), status=401)
        return api_error("INTERNAL_ERROR", "服务暂时不可用。", status=500)
