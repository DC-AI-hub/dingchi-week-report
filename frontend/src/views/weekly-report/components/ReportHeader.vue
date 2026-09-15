<script setup lang="ts">
import { getReportRoleName } from "@/features/weekly-report/constants"
import type { WeeklyReport } from "@/features/weekly-report/types"
import { formatPeriod } from "@/utils/date"

import ReportStatusTag from "./ReportStatusTag.vue"

defineProps<{
  report?: Partial<WeeklyReport> | null
  roleName?: string
}>()
</script>

<template>
  <section class="report-header dashboard-card">
    <div>
      <h1>{{ report?.employee_name || "填写周报" }}</h1>
      <p>{{ getReportRoleName(report?.role_code || "", roleName || report?.role_name) }}</p>
    </div>
    <div class="report-header-meta">
      <div class="period-field">
        <span>报告周期</span>
        <strong>{{ formatPeriod(report?.period_start, report?.period_end) }}</strong>
      </div>
      <ReportStatusTag v-if="report?.status" :status="report.status" />
    </div>
  </section>
</template>

<style scoped src="./ReportHeader.css"></style>
