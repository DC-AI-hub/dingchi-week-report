import { request } from "@/shared/api/http"

export interface Liveness {
  status: "ok"
  service: string
  environment: string
  timestamp: string
}

export interface Readiness {
  status: "ok" | "degraded"
  checks: {
    database: "ok" | "unavailable"
    redis: "ok" | "unavailable"
  }
}

/**
 * 检查后端进程是否存活。
 * 请求：GET /v1/health/live/（统一客户端拼接 /api）；无参数、公开、幂等。
 * 响应：返回 Liveness，timestamp 为带时区 ISO 8601 字符串；失败由统一错误层处理并保留 trace_id。
 * 兼容性：既有字段语义保持不变，新增字段向后兼容。
 */
export function getLiveness(): Promise<Liveness> {
  return request<Liveness>({ method: "GET", url: "/v1/health/live/" })
}

/**
 * 检查数据库、Redis 等后端依赖是否就绪。
 * 请求：GET /v1/health/ready/（统一客户端拼接 /api）；无参数、公开、幂等。
 * 响应：返回 Readiness；status 为 ok/degraded，checks 只包含脱敏后的依赖状态。
 * 错误：HTTP 503 表示未就绪，统一错误层保留 trace_id；页面不读取后端连接信息或异常堆栈。
 * 兼容性：checks 可新增依赖键，既有状态值和字段语义不可静默修改。
 */
export function getReadiness(): Promise<Readiness> {
  return request<Readiness>({ method: "GET", url: "/v1/health/ready/" })
}
