<script setup lang="ts">
import { computed, markRaw, onMounted, watch } from "vue"
import { AlertTriangle, ClipboardCheck, Handshake, ListChecks, Target, UsersRound } from "lucide-vue-next"

import NoticeBridge from "@/components/feedback/NoticeBridge.vue"
import { useAuthStore } from "@/features/auth/store"
import { useDashboardStore } from "@/features/dashboard/store"

import TeamAnalyticsGrid from "./components/TeamAnalyticsGrid.vue"
import TeamHomeHeader from "./components/TeamHomeHeader.vue"
import TeamMetricGrid from "./components/TeamMetricGrid.vue"
import TeamPlansPanel from "./components/TeamPlansPanel.vue"
import TeamReportsPanel from "./components/TeamReportsPanel.vue"
import type { TeamMemberSummary, TeamPlanEntry, TeamReportEntry } from "./types"

const authStore = useAuthStore()
const dashboardStore = useDashboardStore()
const summary = computed(() => dashboardStore.summary)

const roleNameMap: Record<string, string> = {
  system_admin: "系统管理员",
  president: "总裁",
  delivery_manager: "交付经理",
  delivery_specialist: "交付专员",
  delivery_assistant: "交付助理",
  recruitment_manager: "招聘经理",
  recruitment_specialist: "招聘专员",
  ito_sales: "ITO销售",
  innovation_business_sales: "创新业务销售",
}

const reports = computed<TeamReportEntry[]>(() => summary.value.reports.map((report) => ({
  id: report.id,
  employeeId: report.employee_id,
  employeeName: report.employee_name || "未命名成员",
  roleName: roleNameMap[report.role_code] || report.role_code || "团队成员",
  groupName: report.group_name || "未分组",
  summary: report.summary || "",
  completionRate: Number(report.completion_rate || 0),
  status: report.status || "进行中",
  riskLevel: report.risk_level || "none",
  periodStart: formatDate(report.period_start),
  periodEnd: formatDate(report.period_end),
})))

const members = computed<TeamMemberSummary[]>(() => {
  const map = new Map<string, TeamMemberSummary>()
  for (const report of reports.value) {
    const existing = map.get(report.employeeId)
    if (existing) {
      existing.completionRate = Math.max(existing.completionRate, report.completionRate)
      existing.riskCount += report.riskLevel !== "none" ? 1 : 0
      continue
    }
    map.set(report.employeeName, {
      employeeId: report.employeeId,
      employeeName: report.employeeName,
      roleName: report.roleName,
      groupName: report.groupName,
      completionRate: report.completionRate,
      taskCount: 0,
      riskCount: report.riskLevel !== "none" ? 1 : 0,
    })
  }
  return Array.from(map.values()).sort((left, right) => right.completionRate - left.completionRate)
})

const myReport = computed(() => {
  const userId = authStore.user?.id
  if (!userId) return null
  const report = summary.value.reports.find((item) => item.employee_id === userId)
  return report ? reports.value.find((item) => item.id === report.id) || null : null
})

const plans = computed<TeamPlanEntry[]>(() => reports.value.slice(0, 5).map((report) => ({
  id: `plan-${report.id}`,
  title: report.summary || `${report.employeeName}本周重点行动`,
  owner: report.employeeName,
  detail: report.groupName || report.roleName,
  status: report.status.includes("完成") ? "已完成" : "进行中",
  start: report.periodStart,
  end: report.periodEnd,
})))

const metricCards = computed(() => [
  { label: "团队成员", value: members.value.length, hint: "已提交本周周报", tone: "blue" as const, icon: markRaw(UsersRound) },
  { label: "周报提交", value: reports.value.length, hint: "当前周期已提交", tone: "purple" as const, icon: markRaw(ClipboardCheck) },
  { label: "团队完成率", value: `${Math.round(summary.value.kpis.completion_rate)}%`, hint: "进展与质量综合", tone: "green" as const, icon: markRaw(Target) },
  { label: "团队任务", value: summary.value.kpis.planned_tasks, hint: "当前周期任务总数", tone: "orange" as const, icon: markRaw(ListChecks) },
  { label: "风险 / 协同", value: summary.value.kpis.risk_items, hint: "需要团队持续关注", tone: "red" as const, icon: markRaw(Handshake) },
])

onMounted(() => {
  void dashboardStore.load()
})

watch(() => authStore.activeRole?.role_code, () => {
  void dashboardStore.load()
})

function formatDate(value: string) {
  if (!value) return ""
  return value.slice(0, 10).replaceAll("-", ".")
}
</script>

<template>
  <div class="team-home-page">
    <TeamHomeHeader
      :period="summary.period"
      :role-name="authStore.activeRole?.role_name || '团队视角'"
      :user-name="authStore.user?.display_name || ''"
    />
    <NoticeBridge :warning-message="dashboardStore.errorMessage" />

    <div v-if="dashboardStore.isLoading" class="team-state">正在加载团队数据…</div>
    <div v-else-if="dashboardStore.errorMessage" class="team-state team-state--error">
      <AlertTriangle :size="18" />暂无团队首页数据
    </div>
    <template v-else>
      <TeamMetricGrid :cards="metricCards" />
      <TeamAnalyticsGrid
        :trend="summary.trend"
        :status-distribution="summary.status_distribution"
        :task-total="summary.kpis.planned_tasks"
        :members="members"
      />
      <TeamReportsPanel :reports="reports" :my-report="myReport" />
      <TeamPlansPanel :plans="plans" />
    </template>
  </div>
</template>

<style scoped src="./IndexView.css"></style>
