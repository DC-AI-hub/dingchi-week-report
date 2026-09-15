export type ReportStatus = "active" | "pending_activation" | "archived" | string

export interface TemplateItem {
  item_type: "task" | "metric" | string
  section_code: string
  section_name: string
  task_code: string
  label: string
  guidance: string
  scope_type: string
  value_type: string
  unit: string
  required: boolean
  validation_rule: string
  sort_order: number
  config: Record<string, unknown>
}

export interface TemplateSection {
  section_code: string
  section_name: string
  tasks: TemplateItem[]
}

export interface ReportTemplateField {
  field_code: string
  label: string
  sort_order: number
  default_visible: boolean
}

export interface ReportTemplate {
  role_code: string
  role_name: string
  template_code: string
  template_version: string
  template_name: string
  description: string
  sections: TemplateSection[]
  tasks: TemplateItem[]
  metrics: TemplateItem[]
  /** 周报任务列表的列定义；顺序由后端字典配置返回。 */
  fields?: ReportTemplateField[]
}

export interface ReportItem {
  id: string
  report_id: string
  created_at?: string
  updated_at?: string
  scope_type: string
  customer_id: string | null
  task_code: string
  section_code: string
  section_name_snapshot?: string
  customer_name_snapshot: string
  task_name_snapshot: string
  guidance_snapshot: string
  work_content: string
  output_description: string
  planned_completion_date: string | null
  progress_text: string
  progress_percent: number | null
  quality_percent: number | null
  completion_rate: number | null
  delay_reason: string
  actual_completion_date: string | null
  next_action: string
  expected_completion_date: string | null
  owner_id: string | null
  owner_name_snapshot: string
  collaborator_names: string
  document_links: string
  item_status: string
  on_time_status: string
  sort_order: number
}

export interface MonthlyPlan {
  id?: string
  role_code?: string
  employee_id?: string
  group_id?: string | null
  month_key: string
  summary: string
}

export interface ReportMetric {
  id: string
  report_id: string
  item_id: string | null
  metric_code: string
  metric_name_snapshot: string
  value_type: string
  target_value_decimal: number | null
  actual_value_decimal: number | null
  value_text: string
  unit: string
  precision: number
  baseline_value_decimal: number | null
  note: string
}

export interface ReportEvidence {
  id: string
  report_id: string
  item_id: string | null
  evidence_type: string
  file_url: string
  file_name: string
  description: string
  created_at?: string
}

/** 周报独立附件；文件上传记录与周报/任务通过逻辑 ID 关联。 */
export interface ReportAttachment {
  id: string
  /** 业务类型，例如 weekly_report；不是文件格式。 */
  attachment_type: string
  /** 业务主记录 ID，例如周报 ID。 */
  relation_id: string
  /** 可选业务子记录 ID，例如周报任务 ID。 */
  relation_sub_id: string | null
  storage_key: string
  file_url: string
  file_name: string
  mime_type: string
  file_size: number
  description: string
  created_at: string
  updated_at: string
}

export interface WeeklyReport {
  id: string
  role_code: string
  role_name: string
  template_code: string
  employee_id: string
  employee_name: string
  group_id: string | null
  group_name: string | null
  period_start: string
  period_end: string
  as_of_date: string
  period_type: string
  month_key: string
  status: ReportStatus
  summary: string
  risk_level: string
  risk_blocked: boolean
  risk_reason: string
  next_action: string
  support_needed: string
  expected_resolve_date: string | null
  created_at: string
  updated_at: string
  completion_rate?: number
  item_count?: number
}

export interface WeeklyReportDetail {
  report: WeeklyReport
  monthly_plan: MonthlyPlan | null
  items: ReportItem[]
  metrics: ReportMetric[]
  evidence: ReportEvidence[]
  attachments?: ReportAttachment[]
}

export interface ReportListResponse {
  items: WeeklyReport[]
  page: number
  page_size: number
  total: number
  total_pages: number
}

export interface ReportListFilters {
  page?: number
  page_size?: number
  period_start?: string
  period_end?: string
  month_key?: string
  group_id?: string
  employee_scope?: "self" | "team"
}

export interface ReportPayload {
  period_start: string
  period_end: string
  as_of_date?: string
  summary: string
  risk_level: string
  risk_blocked: boolean
  risk_reason: string
  next_action: string
  support_needed: string
  expected_resolve_date: string | null
  items: Array<Partial<ReportItem> & { task_code: string }>
  metrics: Array<Partial<ReportMetric> & { metric_code: string }>
  evidence: Array<Partial<ReportEvidence> & { task_code?: string }>
  /** 已上传附件的保留及任务关联信息；新文件通过 multipart 接口上传。 */
  attachments?: Array<{ id: string; task_code?: string }>
}
