from dataclasses import asdict, dataclass
from typing import Any, Literal

ChatRole = Literal["system", "user", "assistant"]
ALLOWED_ROLES: set[str] = {"system", "user", "assistant"}
MAX_MESSAGES = 50
MAX_CONTENT_LENGTH = 20_000
MAX_TOTAL_CONTENT_LENGTH = 100_000


class ChatPayloadError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ChatMessage:
    role: ChatRole
    content: str

    def to_provider_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass(frozen=True, slots=True)
class ChatRequest:
    messages: tuple[ChatMessage, ...]

    @classmethod
    def from_payload(cls, payload: Any) -> "ChatRequest":
        if not isinstance(payload, dict):
            raise ChatPayloadError("请求体必须是 JSON 对象。")

        raw_messages = payload.get("messages")
        if not isinstance(raw_messages, list) or not raw_messages:
            raise ChatPayloadError("messages 必须是非空数组。")
        if len(raw_messages) > MAX_MESSAGES:
            raise ChatPayloadError(f"messages 最多包含 {MAX_MESSAGES} 条消息。")

        messages: list[ChatMessage] = []
        total_length = 0
        for index, item in enumerate(raw_messages):
            if not isinstance(item, dict):
                raise ChatPayloadError(f"messages[{index}] 必须是对象。")

            role = item.get("role")
            content = item.get("content")
            if role not in ALLOWED_ROLES:
                raise ChatPayloadError(f"messages[{index}].role 不受支持。")
            if not isinstance(content, str) or not content.strip():
                raise ChatPayloadError(f"messages[{index}].content 不能为空。")

            clean_content = content.strip()
            if len(clean_content) > MAX_CONTENT_LENGTH:
                raise ChatPayloadError(
                    f"messages[{index}].content 不能超过 {MAX_CONTENT_LENGTH} 个字符。"
                )
            total_length += len(clean_content)
            messages.append(ChatMessage(role=role, content=clean_content))

        if total_length > MAX_TOTAL_CONTENT_LENGTH:
            raise ChatPayloadError("消息总长度超出限制。")

        return cls(messages=tuple(messages))


@dataclass(frozen=True, slots=True)
class TokenUsage:
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


@dataclass(frozen=True, slots=True)
class ChatResult:
    content: str
    model: str
    request_id: str | None
    usage: TokenUsage

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
