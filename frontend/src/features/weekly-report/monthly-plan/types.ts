/** 按员工、角色、月份共用的月度计划明细。ID 为字符串，排序按数组顺序。 */
export interface MonthlyPlanTask {
  id: string
  scope_name?: string
  work_task: string
  /** 主要工作内容；旧审批快照省略时按空文本显示。 */
  work_content?: string
  sort_order?: number
  updated_at?: string
}

export interface MonthlyPlanTaskPayload {
  scope_name?: string
  work_task: string
  work_content?: string
}
