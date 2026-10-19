import { splitTaskBlocks } from "@/features/weekly-report/task-groups"
import { createId } from "@/utils/id"
import { renderTaskTemplate } from "@/features/weekly-report/task-texts"
import type { MonthlyPlanTask } from "@/features/weekly-report/monthly-plan/types"

export type MonthlyGroupLevel = "scope" | "task"
export function monthlyGroupKey(task: MonthlyPlanTask, level: MonthlyGroupLevel): string {
  const scope = task.scope_group_key || task.id
  return level === "scope" ? scope : `${scope}:${task.task_group_key || task.id}`
}
export function splitMonthlyBlocks(value: string): string[] {
  const blocks = splitTaskBlocks(value)
  return blocks.length ? blocks : [""]
}
/** 普通换行保留，任务块下分别展开工作内容块，不凭相同文字合并独立任务。 */
export function expandMonthlyTasks(tasks: MonthlyPlanTask[]): MonthlyPlanTask[] {
  const result: MonthlyPlanTask[] = []
  for (let start = 0; start < tasks.length;) {
    const first = tasks[start]!
    let end = start + 1
    while (end < tasks.length && monthlyGroupKey(tasks[end]!, "task") === monthlyGroupKey(first, "task")) end++
    const group = tasks.slice(start, end)
    const templates = splitMonthlyBlocks(first.task_source === "template" && first.task_template ? first.task_template : first.work_task)
    if (templates.length === 1 && group.every(task => splitMonthlyBlocks(task.work_content || "").length === 1)) result.push(...group)
    else {
      let offset = 0
      for (const [taskIndex, text] of templates.entries()) {
        const count = (text.match(/[?？]/g) || []).length
        const values = (first.task_values || []).slice(offset, offset + count)
        offset += count
        const template = first.task_source === "template" ? { task_template: text, task_values: values,
          work_task: renderTaskTemplate(text, values) } : { work_task: text }
        const taskKey = taskIndex === 0 ? first.task_group_key || first.id : createId()
        for (const task of group) for (const [contentIndex, work_content] of splitMonthlyBlocks(task.work_content || "").entries()) {
          result.push({ ...task, ...template, work_content,
            id: taskIndex === 0 && contentIndex === 0 ? task.id : `draft-${createId()}`,
            scope_group_key: first.scope_group_key || first.id, task_group_key: taskKey,
          })
        }
      }
    }
    start = end
  }
  return result
}
export function patchMonthlyTasks(tasks: MonthlyPlanTask[], id: string, fields: Partial<MonthlyPlanTask>): MonthlyPlanTask[] {
  const origin = tasks.find(task => task.id === id)
  if (!origin) return tasks
  const scopeFields = ["scope_name", "dimension_source", "dimension_template", "dimension_values", "customer_source", "customer_template", "customer_values"] as const
  const taskFields = ["work_task", "task_source", "task_template", "task_values"] as const
  return expandMonthlyTasks(tasks.map(task => {
    const patch: Partial<MonthlyPlanTask> = task.id === id ? { ...fields } : {}
    for (const [level, names] of [["scope", scopeFields], ["task", taskFields]] as const) {
      if (monthlyGroupKey(task, level) !== monthlyGroupKey(origin, level)) continue
      for (const name of names) if (name in fields) Object.assign(patch, { [name]: fields[name] })
    }
    return Object.keys(patch).length ? { ...task, ...patch } : task
  }))
}
export function insertMonthlyChild(tasks: MonthlyPlanTask[], id: string, level: MonthlyGroupLevel): MonthlyPlanTask[] {
  const index = tasks.findIndex(task => task.id === id)
  const origin = tasks[index]
  if (!origin) return tasks
  const scopeKey = origin.scope_group_key || origin.id
  const child: MonthlyPlanTask = { ...origin, id: `draft-${createId()}`, scope_group_key: scopeKey,
    work_content: "", task_group_key: level === "task" ? origin.task_group_key || origin.id : createId(),
    ...(level === "scope" ? { work_task: "", task_source: "custom", task_template: "", task_values: [] } : {}),
  }
  let after = index + 1
  while (after < tasks.length && monthlyGroupKey(tasks[after]!, level) === monthlyGroupKey(origin, level)) after++
  return [...tasks.slice(0, after), child, ...tasks.slice(after)]
}
export function monthlyRowSpan(tasks: MonthlyPlanTask[], index: number, level: MonthlyGroupLevel): number {
  const key = monthlyGroupKey(tasks[index]!, level)
  if (index && monthlyGroupKey(tasks[index - 1]!, level) === key) return 0
  let count = 1
  while (index + count < tasks.length && monthlyGroupKey(tasks[index + count]!, level) === key) count++
  return count
}
