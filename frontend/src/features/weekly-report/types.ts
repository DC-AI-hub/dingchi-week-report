export type ReportStatus = "draft" | "submitted" | "approved" | "returned" | string

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

export interface ReportTemplate {
  role_code: string
  role_name: string
  template_code: string
  template_version: string
  template_name: string
  description: string
  submit_deadline_rule: string
  review_deadline_rule: string
  sections: TemplateSection[]
  tasks: TemplateItem[]
  metrics: TemplateItem[]
}

export interface ReportItem {
  id: string
  report_id: string
  scope_type: string
  customer_id: string | null
  task_code: string
  section_code: string
  section_name_snapshot?: string
  customer_name_snapshot: string
  task_name_snapshot: string
  guidance_snapshot: string
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
  item_status: string
  on_time_status: string
  sort_order: number
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
}

export interface ReportReview {
  id: string
  report_id: string
  reviewer_id: string
  reviewer_name: string
  action: string
  comment: string
  created_at: string
}

export interface WeeklyReport {
  id: string
  role_code: string
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
  submitted_at: string | null
  reviewed_at: string | null
  reviewer_id: string | null
  review_comment: string
  completion_rate?: number
  item_count?: number
}

export interface WeeklyReportDetail {
  report: WeeklyReport
  items: ReportItem[]
  metrics: ReportMetric[]
  evidence: ReportEvidence[]
  history: ReportReview[]
}

export interface ReportListResponse {
  items: WeeklyReport[]
}

export interface ReportPayload {
  period_start: string
  period_end: string
  as_of_date: string
  summary: string
  risk_level: string
  risk_blocked: boolean
  risk_reason: string
  next_action: string
  support_needed: string
  expected_resolve_date: string | null
  items: Array<Partial<ReportItem> & { task_code: string }>
  metrics: Array<Partial<ReportMetric> & { metric_code: string }>
  evidence: Array<Partial<ReportEvidence>>
}
