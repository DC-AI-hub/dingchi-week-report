import type { TaskTextMetadata } from "../task-texts"

/** 按员工、角色、月份共用的月度计划明细。ID 为字符串，排序按数组顺序。 */
export interface MonthlyPlanTask extends Pick<TaskTextMetadata, "task_source" | "task_template" | "task_values" | "dimension_source" | "dimension_template" | "dimension_values" | "customer_source" | "customer_template" | "customer_values"> {
  id: string
  scope_name?: string
  work_task: string
  /** 主要工作内容；旧审批快照省略时按空文本显示。 */
  work_content?: string
  sort_order?: number
  updated_at?: string
}

export interface MonthlyPlanTaskPayload extends Pick<TaskTextMetadata, "task_source" | "task_template" | "task_values" | "dimension_source" | "dimension_template" | "dimension_values" | "customer_source" | "customer_template" | "customer_values"> {
  scope_name?: string
  work_task: string
  work_content?: string
}
