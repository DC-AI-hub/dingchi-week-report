import { defineStore } from "pinia"
import { ref } from "vue"

import { getDashboardSummary } from "./api"
import type { DashboardSummary } from "./types"

const previewSummary: DashboardSummary = {
  scope: "self",
  period: { start: "2026-09-07", end: "2026-09-13" },
  kpis: { planned_tasks: 3, completion_rate: 83, completed_tasks: 1, risk_items: 1 },
  trend: [
    { date: "2026-09-07", label: "周一", progress: 36, completion: 48 },
    { date: "2026-09-08", label: "周二", progress: 49, completion: 65 },
    { date: "2026-09-09", label: "周三", progress: 63, completion: 78 },
    { date: "2026-09-10", label: "周四", progress: 75, completion: 86 },
    { date: "2026-09-11", label: "周五", progress: 81, completion: 91 },
    { date: "2026-09-12", label: "周六", progress: 86, completion: 95 },
    { date: "2026-09-13", label: "周日", progress: 91, completion: 100 },
  ],
  status_distribution: [
    { name: "进行中", value: 2, color: "#f4ae2e" },
    { name: "已完成", value: 1, color: "#12b883" },
    { name: "延期/风险", value: 1, color: "#f05d5e" },
  ],
  my_tasks: [
    {
      id: "preview-1",
      report_id: "preview",
      customer_name_snapshot: "中证信息",
      task_name_snapshot: "遗留 17 人退项处置与安置方案",
      progress_percent: 80,
      quality_percent: 90,
      completion_rate: 85,
      on_time_status: "overdue",
      planned_completion_date: "2026-09-09",
      progress_text: "完成需求澄清，等待客户确认",
    },
    {
      id: "preview-2",
      report_id: "preview",
      customer_name_snapshot: "方正证券",
      task_name_snapshot: "8 人高风险流失挽回",
      progress_percent: 60,
      quality_percent: 85,
      completion_rate: 72.5,
      on_time_status: "in_progress",
      planned_completion_date: "2026-09-12",
      progress_text: "已完成首轮沟通",
    },
    {
      id: "preview-3",
      report_id: "preview",
      customer_name_snapshot: "中证信息",
      task_name_snapshot: "合同续签沟通",
      progress_percent: 90,
      quality_percent: 90,
      completion_rate: 90,
      on_time_status: "in_progress",
      planned_completion_date: "2026-09-13",
      progress_text: "客户法务确认中",
    },
  ],
  reports: [],
}

export const useDashboardStore = defineStore("dashboard", () => {
  const summary = ref<DashboardSummary>(previewSummary)
  const isLoading = ref(false)
  const errorMessage = ref("")
  const isPreview = ref(true)

  async function load() {
    isLoading.value = true
    errorMessage.value = ""
    try {
      summary.value = await getDashboardSummary()
      isPreview.value = false
    } catch (error) {
      isPreview.value = true
      errorMessage.value = error instanceof Error ? `${error.message}（当前展示预览数据）` : "后端暂不可用（当前展示预览数据）"
    } finally {
      isLoading.value = false
    }
  }

  return { summary, isLoading, errorMessage, isPreview, load }
})
