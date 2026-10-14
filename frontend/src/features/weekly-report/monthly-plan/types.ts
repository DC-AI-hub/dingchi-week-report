/** 按员工、角色、月份共用的月度计划明细。ID 为字符串，排序按数组顺序。 */
export interface MonthlyPlanTask {
  id: string
  scope_name?: string
  work_task: string
  sort_order?: number
  updated_at?: string
}

export interface MonthlyPlanTaskPayload {
  scope_name?: string
  work_task: string
}
