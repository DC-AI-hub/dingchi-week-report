import { request } from "@/shared/api/http"

import type { DashboardSummary } from "./types"

/**
 * 获取周报驾驶舱：GET /v1/dashboard/summary/（统一客户端拼接 /api）。
 * 无请求参数，Bearer 认证；服务端按激活角色返回个人/团队/全量维度的 KPI、趋势、分布和任务。
 * 错误：AUTHENTICATION_FAILED、INTERNAL_ERROR；http 层保留 X-Trace-ID；响应字段只增不删。
 */
export function getDashboardSummary(): Promise<DashboardSummary> {
  return request<DashboardSummary>({ method: "GET", url: "/v1/dashboard/summary/" })
}
