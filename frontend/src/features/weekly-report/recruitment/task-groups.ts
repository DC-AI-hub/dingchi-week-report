import type { RecruitmentTaskDraft } from "./types"
import type { EditableTask } from "../task-editing"
import type { TaskTemplateOption } from "../task-editing"

export type RecruitmentSharedField = "dimension" | "task_name" | "work_content"
const sharedFields = {
  dimension: ["dimension", "dimension_source", "dimension_template", "dimension_values"],
  task_name: ["task_name", "task_source", "task_template", "task_values"],
  work_content: ["work_content"],
} as const
export function groupKey(task: RecruitmentTaskDraft, field: RecruitmentSharedField): string {
  if (field === "dimension") return task.dimension_text_id || task.dimension_group_key || task.client_key
  if (field === "task_name") return task.task_text_id || task.task_group_key || task.client_key
  return task.work_content_text_id || task.work_content_group_key || task.client_key
}
export function templateTask(template: TaskTemplateOption): Partial<RecruitmentTaskDraft> {
  return {
    dimension: template.dimension || "", dimension_source: "template", dimension_template: template.dimension || "",
    dimension_values: Array((template.dimension || "").split(/[?？]/).length - 1).fill(""),
    task_name: template.task, task_source: "template", task_template: template.task,
    task_values: Array(template.task.split(/[?？]/).length - 1).fill(""), work_content: template.work,
  }
}
export function patchSharedTasks(tasks: RecruitmentTaskDraft[], key: string, value: Partial<EditableTask>) {
  const original = tasks.find(task => task.client_key === key)
  if (!original) return tasks
  return tasks.map(task => {
    const patch: Partial<RecruitmentTaskDraft> = task.client_key === key ? { ...value } : {}
    for (const field of ["dimension", "task_name", "work_content"] as const) {
      if (groupKey(task, field) !== groupKey(original, field)) continue
      for (const name of sharedFields[field]) if (name in value) Object.assign(patch, { [name]: value[name] })
    }
    if (!Object.keys(patch).length) return task
    const next = { ...task, ...patch, updated_at: new Date().toISOString() }
    next.completion_rate = (Number(next.progress_percent || 0) + Number(next.quality_percent || 0)) / 2
    return next
  })
}
export function insertChild(tasks: RecruitmentTaskDraft[], index: number, task: RecruitmentTaskDraft, field?: RecruitmentSharedField) {
  const next = tasks.map(row => ({ ...row }))
  const origin = next[index]
  let after = index + 1
  if (origin && field) {
    const levels: RecruitmentSharedField[] = ["dimension", "task_name", "work_content"]
    for (const level of levels.slice(0, levels.indexOf(field) + 1)) {
      const id = level === "dimension" ? "dimension_text_id" : level === "task_name" ? "task_text_id" : "work_content_text_id"
      const group = level === "dimension" ? "dimension_group_key" : level === "task_name" ? "task_group_key" : "work_content_group_key"
      Object.assign(task, { [id]: origin[id], [group]: groupKey(origin, level) })
      for (const name of sharedFields[level]) Object.assign(task, { [name]: origin[name] })
    }
    while (after < next.length && groupKey(next[after]!, field) === groupKey(origin, field)) after++
  }
  next.splice(after, 0, task)
  return next
}
