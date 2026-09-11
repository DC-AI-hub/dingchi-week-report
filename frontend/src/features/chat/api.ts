import { request } from "@/shared/api/http"

import type { ChatMessage, ChatResult } from "./types"

/**
 * 调用后端大模型生成聊天回复。
 * 用途：根据按顺序提供的 system/user/assistant 消息生成一条文本结果。
 * 请求：POST /v1/ai/chat/（统一客户端拼接 /api）；Body 为 messages 非空数组，最多 50 条，
 *   每条 content 非空且不超过 20,000 字符，总长度不超过 100,000；当前接口非幂等，禁止无幂等键自动重试。
 * 认证/权限：由后端统一认证和权限中间件处理；调用方不得根据页面权限自行猜测。
 * 响应：返回 ChatResult；content/model 为字符串，request_id 和 usage 字段可空，ID 按 string 处理。
 * 错误：INVALID_JSON、INVALID_REQUEST、AI_NOT_CONFIGURED、AI_PROVIDER_ERROR、INTERNAL_ERROR；
 *   统一错误层保留 trace_id，页面只展示安全提示。
 * 兼容性：新增响应字段向后兼容，字段改名/改类型或消息语义变化需升级 API 主版本。
 */
export function createChatCompletion(messages: ChatMessage[]): Promise<ChatResult> {
  return request<ChatResult>({
    method: "POST",
    url: "/v1/ai/chat/",
    data: { messages },
  })
}
