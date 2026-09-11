<script setup lang="ts">
import type { WeeklyReport } from "@/features/weekly-report/types"

defineProps<{
  report?: Partial<WeeklyReport> | null
  roleName?: string
  editable?: boolean
}>()

const statusLabels: Record<string, string> = {
  draft: "草稿",
  submitted: "待审核",
  approved: "已通过",
  returned: "已退回",
}
</script>

<template>
  <section class="report-header dashboard-card">
    <div>
      <span class="section-caption">WEEKLY REPORT</span>
      <h1>{{ report?.employee_name || "填写本周周报" }}</h1>
      <p>{{ roleName || report?.role_code || "当前角色" }} · 聚焦进展、风险与下一步行动</p>
    </div>
    <div class="report-header-meta">
      <div class="period-field">
        <span>报告周期</span>
        <strong>{{ report?.period_start || "本周" }} <i>至</i> {{ report?.period_end || "周日" }}</strong>
      </div>
      <span v-if="report?.status" :class="`status-pill status-pill--${report.status}`">
        {{ statusLabels[report.status] || report.status }}
      </span>
    </div>
  </section>
</template>

<style scoped src="./ReportHeader.css"></style>
