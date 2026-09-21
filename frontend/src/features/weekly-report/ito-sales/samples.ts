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

const taskExamples = [
  {
    customer: "市场开拓",
    task: `目标客户签约？家
1）新增机会点？家
2）中标率？%`,
    guidance: `2.1 老客户机会管理
1）老客户现有鼎驰未涉及项目/框架盘点
2）老客户关系盘点及评估新机会的成功率
3）确定目标客户
4）制定老客户新机会策略并实施

2.2 新客户机会管理
1）全量市场机会扫描
2）构建客户朋友圈
3）新客户历年招投标信息分析
4）盘点鼎驰可整合资源
5）明确新客户机会目标
6）形成新机会策略并实施

2.3 招投标管理
1）分析客户招标文件并形成投标策略
2）协同商务专员开展投标文件撰写`,
  },
  {
    customer: "客户关系管理（其中新客户可根据目标客户数量进行增减）",
    task: `老客户A关系管理
1）老客户教练？名，内线？名
2）老客户关系建立？%`,
    guidance: `3.1 老客户中高层关系推进
1）制定老客户关系管理策略
2）制定并实施关键客户一企一策（实施客户分级管理）
3）协同交付或总裁开展老客户中高层拜访
4）节假日/客户特别关注活动的关怀
4）完善客户画像`,
  },
  {
    customer: "客户关系管理（其中新客户可根据目标客户数量进行增减）",
    task: `新客户A关系管理（目标客户）
1）教练？名，内线？名
2）新客户画像`,
    guidance: `3.2 新客户关系推进
1）制定新客户画像
2）明确新客户决策链
3）制定新客户关系策略
4）客户拜访管理`,
  },
  {
    customer: "客户关系管理（其中新客户可根据目标客户数量进行增减）",
    task: `新客户B关系管理（目标客户）
1）教练？名，内线？名
2）新客户画像`,
    guidance: `3.2 新客户关系推进
1）制定新客户画像
2）明确新客户决策链
3）制定新客户关系策略
4）客户拜访管理`,
  },
  {
    customer: "新签合同销售收入",
    task: "1、新签合同需求目标：新增需求？个，月初有效需求数？个",
    guidance: `4.1 协同交付专员制定新增需求策略：
4.2 客户关系维护：决策层客户关系维护`,
  },
  { customer: "其他", task: "其他", guidance: "" },
] as const

export const itoSalesWeeklyTaskSampleFields = taskExamples.map((task, index) => ({
  label: `任务 ${index + 1}`,
  rows: [
    { label: "客户", value: task.customer },
    { label: "工作任务", value: task.task },
    { label: "主要工作指引", value: task.guidance || "（暂无填写）" },
  ],
}))

export const itoSalesWeeklyTaskSample = taskExamples
  .map((task, index) => [
    `任务 ${index + 1}`,
    `客户：${task.customer}`,
    `工作任务：${task.task}`,
    `主要工作指引：${task.guidance || "（暂无填写）"}`,
  ].join("\n"))
  .join("\n\n")
