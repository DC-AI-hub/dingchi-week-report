import { reportRequest as request } from "@/shared/api/report-context"

import type { MonthlyPlanTask } from "./types"

/**
 * 通过X-Report-Role指定本人填写职位（未分配职位403）；查询该职位指定月份的月度计划明细。
 * GET /v1/monthly-plan-tasks/{monthKey}/；路径 monthKey 为 YYYY-MM；无请求体。
 * 响应 {items: MonthlyPlanTask[]}，按 sort_order 排序，ID 为字符串，scope_name 为客户或维度（最多 255 字符），无记录返回空数组。
 * 认证：Bearer；失败 400 INVALID_REQUEST、401 AUTHENTICATION_FAILED；携带 X-Trace-ID。
 * 幂等读取；明细随周报创建/更新请求的 monthly_plan_tasks 字段保存；旧接口字段保持兼容。
 */
export function getMonthlyPlanTasks(monthKey: string): Promise<{ items: MonthlyPlanTask[] }> {
  return request({ method: "GET", url: `/v1/monthly-plan-tasks/${encodeURIComponent(monthKey)}/` })
}
