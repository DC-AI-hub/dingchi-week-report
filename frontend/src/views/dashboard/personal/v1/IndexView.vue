<script setup lang="ts">
import { computed, onMounted, watch } from "vue"

import NoticeBridge from "@/components/feedback/NoticeBridge.vue"
import { useAuthStore } from "@/features/auth/store"
import { useDashboardStore } from "@/features/dashboard/store"
import type { DashboardDistribution } from "@/features/dashboard/types"

import PersonalAnalyticsGrid from "./components/PersonalAnalyticsGrid.vue"
import PersonalHomeHeader from "./components/PersonalHomeHeader.vue"
import PersonalMetricGrid from "./components/PersonalMetricGrid.vue"
import PersonalPlansPanel from "./components/PersonalPlansPanel.vue"
import PersonalResultsPanel from "./components/PersonalResultsPanel.vue"
import PersonalTaskPanel from "./components/PersonalTaskPanel.vue"

const authStore = useAuthStore()
const dashboardStore = useDashboardStore()
const summary = computed(() => dashboardStore.summary)
const plans = computed(() => summary.value.my_tasks.slice(0, 3))
const customerDistribution = computed<DashboardDistribution[]>(() => {
  const grouped = new Map<string, number>()
  for (const task of summary.value.my_tasks) {
    const customer = task.customer_name_snapshot?.trim() || "内部事项"
    grouped.set(customer, (grouped.get(customer) || 0) + 1)
  }
  const colors = ["#2d83ee", "#12b98d", "#8058e8", "#f1a82d", "#5ba8f7"]
  return Array.from(grouped.entries()).map(([name, value], index) => ({
    name,
    value,
    color: colors[index % colors.length],
  }))
})

onMounted(() => {
  void dashboardStore.load()
})

watch(() => authStore.activeRole?.role_code, () => {
  void dashboardStore.load()
})
</script>

<template>
  <div class="personal-home-page">
    <PersonalHomeHeader
      :period="summary.period"
      :role-name="authStore.activeRole?.role_name || '个人视角'"
      :user-name="authStore.user?.display_name || ''"
    />
    <NoticeBridge :warning-message="dashboardStore.errorMessage" />

    <div v-if="dashboardStore.isLoading" class="personal-state">正在加载数据…</div>
    <div v-else-if="dashboardStore.errorMessage" class="personal-state personal-state--error">
      暂无首页数据
    </div>
    <template v-else>
      <PersonalMetricGrid
        :planned-tasks="summary.kpis.planned_tasks"
        :completion-rate="summary.kpis.completion_rate"
        :completed-tasks="summary.kpis.completed_tasks"
        :plan-count="plans.length"
      />

      <PersonalAnalyticsGrid
        :planned-tasks="summary.kpis.planned_tasks"
        :trend="summary.trend"
        :status-distribution="summary.status_distribution"
        :customer-distribution="customerDistribution"
        :completion-rate="summary.kpis.completion_rate"
      />

      <div class="personal-lower-grid">
        <PersonalTaskPanel :tasks="summary.my_tasks" />
        <PersonalResultsPanel :tasks="summary.my_tasks" :reports="summary.reports" />
      </div>

      <PersonalPlansPanel :plans="plans" :period="summary.period" />
    </template>
  </div>
</template>

<style scoped src="./IndexView.css"></style>
