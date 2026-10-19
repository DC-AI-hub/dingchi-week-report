import { itoSalesTaskTemplates as taskExamples } from "./task-templates"

/** ITO 销售 Excel 中“月度目标”行的完整填写样例。 */
const monthlyGoal = `1.1 目标客户签约？？家
1）新增机会？家
2）中标率？率
3）合同签订数？家
1.2 新签合同销售收入？？万元
1）新签合同需求数？个
2）有效入职人数？个
3、客户关系：新增教练？名、新增内线？名`

export const itoSalesMonthlyPlanSample = monthlyGoal
export const itoSalesMonthlyPlanSampleFields = [
  { label: "月度目标", value: monthlyGoal },
] as const



export const itoSalesWeeklyTaskSampleFields = taskExamples.map((task, index) => ({
  label: `任务 ${index + 1}`,
  rows: [
    { label: "客户", value: task.customer },
    { label: "工作任务", value: task.task },
    { label: "主要工作指引", value: task.work || "（暂无填写）" },
  ],
}))

export const itoSalesWeeklyTaskSample = taskExamples
  .map((task, index) => [
    `任务 ${index + 1}`,
    `客户：${task.customer}`,
    `工作任务：${task.task}`,
    `主要工作指引：${task.work || "（暂无填写）"}`,
  ].join("\n"))
  .join("\n\n")
