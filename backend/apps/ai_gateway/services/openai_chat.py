from collections.abc import Sequence
from typing import Any

from django.conf import settings
from openai import AsyncOpenAI, OpenAIError

from ..schemas import ChatMessage, ChatResult, TokenUsage


class AIProviderConfigurationError(RuntimeError):
    pass


class AIProviderError(RuntimeError):
    pass


class OpenAIChatService:
    def __init__(self) -> None:
        if not settings.AI_API_KEY:
            raise AIProviderConfigurationError("尚未配置 AI_API_KEY。")
        if not settings.AI_MODEL or settings.AI_MODEL == "your-model-name":
            raise AIProviderConfigurationError("尚未配置 AI_MODEL。")

        client_options: dict[str, Any] = {
            "api_key": settings.AI_API_KEY,
            "timeout": settings.AI_TIMEOUT_SECONDS,
        }
        if settings.AI_BASE_URL:
            client_options["base_url"] = settings.AI_BASE_URL

        self.model = settings.AI_MODEL
        self.client = AsyncOpenAI(**client_options)

    async def complete(self, messages: Sequence[ChatMessage]) -> ChatResult:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[message.to_provider_dict() for message in messages],
            )
        except OpenAIError as exc:
            raise AIProviderError("大模型服务调用失败，请稍后重试。") from exc

        if not response.choices:
            raise AIProviderError("大模型服务未返回候选结果。")

        content = response.choices[0].message.content or ""
        usage = response.usage
        return ChatResult(
            content=content,
            model=response.model or self.model,
            request_id=response.id,
            usage=TokenUsage(
                input_tokens=getattr(usage, "prompt_tokens", None),
                output_tokens=getattr(usage, "completion_tokens", None),
                total_tokens=getattr(usage, "total_tokens", None),
            ),
        )

    async def close(self) -> None:
        await self.client.close()


_chat_service: OpenAIChatService | None = None


def get_chat_service() -> OpenAIChatService:
    global _chat_service
    if _chat_service is None:
        _chat_service = OpenAIChatService()
    return _chat_service


async def close_chat_service() -> None:
    global _chat_service
    if _chat_service is not None:
        await _chat_service.close()
        _chat_service = None
