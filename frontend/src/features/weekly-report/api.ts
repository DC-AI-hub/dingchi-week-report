import { request } from "@/shared/api/http"

import type {
  ReportListFilters,
  ReportListResponse,
  MonthlyPlan,
  ReportPayload,
  ReportTemplate,
  ReportAttachment,
  DailyWorkTask,
  DailyWorkTaskListResponse,
  WeeklyReportDetail,
} from "./types"

/**
 * 获取指定版本周报模板。
 * 方法/路径：GET /v1/weekly-report-templates/{template_code}/；认证：Bearer；幂等：是。
 * 请求参数：路径 template_code，包含版本号的模板编码；响应 data 为模板、任务、指标和按字典配置排序的 fields JSON；
 * 失败：401/400，统一客户端保留 trace_id，页面只展示错误消息。
 */
export function getReportTemplate(templateCode: string): Promise<ReportTemplate> {
  return request<ReportTemplate>({
    method: "GET",
    url: "/v1/weekly-report-templates/" + templateCode + "/",
  })
}

/**
 * 分页查询当前角色可见的周报摘要。
 * 方法/路径：GET /v1/weekly-reports/；认证：Bearer；幂等：是。
 * 请求参数：page/page_size 为正整数（默认 1/10）；period_start、period_end 为
 * YYYY-MM-DD 周期范围上下限，month_key 为 YYYY-MM 所属月度；team 角色可传 employee_scope=self/team；团队和全员角色可传
 * group_id 字符串筛选分组；employee_id 字符串筛选指定人员（服务端仍按当前角色可见范围校验）。响应 data.items 为周报数组，并返回 page、page_size、total、
 * total_pages；ID 为字符串，失败 400/401/403/404，统一客户端携带 trace_id。
 */
export function listReports(filters: ReportListFilters = {}): Promise<ReportListResponse> {
  return request<ReportListResponse>({
    method: "GET",
    url: "/v1/weekly-reports/",
    params: filters,
  })
}

/**
 * 获取当前用户当前角色指定月度的共用计划。
 * 方法/路径：GET /v1/monthly-plans/{month_key}/；认证：Bearer；幂等：是。
 * 路径参数 month_key 为 YYYY-MM；响应 data 为月度计划文本，未填写时为 null；
 * 失败：400/401/403，统一客户端携带 trace_id。
 */
export function getMonthlyPlan(monthKey: string): Promise<MonthlyPlan | null> {
  return request<MonthlyPlan | null>({
    method: "GET",
    url: "/v1/monthly-plans/" + monthKey + "/",
  })
}

/**
 * 保存当前用户当前角色指定月度的计划文本。
 * 方法/路径：PUT /v1/monthly-plans/{month_key}/；认证：Bearer；幂等：是。
 * 请求体：summary 月度计划文本；响应 data 为保存后的月度计划；失败：400/401/403。
 */
export function saveMonthlyPlan(monthKey: string, summary: string): Promise<MonthlyPlan> {
  return request<MonthlyPlan>({
    method: "PUT",
    url: "/v1/monthly-plans/" + monthKey + "/",
    data: { summary },
  })
}

/**
 * 创建当前用户当前角色的周报。
 * 方法/路径：POST /v1/weekly-reports/；认证：Bearer；幂等：否。
 * 请求体：period_start/period_end、动态 items、summary；统计日期由服务端按当前日期处理；
 * 只能创建当前或未来周期，周期不能重复。响应 data 为完整周报详情；失败 400/401/409，
 * 统一客户端携带 trace_id，页面不得依赖后端实现细节。
 */
export function createReport(payload: ReportPayload): Promise<WeeklyReportDetail> {
  return request<WeeklyReportDetail>({ method: "POST", url: "/v1/weekly-reports/", data: payload })
}

/**
 * 更新本人当前周报。
 * 方法/路径：PATCH /v1/weekly-reports/{id}/；认证：Bearer；幂等：否。
 * 请求体字段同创建，周报周期不可修改且仅本人未完成周报可编辑；响应 data 为更新后的详情；
 * 失败 400/401/403/404，统一客户端携带 trace_id。
 */
export function updateReport(reportId: string, payload: ReportPayload): Promise<WeeklyReportDetail> {
  return request<WeeklyReportDetail>({
    method: "PATCH",
    url: "/v1/weekly-reports/" + reportId + "/",
    data: payload,
  })
}

/**
 * 查询周报详情。
 * 方法/路径：GET /v1/weekly-reports/{id}/；认证：Bearer；幂等：是。
 * 当前角色必须对该员工可见；响应 data 返回 report/template/monthly_plan/items/metrics/attachments/daily_tasks；
 * template 按 report.template_code 返回周报创建时绑定的完整版本模板；
 * 失败 401/403/404，ID 和日期字段遵守统一 JSON 契约。
 */
export function getReportDetail(reportId: string): Promise<WeeklyReportDetail> {
  return request<WeeklyReportDetail>({
    method: "GET",
    url: "/v1/weekly-reports/" + reportId + "/",
  })
}

/**
 * 查询指定周报的每日工作任务。
 * 方法/路径：GET /v1/weekly-reports/{id}/daily-tasks/；认证：Bearer；幂等：是。
 * 无分页参数，响应 data.items 按日期升序返回日报；日期为 YYYY-MM-DD，逻辑 ID 为字符串；
 * 当前角色必须对周报可见，失败 401/403/404，统一客户端携带 trace_id。
 */
export function getDailyTasks(reportId: string): Promise<DailyWorkTaskListResponse> {
  return request<DailyWorkTaskListResponse>({
    method: "GET",
    url: "/v1/weekly-reports/" + reportId + "/daily-tasks/",
  })
}

/**
 * 新增周报中的每日工作任务。
 * 方法/路径：POST /v1/weekly-reports/{id}/daily-tasks/；认证：Bearer；幂等：否。
 * 请求体：work_date（YYYY-MM-DD）和 work_content；日期必须在周报周期内且每天只能一条；
 * 仅本人进行中状态周报可新增，成功返回日报记录，失败 400/401/403/404/409。
 */
export function createDailyTask(
  reportId: string,
  payload: Pick<DailyWorkTask, "work_date" | "work_content">,
): Promise<DailyWorkTask> {
  return request<DailyWorkTask>({
    method: "POST",
    url: "/v1/weekly-reports/" + reportId + "/daily-tasks/",
    data: payload,
  })
}

/**
 * 修改周报中的每日工作任务。
 * 方法/路径：PATCH /v1/weekly-reports/{id}/daily-tasks/{daily_task_id}/；认证：Bearer；幂等：否。
 * 请求体字段同新增；仅本人进行中状态周报可修改，成功返回日报记录，失败 400/401/403/404/409。
 */
export function updateDailyTask(
  reportId: string,
  dailyTaskId: string,
  payload: Pick<DailyWorkTask, "work_date" | "work_content">,
): Promise<DailyWorkTask> {
  return request<DailyWorkTask>({
    method: "PATCH",
    url: "/v1/weekly-reports/" + reportId + "/daily-tasks/" + dailyTaskId + "/",
    data: payload,
  })
}

/**
 * 删除周报中的每日工作任务。
 * 方法/路径：DELETE /v1/weekly-reports/{id}/daily-tasks/{daily_task_id}/；认证：Bearer；幂等：否。
 * 无请求体；仅本人进行中状态周报可删除，成功返回 {id, deleted:true}，失败 401/403/404。
 */
export function deleteDailyTask(
  reportId: string,
  dailyTaskId: string,
): Promise<{ id: string; deleted: true }> {
  return request<{ id: string; deleted: true }>({
    method: "DELETE",
    url: "/v1/weekly-reports/" + reportId + "/daily-tasks/" + dailyTaskId + "/",
  })
}

/**
 * 删除本人当前周报。
 * 方法/路径：DELETE /v1/weekly-reports/{id}/；认证：Bearer；幂等：否。
 * 无请求体；仅本人且未完成的周报可删除，响应 data 为 { id: string, deleted: true }；
 * 失败 400/401/403/404，统一客户端携带 trace_id。
 */
export function deleteReport(reportId: string): Promise<{ id: string; deleted: true }> {
  return request<{ id: string; deleted: true }>({
    method: "DELETE",
    url: "/v1/weekly-reports/" + reportId + "/",
  })
}

/**
 * 手动提交本人当前角色的周报。
 * 方法/路径：POST /v1/weekly-reports/{id}/submit/；认证：Bearer；幂等：否。
 * 仅进行中状态的本人周报可以提交，提交后周报及其任务、日报、附件只读。
 */
export function submitReport(
  reportId: string,
): Promise<{ id: string; status: "completed"; submitted: true }> {
  return request<{ id: string; status: "completed"; submitted: true }>({
    method: "POST",
    url: "/v1/weekly-reports/" + reportId + "/submit/",
  })
}

/**
 * 上传周报任务附件。
 * 方法/路径：POST /v1/weekly-reports/{id}/attachments/；认证：Bearer；幂等：否�?
 * 请求体：multipart/form-data，file 必填，item_id 和 description 可选；attachment_type 固定为 weekly_report。
 * 成功响应为系统通用附件信息。
 * 仅允许本人当前或未来周期周报；失败 400/401/403/404，统一客户端携带 trace_id�?
 */
export function uploadReportAttachment(
  reportId: string,
  file: File,
  itemId?: string | null,
  description = "",
  attachmentType = "weekly_report",
): Promise<ReportAttachment> {
  const data = new FormData()
  data.append("file", file)
  if (itemId) data.append("item_id", itemId)
  if (description) data.append("description", description)
  data.append("attachment_type", attachmentType)
  return request<ReportAttachment>({
    method: "POST",
    url: "/v1/weekly-reports/" + reportId + "/attachments/",
    data,
  })
}
