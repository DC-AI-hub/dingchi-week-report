import { request } from "@/shared/api/http"

import type { DashboardNextWeek, DashboardSummary } from "./types"

/**
 * 获取周报驾驶舱：GET /v1/dashboard/summary/（统一客户端拼接 /api）。
 * periodStart 可选且必须是周一；服务端按激活角色和指定周期返回个人/团队/全量维度的 KPI、趋势、分布和任务。
 * member_reports 为当前周期按成员去重、更新时间降序的摘要，数量不超过可见成员数；status=completed 才算已提交。
 * 全量维度额外返回 team_tasks，包含当前周期的任务、责任人和分组，供领导版首页分析展示。
 * 错误：AUTHENTICATION_FAILED、INTERNAL_ERROR；http 层保留 X-Trace-ID；响应字段只增不删。
 */
export function getDashboardSummary(periodStart?: string): Promise<DashboardSummary> {
  return request<DashboardSummary>({
    method: "GET",
    url: "/v1/dashboard/summary/",
    params: periodStart ? { period_start: periodStart } : undefined,
  })
}

/**
 * 获取所选周期紧邻下一周的数据：GET /v1/dashboard/next-week/。
 * 服务端严格查询 periodStart + 7 天所在周期；空周返回空数组，不会跳到更远的有数据周期。
 */
export function getDashboardNextWeek(periodStart?: string): Promise<DashboardNextWeek> {
  return request<DashboardNextWeek>({
    method: "GET",
    url: "/v1/dashboard/next-week/",
    params: periodStart ? { period_start: periodStart } : undefined,
  })
}
