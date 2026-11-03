import { ref } from "vue"
import { useRouter } from "vue-router"
import type { DailyWorkTask, WeeklyReport } from "../types"

export function useReportDailyEntry(onError: (message: string) => void) {
  const open = ref(false)
  const report = ref<WeeklyReport | null>(null)
  const tasks = ref<DailyWorkTask[]>([])
  const router=useRouter()
  async function show(value:WeeklyReport){
    try{await router.push({name:"weekly-report-edit",params:{reportId:value.id},query:{section:"daily"}})}
    catch(cause){onError(cause instanceof Error?cause.message:"填写页面打开失败。")}
  }
  function close() { open.value = false; report.value = null; tasks.value = [] }
  function saved(task: DailyWorkTask) {
    const index = tasks.value.findIndex(item => item.id === task.id)
    if (index === -1) tasks.value = [...tasks.value, task]
    else tasks.value.splice(index, 1, task)
  }
  return { open, report, tasks, show, close, saved }
}
