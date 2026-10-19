import type { EditableTask } from "./task-editing"
import type { TaskTemplateOption } from "./task-editing"

export type SharedTaskField = "dimension" | "customer_name" | "task_name" | "work_content"
const sharedFields = {
  customer_name: ["customer_name", "customer_source", "customer_template", "customer_values"],
  dimension: ["dimension", "dimension_source", "dimension_template", "dimension_values"],
  task_name: ["task_name", "task_source", "task_template", "task_values"],
  work_content: ["work_content"],
} as const
export function groupKey(task: EditableTask, field: SharedTaskField): string {
  if (field === "customer_name") return task.customer_text_id || task.customer_group_key || task.client_key
  if (field === "dimension") return task.dimension_text_id || task.dimension_group_key || task.client_key
  if (field === "task_name") return task.task_text_id || task.task_group_key || task.client_key
  return task.work_content_text_id || task.work_content_group_key || task.client_key
}
export function templateTask(template: TaskTemplateOption, scope: "dimension" | "customer_name" = "dimension"): Partial<EditableTask> {
  if (scope === "customer_name") return {
    customer_name: template.customer || "", customer_source: "template", customer_template: template.customer || "",
    customer_values: Array((template.customer || "").split(/[?？]/).length - 1).fill(""),
    task_name: template.task, task_source: "template", task_template: template.task,
    task_values: Array(template.task.split(/[?？]/).length - 1).fill(""), work_content: template.work,
  }
  return {
    dimension: template.dimension || "", dimension_source: "template", dimension_template: template.dimension || "",
    dimension_values: Array((template.dimension || "").split(/[?？]/).length - 1).fill(""),
    task_name: template.task, task_source: "template", task_template: template.task,
    task_values: Array(template.task.split(/[?？]/).length - 1).fill(""), work_content: template.work,
  }
}
export function patchSharedTasks<T extends EditableTask>(tasks: T[], key: string, value: Partial<EditableTask>) {
  const original = tasks.find(task => task.client_key === key)
  if (!original) return tasks
  return tasks.map(task => {
    const patch: Partial<EditableTask> = task.client_key === key ? { ...value } : {}
    for (const field of ["dimension", "customer_name", "task_name", "work_content"] as const) {
      if (groupKey(task, field) !== groupKey(original, field)) continue
      for (const name of sharedFields[field]) if (name in value) Object.assign(patch, { [name]: value[name] })
    }
    if (!Object.keys(patch).length) return task
    const next = { ...task, ...patch, updated_at: new Date().toISOString() }
    next.completion_rate = (Number(next.progress_percent || 0) + Number(next.quality_percent || 0)) / 2
    return next
  })
}
export function insertChild<T extends EditableTask>(tasks: T[], index: number, task: T, field?: SharedTaskField, scope: "dimension" | "customer_name" = "dimension") {
  const next = tasks.map(row => ({ ...row }))
  const origin = next[index]
  let after = index + 1
  if (origin && field) {
    const levels: SharedTaskField[] = [scope, "task_name", "work_content"]
    for (const level of levels.slice(0, levels.indexOf(field) + 1)) {
      const id = level === "customer_name" ? "customer_text_id" : level === "dimension" ? "dimension_text_id" : level === "task_name" ? "task_text_id" : "work_content_text_id"
      const group = level === "customer_name" ? "customer_group_key" : level === "dimension" ? "dimension_group_key" : level === "task_name" ? "task_group_key" : "work_content_group_key"
      Object.assign(task, { [id]: origin[id], [group]: groupKey(origin, level) })
      for (const name of sharedFields[level]) Object.assign(task, { [name]: origin[name] })
    }
    while (after < next.length && groupKey(next[after]!, field) === groupKey(origin, field)) after++
  }
  next.splice(after, 0, task)
  return next
}
