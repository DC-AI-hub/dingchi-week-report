import { ref } from "vue"
import { getDailyTasks } from "../api"
import type { DailyWorkTask, WeeklyReport } from "../types"

export function useReportDailyEntry(onError: (message: string) => void) {
  const open = ref(false)
  const report = ref<WeeklyReport | null>(null)
  const tasks = ref<DailyWorkTask[]>([])
  async function show(value: WeeklyReport) {
    try {
      const response = await getDailyTasks(value.id)
      report.value = value
      tasks.value = response.items
      open.value = true
    } catch (cause) { onError(cause instanceof Error ? cause.message : "日报加载失败。") }
  }
  function close() { open.value = false; report.value = null; tasks.value = [] }
  function saved(task: DailyWorkTask) {
    const index = tasks.value.findIndex(item => item.id === task.id)
    if (index === -1) tasks.value = [...tasks.value, task]
    else tasks.value.splice(index, 1, task)
  }
  return { open, report, tasks, show, close, saved }
}
