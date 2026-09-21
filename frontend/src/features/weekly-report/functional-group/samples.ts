/** 职能组模板沿用交付模板的月度计划样式，内容可由职能组按月调整。 */
export const functionalMonthlyPlanSample = `2月度目标
1、净增？？人
1）新增需求：？个
2）增量入职人数：？人
3）流失控制人数：？人
4）离职替补人数：？人
2、成本控制？？元
3、回款：？？万元`

export const functionalMonthlyPlanSampleFields = [
  {
    label: "2月度目标",
    value: `1、净增？？人
1）新增需求：？个
2）增量入职人数：？人
3）流失控制人数：？人
4）离职替补人数：？人
2、成本控制？？元
3、回款：？？万元`,
  },
] as const

const functionalWeeklyTaskExamples = [
  {
    task: `1、需求目标：新增需求？个
月初有效需求数？个`,
    work: `1.1、新增需求策略：
1.2、客户关系维护：决策层、影响层、执行层客户关系维护`,
  },
  {
    task: `2、增量入职目标：入职目标？人，
1）需求数？个，需求转化率？%；
2）命中率？%；
3）招聘进程？天等`,
    work: `2.1、如客户面试进度
2.2、转包、其他供应商挖掘；
2.3、招聘协同目标：
1）简历推荐数需要达到？份；
2）到面数？份；
3）面通数？份`,
  },
  {
    task: "3、流失控制  人：离职替补  人、空岗人日   天；",
    work: "3.1流失控制举措：",
  },
  {
    task: "4、客情关系维护目标：",
    work: "4.1、客情关系维护策略：（客户拜访计划）",
  },
  {
    task: `5、成本控制目标：
1）释放成本
2）假期成本干预
3）EGM小于10%策略
4）专项成本控制等管控目标`,
    work: "5.1成本控制策略：",
  },
  {
    task: "6、风险控制：三期风险、司龄长且年限大、释放风险等管控目标",
    work: "6.1风险管控策略：",
  },
  {
    task: "7、合同续签/报价提升：",
    work: `7.1合同续签策略：
7.2报价提升策略：`,
  },
  {
    task: "8、回款目标：？万元",
    work: `8.1、回款目前流程进展：？？，主要障碍：
1）
应对措施：
1）`,
  },
] as const

/** 工作任务样例不展示客户字段，其余内容完整保留交付模板原文。 */
export const functionalWeeklyTaskSample = functionalWeeklyTaskExamples
  .flatMap(({ task, work }) => [
    `工作任务：${task}`,
    `主要工作内容：${work}`,
  ])
  .join("\n\n")

export const functionalWeeklyTaskSampleFields = functionalWeeklyTaskExamples.map(
  ({ task, work }, index) => ({
    label: `任务 ${index + 1}`,
    rows: [
      { label: "工作任务", value: task },
      { label: "主要工作内容", value: work },
    ],
  }),
)
