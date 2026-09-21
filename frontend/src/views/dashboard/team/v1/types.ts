export interface TeamMemberSummary {
  employeeId: string
  employeeName: string
  roleName: string
  groupName: string
  completionRate: number
  taskCount: number
  riskCount: number
}

export interface TeamReportEntry {
  id: string
  employeeId: string
  employeeName: string
  roleName: string
  groupName: string
  summary: string
  completionRate: number
  status: string
  riskLevel: string
  periodStart: string
  periodEnd: string
}

export interface TeamPlanEntry {
  id: string
  title: string
  owner: string
  detail: string
  status: string
  start: string
  end: string
}
