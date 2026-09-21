/** 招聘周报 Excel 中“月计划”行的填写样例，保留原文换行。 */
const monthlyPlanBody = `9月招聘目标21人
9月主攻客户及入职目标(按客户汇总):港交所科技4人、中信期货4人，国信证券3人、中信中证2人、广发
有效简历数300份，
入职人数21人:目标:客户筛通>=42%/到面>=80%/
第一周入职4人/第二周4人/`

/** 招聘周报 Excel 中“需求管理”行的填写样例，保留原文换行。 */
const demandTask = `识别重点需求与响应`
const demandWork = `9月与交付协同重点需求确认(按周分解目标客户招聘)`
const demandOutput = `9月重点招聘目标岗位清单(含优先级、HC数)`
const demandPlanDate = `9月1号前完成重点`
const demandProgress = `完成8月重点岗位清单，已发布`

export const recruitmentMonthlyPlanSample = monthlyPlanBody

export const recruitmentMonthlyPlanSampleFields = [
  { label: "总体目标", value: monthlyPlanBody },
] as const

export const recruitmentWeeklyTaskSampleFields = [
  {
    label: "任务 1",
    rows: [
      { label: "维度", value: "总体目标" },
      { label: "工作任务", value: "9月招聘目标21人" },
      {
        label: "主要工作内容",
        value: "9月主攻客户及入职目标(按客户汇总):港交所科技4人、中信期货4人，国信证券3人、中信中证2人、广发",
      },
      { label: "输出成果", value: "有效简历数300份，\n入职人数21人:目标:客户筛通>=42%/到面>=80%/" },
      { label: "计划完成时间", value: "第一周入职4人/第二周4人/" },
    ],
  },
  {
    label: "任务 2",
    rows: [
      { label: "维度", value: "需求管理" },
      { label: "工作任务", value: demandTask },
      { label: "主要工作内容", value: demandWork },
      { label: "输出成果", value: demandOutput },
      { label: "计划完成时间", value: demandPlanDate },
      { label: "工作进展（截至月日）", value: demandProgress },
    ],
  },
  { label: "任务 3", rows: [{ label: "维度", value: "其他" }] },
] as const

export const recruitmentWeeklyTaskSample = recruitmentWeeklyTaskSampleFields
  .flatMap((task) => [
    task.label,
    ...task.rows.map((row) => `${row.label}：${row.value}`),
  ])
  .join("\n")
