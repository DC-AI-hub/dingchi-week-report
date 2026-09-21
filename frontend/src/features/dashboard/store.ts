import { defineStore } from "pinia"
import { ref } from "vue"

import { getDashboardSummary } from "./api"
import type { DashboardSummary } from "./types"

function emptySummary(): DashboardSummary {
  return {
    scope: "self",
    period: { start: "", end: "" },
    kpis: { planned_tasks: 0, completion_rate: 0, completed_tasks: 0, risk_items: 0 },
    trend: [],
    status_distribution: [],
    my_tasks: [],
    reports: [],
    team_tasks: [],
  }
}

export const useDashboardStore = defineStore("dashboard", () => {
  const summary = ref<DashboardSummary>(emptySummary())
  const isLoading = ref(false)
  const isLoaded = ref(false)
  const errorMessage = ref("")

  async function load() {
    isLoading.value = true
    errorMessage.value = ""
    try {
      summary.value = await getDashboardSummary()
    } catch (error) {
      summary.value = emptySummary()
      errorMessage.value = error instanceof Error ? error.message : "首页数据加载失败。"
    } finally {
      isLoaded.value = true
      isLoading.value = false
    }
  }

  return { summary, isLoading, isLoaded, errorMessage, load }
})
