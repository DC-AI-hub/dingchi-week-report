/** 交付助理 Excel 模板中的月度计划样例（原文保留换行）。 */
const monthlyPlanBody = `1、流失控制人数：？人：
1）主动离职：？人；
2）客户释放：？人；
2、离职替补人数：？人，空岗人日：？人日
3、存量收入流失：？元；存量利润流失：？元
4、成本控制：？元`

const monthlyPlanSampleValue = monthlyPlanBody

export const deliveryAssistantMonthlyPlanSample = monthlyPlanSampleValue

export const deliveryAssistantMonthlyPlanSampleFields = [
  {
    label: "总体目标",
    value: monthlyPlanSampleValue,
  },
] as const

const monthlyTaskExamples = [
  {
    task: `当月总人数：？人（存量：？人、增量：？人、试用期：？人）
1、人员流失控制目标：流失控制  人：离职替补  人、空岗人日   天；`,
    work: `1.1、正式人员流失控制策略：
1.2、试用期人员流失控制策略：
1.3、离职替补策略：
1.4、空岗人日目标为0策略：`,
  },
  { task: "2、客户释放人员：？人（存量：？人、增量：？人）", work: "2.1、客户释放人员策略：\n2.2、离职替补策略：\n2.3、减少释放成本策略：" },
  {
    task: `3、中高风险人数降低目标：
1）高风险（客户释放）管理目标：
2）中风险（三期、离职想法）管理目标：`,
    work: "3.1、高风险人数策略：\n3.2、中风险人数策略：\n3.3、风险转化策略：",
  },
  {
    task: `4、假期管控目标：
1）年假控制目标（结合结算规则和假期分布图）：当月无年假
2）事假控制目标：？天
3）其他假期管控目标：控制在？天以内或有薪假签订折算协议等`,
    work: "4.1、年假管控策略：\n4.2、事假管控策略：\n4.3、其他假期管控策略：",
  },
  {
    task: `5、EGM小于10%人员管控目标：
1）战略客户需要：？人、三期风险：？人、可替补：？人
2）本月管控目标：`,
    work: "5.1、与客户沟通涨价策略：\n5.2、冻薪、年终奖不发策略：\n5.3、员工降薪谈判策略：",
  },
  {
    task: `6、报价调整/员工调薪目标：
1）客户报价调整窗口期；
2）员工调薪/降薪目标。`,
    work: "6.1、报价提升策略：\n6.2、员工调薪/降薪策略：",
  },
  { task: "7、公积金全额缴纳专项目标：？人签订协议", work: "7.1、公积金专项沟通情况：" },
  { task: "8、薪酬确认书签订目标：当月总人数？人，未签？人，当月目标？人", work: "8.1、薪酬确认书签订策略：合同续签时、涨薪时谈、" },
  { task: "9、客情关系维护目标：", work: "9.1、客情关系维护策略：（客户拜访计划）" },
  { task: "10、员工沟通目标：", work: "10.1、员工沟通话术：" },
  { task: "11、其他成本管控专项目标：", work: "11.1、其他成本管控专项策略：" },
  { task: "12、其他工作安排：外派员工入职培训、礼品发放、体检安排等相关工作", work: "" },
] as const

/** 周任务样例完整呈现 Excel 中 A 客户的 12 条任务和对应工作内容。 */
export const deliveryAssistantWeeklyTaskSample = [
  "客户：A客户",
  ...monthlyTaskExamples.flatMap(({ task, work }) => [
    `工作任务：${task}`,
    `主要工作内容：${work || "（暂无填写）"}`,
  ]),
].join("\n\n")

export const deliveryAssistantWeeklyTaskSampleFields = [
  { label: "客户", value: "A客户" },
  ...monthlyTaskExamples.map(({ task, work }, index) => ({
    label: `任务 ${index + 1}`,
    rows: [
      { label: "工作任务", value: task },
      { label: "主要工作内容", value: work || "（暂无填写）" },
    ],
  })),
] as const
