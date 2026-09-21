export interface DashboardKpis {
  planned_tasks: number
  completion_rate: number
  completed_tasks: number
  risk_items: number
}

export interface DashboardTrendPoint {
  date: string
  label: string
  progress: number
  completion: number
}

export interface DashboardDistribution {
  name: string
  value: number
  color: string
}

export interface DashboardReport {
  id: string
  role_code: string
  employee_id: string
  employee_name: string
  group_name: string | null
  period_start: string
  period_end: string
  status: string
  summary: string
  risk_level: string
  risk_blocked: boolean
  completion_rate?: number
}

export interface DashboardItem {
  id: string
  report_id: string
  customer_name_snapshot: string
  section_code?: string
  task_name_snapshot: string
  work_content?: string
  output_description?: string
  progress_percent: number | null
  quality_percent: number | null
  completion_rate: number | null
  on_time_status: string
  planned_completion_date: string | null
  progress_text: string
  owner_name_snapshot?: string
  collaborator_names?: string
  document_links?: string
}

export interface DashboardTeamTask extends DashboardItem {
  employee_id: string
  employee_name: string
  role_code: string
  group_name: string
  report_status: string
  report_period_start: string | null
  report_period_end: string | null
}

export interface DashboardSummary {
  scope: string
  period: { start: string; end: string }
  kpis: DashboardKpis
  trend: DashboardTrendPoint[]
  status_distribution: DashboardDistribution[]
  my_tasks: DashboardItem[]
  reports: DashboardReport[]
  team_tasks: DashboardTeamTask[]
}
