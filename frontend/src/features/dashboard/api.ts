import { request } from "@/shared/api/http"

import type { DashboardSummary } from "./types"

/**
 * 获取周报驾驶舱：GET /v1/dashboard/summary/（统一客户端拼接 /api）。
 * 无请求参数，Bearer 认证；服务端按激活角色返回个人/团队/全量维度的 KPI、趋势、分布和任务。
 * 全量维度额外返回 team_tasks，包含当前周期的任务、责任人和分组，供领导版首页分析展示。
 * 错误：AUTHENTICATION_FAILED、INTERNAL_ERROR；http 层保留 X-Trace-ID；响应字段只增不删。
 */
export function getDashboardSummary(): Promise<DashboardSummary> {
  return request<DashboardSummary>({ method: "GET", url: "/v1/dashboard/summary/" })
}
