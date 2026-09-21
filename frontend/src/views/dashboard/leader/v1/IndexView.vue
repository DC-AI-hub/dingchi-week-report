<script setup lang="ts">
import { computed, markRaw, onMounted, watch } from "vue"
import { AlertTriangle, BarChart3, ClipboardCheck, FileOutput, ListChecks, Network, Target } from "lucide-vue-next"

import NoticeBridge from "@/components/feedback/NoticeBridge.vue"
import { useAuthStore } from "@/features/auth/store"
import { useDashboardStore } from "@/features/dashboard/store"
import type { DashboardDistribution, DashboardTeamTask } from "@/features/dashboard/types"

import LeaderAnalyticsGrid from "./components/LeaderAnalyticsGrid.vue"
import LeaderHomeHeader from "./components/LeaderHomeHeader.vue"
import LeaderMetricGrid from "./components/LeaderMetricGrid.vue"
import LeaderPlansPanel from "./components/LeaderPlansPanel.vue"
import LeaderRelationsPanel from "./components/LeaderRelationsPanel.vue"
import LeaderWorkGrid from "./components/LeaderWorkGrid.vue"
import type { LeaderDepartment, LeaderPlan, LeaderRelation, LeaderResult } from "./types"

const authStore = useAuthStore()
const dashboardStore = useDashboardStore()
const summary = computed(() => dashboardStore.summary)
const tasks = computed<DashboardTeamTask[]>(() => summary.value.team_tasks || [])

const roleNameMap: Record<string, string> = {
  system_admin: "系统管理员",
  president: "总裁",
  delivery_manager: "交付经理",
  delivery_specialist: "交付专员",
  delivery_assistant: "交付助理",
  recruitment_manager: "招聘经理",
  recruitment_specialist: "招聘专员",
  ito_sales: "ITO销售",
  innovation_sales: "创新业务销售",
  innovation_business_sales: "创新业务销售",
  functional_group: "职能组",
}

function formatDate(value: string | null | undefined) {
  return value ? value.slice(0, 10).replaceAll("-", ".") : "—"
}

function sectionLabel(value: string | null | undefined) {
  const labels: Record<string, string> = { overall: "总体事项", recruitment: "招聘工作", delivery: "交付工作", sales: "销售工作", risk: "风险事项", other: "其他事项" }
  return labels[value || ""] || value || "其他事项"
}

function splitCollaborators(value: string | null | undefined) {
  return (value || "").split(/[、,，;/；]/).map((item) => item.trim()).filter(Boolean)
}

const departments = computed<LeaderDepartment[]>(() => {
  const grouped = new Map<string, { total: number; count: number }>()
  for (const task of tasks.value) {
    const name = task.group_name || "未分组"
    const existing = grouped.get(name) || { total: 0, count: 0 }
    existing.total += Number(task.completion_rate || 0)
    existing.count += 1
    grouped.set(name, existing)
  }
  if (!grouped.size) {
    for (const report of summary.value.reports) {
      const name = report.group_name || "未分组"
      const existing = grouped.get(name) || { total: 0, count: 0 }
      existing.total += Number(report.completion_rate || 0)
      existing.count += 1
      grouped.set(name, existing)
    }
  }
  return Array.from(grouped, ([name, value]) => ({ name, rate: value.count ? Math.round(value.total / value.count) : 0, taskCount: value.count }))
    .sort((left, right) => right.rate - left.rate || right.taskCount - left.taskCount)
    .slice(0, 4)
})

const outputDistribution = computed<DashboardDistribution[]>(() => {
  const colors = ["#168cff", "#00bcd7", "#ffca38", "#944aff", "#12b98d"]
  const grouped = new Map<string, number>()
  for (const task of tasks.value) {
    const key = sectionLabel(task.section_code)
    grouped.set(key, (grouped.get(key) || 0) + 1)
  }
  return Array.from(grouped, ([name, value], index) => ({ name, value, color: colors[index % colors.length] }))
    .sort((left, right) => right.value - left.value)
    .slice(0, 5)
})

const results = computed<LeaderResult[]>(() => tasks.value.filter((task) => Boolean(task.output_description?.trim())).slice(0, 4).map((task) => ({
  id: task.id,
  name: task.output_description || "",
  owner: task.employee_name,
  category: sectionLabel(task.section_code),
  file: task.document_links || "—",
})))

const plans = computed<LeaderPlan[]>(() => [...tasks.value].sort((left, right) => String(left.planned_completion_date || "").localeCompare(String(right.planned_completion_date || ""))).slice(0, 4).map((task) => ({
  id: task.id,
  name: task.task_name_snapshot || "未命名任务",
  note: task.progress_text || task.work_content || "暂无说明",
  date: formatDate(task.planned_completion_date),
  owner: task.employee_name,
})))

const relations = computed<LeaderRelation[]>(() => {
  const grouped = new Map<string, number>()
  for (const task of tasks.value) {
    for (const name of splitCollaborators(task.collaborator_names)) grouped.set(name, (grouped.get(name) || 0) + 1)
  }
  return Array.from(grouped, ([name, count]) => ({ id: name, name, count })).sort((left, right) => right.count - left.count).slice(0, 6)
})

const planCoverage = computed(() => {
  if (!tasks.value.length) return 0
  return Math.round((tasks.value.filter((task) => Boolean(task.planned_completion_date)).length / tasks.value.length) * 100)
})

const metricCards = computed(() => [
  { label: "本周任务", value: summary.value.kpis.planned_tasks, hint: "当前周期任务总数", tone: "blue" as const, icon: markRaw(ListChecks) },
  { label: "整体完成率", value: `${Math.round(summary.value.kpis.completion_rate)}%`, hint: "进展与质量综合", tone: "purple" as const, icon: markRaw(Target) },
  { label: "计划覆盖率", value: `${planCoverage.value}%`, hint: "已设置计划完成时间", tone: "green" as const, icon: markRaw(ClipboardCheck) },
  { label: "成果输出", value: results.value.length, hint: "本周已沉淀成果", tone: "amber" as const, icon: markRaw(FileOutput) },
  { label: "协同人数", value: relations.value.length, hint: "参与跨团队协作", tone: "red" as const, icon: markRaw(Network) },
])

onMounted(() => { void dashboardStore.load() })
watch(() => authStore.activeRole?.role_code, () => { void dashboardStore.load() })
</script>

<template>
  <div class="leader-home-page">
    <LeaderHomeHeader :period="summary.period" :role-name="roleNameMap[authStore.activeRole?.role_code || ''] || authStore.activeRole?.role_name || '领导视角'" :user-name="authStore.user?.display_name || ''" />
    <NoticeBridge :warning-message="dashboardStore.errorMessage" />

    <div v-if="dashboardStore.isLoading" class="leader-state">正在加载领导首页数据…</div>
    <div v-else-if="dashboardStore.errorMessage" class="leader-state leader-state--error"><AlertTriangle :size="18" />暂无领导首页数据</div>
    <template v-else>
      <LeaderMetricGrid :cards="metricCards" />
      <LeaderAnalyticsGrid :trend="summary.trend" :departments="departments" :output-distribution="outputDistribution" :output-total="tasks.length" :completion-rate="summary.kpis.completion_rate" />
      <LeaderWorkGrid :tasks="tasks" :results="results" />
      <div class="leader-bottom-grid">
        <LeaderPlansPanel :plans="plans" />
        <LeaderRelationsPanel :relations="relations" />
      </div>
    </template>
  </div>
</template>

<style scoped src="./IndexView.css"></style>
