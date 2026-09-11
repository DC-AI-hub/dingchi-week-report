import { request } from "@/shared/api/http"

import type {
  ReportListResponse,
  ReportPayload,
  ReportTemplate,
  WeeklyReportDetail,
} from "./types"

/**
 * 获取当前激活角色的周报模板：GET /v1/weekly-report-templates/{role_code}/。
 * 请求：路径 role_code；认证：Bearer；响应：tasks、metrics、sections 及校验规则；失败：401/400。
 */
export function getReportTemplate(roleCode: string): Promise<ReportTemplate> {
  return request<ReportTemplate>({ method: "GET", url: `/v1/weekly-report-templates/${roleCode}/` })
}

/**
 * 查询当前角色可见的周报摘要：GET /v1/weekly-reports/，可选 status 筛选。
 * 后端按 self/team/all 作用域返回 JSON；响应带 trace_id；失败：401/400。
 */
export function listReports(status?: string): Promise<ReportListResponse> {
  return request<ReportListResponse>({
    method: "GET",
    url: "/v1/weekly-reports/",
    params: status ? { status } : undefined,
  })
}

/**
 * 创建当前用户当前角色的周报草稿：POST /v1/weekly-reports/。
 * 请求：周期、摘要、风险、items、metrics、evidence；响应：完整周报详情；失败：400/401。
 */
export function createReport(payload: ReportPayload): Promise<WeeklyReportDetail> {
  return request<WeeklyReportDetail>({ method: "POST", url: "/v1/weekly-reports/", data: payload })
}

/**
 * 更新自己的草稿或退回周报：PATCH /v1/weekly-reports/{id}/。
 * 请求：完整或部分 ReportPayload；已提交/已审核不可编辑；响应：更新后详情；失败：400/401。
 */
export function updateReport(reportId: string, payload: ReportPayload): Promise<WeeklyReportDetail> {
  return request<WeeklyReportDetail>({ method: "PATCH", url: `/v1/weekly-reports/${reportId}/`, data: payload })
}

/**
 * 查询周报详情：GET /v1/weekly-reports/{id}/，返回 report/items/metrics/evidence/history。
 * 当前角色必须对该员工可见；失败：400/401；字段采用统一 JSON 契约。
 */
export function getReportDetail(reportId: string): Promise<WeeklyReportDetail> {
  return request<WeeklyReportDetail>({ method: "GET", url: `/v1/weekly-reports/${reportId}/` })
}

/**
 * 提交自己的周报：POST /v1/weekly-reports/{id}/submit/，无请求体。
 * 状态必须为 draft/returned；成功返回提交后的详情并记录历史；失败：400/401。
 */
export function submitReport(reportId: string): Promise<WeeklyReportDetail> {
  return request<WeeklyReportDetail>({ method: "POST", url: `/v1/weekly-reports/${reportId}/submit/` })
}

/**
 * 审核周报：POST /v1/weekly-reports/{id}/review/。
 * 请求：action=approve/return、comment；经理/总裁/系统管理员按可见范围操作；响应：审核后详情。
 */
export function reviewReport(reportId: string, action: "approve" | "return", comment: string): Promise<WeeklyReportDetail> {
  return request<WeeklyReportDetail>({
    method: "POST",
    url: `/v1/weekly-reports/${reportId}/review/`,
    data: { action, comment },
  })
}

/**
 * 查询审核历史：GET /v1/weekly-reports/{id}/history/；认证：Bearer；响应 data.items。
 */
export function getReportHistory(reportId: string): Promise<{ items: WeeklyReportDetail["history"] }> {
  return request<{ items: WeeklyReportDetail["history"] }>({ method: "GET", url: `/v1/weekly-reports/${reportId}/history/` })
}
