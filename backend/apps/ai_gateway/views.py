import json
import logging

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.core.http import api_error, api_success

from .schemas import ChatPayloadError, ChatRequest
from .services.openai_chat import (
    AIProviderConfigurationError,
    AIProviderError,
    get_chat_service,
)

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
async def chat_completion(request: HttpRequest) -> JsonResponse:
    """调用已配置的大模型，根据消息列表生成文本。

    方法/路径：POST /api/v1/ai/chat/
    认证/权限：当前示例入口未绑定具体业务用户，生产接入必须由统一认证/权限中间件保护；幂等：否，禁止无幂等键自动重试。
    请求参数：JSON Body 的 messages 必须是非空数组，最多 50 条；每项 role 为 system/user/assistant，
      content 为非空字符串，单条最多 20,000 字符，总计最多 100,000 字符。
    成功响应：200，统一 JSON 包络；data.content、data.model、data.request_id 为字符串或可空值，
      data.usage 为输入/输出/总 token 数对象。
    失败响应：400 INVALID_JSON/INVALID_REQUEST；503 AI_NOT_CONFIGURED；
      502 AI_PROVIDER_ERROR；500 INTERNAL_ERROR。
      客户端只展示安全提示并保留 trace_id，不解析上游原始异常。
    追踪/兼容：请求可带 X-Trace-ID，响应带同值；新增响应字段向后兼容，
      改变消息语义需升级 API 主版本。
    """
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return api_error("INVALID_JSON", "请求体不是有效的 JSON。", status=400)

    try:
        chat_request = ChatRequest.from_payload(payload)
        result = await get_chat_service().complete(chat_request.messages)
    except ChatPayloadError as exc:
        return api_error("INVALID_REQUEST", str(exc), status=400)
    except AIProviderConfigurationError as exc:
        return api_error("AI_NOT_CONFIGURED", str(exc), status=503)
    except AIProviderError as exc:
        logger.warning("AI provider request failed: %s", exc)
        return api_error("AI_PROVIDER_ERROR", str(exc), status=502)
    except Exception:
        logger.exception("Unexpected AI gateway error")
        return api_error("INTERNAL_ERROR", "服务暂时不可用。", status=500)

    return api_success(result.to_dict())
