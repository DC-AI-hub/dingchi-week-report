<script setup lang="ts">
import { RouterLink, type LocationQueryRaw } from "vue-router"

import { getReportRoleName } from "@/features/weekly-report/constants"
import type { WeeklyReport } from "@/features/weekly-report/types"
import { formatDateTime, formatPeriod } from "@/utils/date"

import ReportStatusTag from "./ReportStatusTag.vue"

type ReportTableScope = "self" | "team" | "all"

const props = withDefaults(
  defineProps<{
    reports: WeeklyReport[]
    scope: ReportTableScope
    isLoading?: boolean
    emptyMessage?: string
    canEdit?: (report: WeeklyReport) => boolean
    canSubmit?: (report: WeeklyReport) => boolean
    canDelete?: (report: WeeklyReport) => boolean
    canFillDaily?: (report: WeeklyReport) => boolean
    returnQuery?: LocationQueryRaw
  }>(),
  {
    isLoading: false,
    emptyMessage: "暂无周报",
    canEdit: undefined,
    canSubmit: undefined,
    canDelete: undefined,
    canFillDaily: undefined,
  },
)

const emit = defineEmits<{
  submit: [report: WeeklyReport]
  delete: [report: WeeklyReport]
  dailyTask: [report: WeeklyReport]
}>()

function canEditReport(report: WeeklyReport) {
  return props.canEdit?.(report) ?? false
}

function canDeleteReport(report: WeeklyReport) {
  return props.canDelete?.(report) ?? false
}

function canSubmitReport(report: WeeklyReport) {
  return props.canSubmit?.(report) ?? false
}

function canFillDailyReport(report: WeeklyReport) {
  return props.canFillDaily?.(report) ?? false
}

function hasActions() {
  return props.scope === "self"
}

function editRoute(report: WeeklyReport) {
  return {
    name: "weekly-report-edit",
    params: { reportId: report.id },
    query: props.returnQuery,
  }
}
</script>

<template>
  <div class="report-list-table-wrap">
    <table class="report-list-table">
      <thead>
        <tr>
          <th>周报周期</th>
          <th>所属月度</th>
          <th v-if="scope !== 'self'">填写人</th>
          <th>职位</th>
          <th v-if="scope !== 'self'">分组</th>
          <th>状态</th>
          <th>更新时间</th>
          <th v-if="hasActions()" class="actions-heading">操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="report in reports" :key="report.id">
          <td class="period-cell">
            <RouterLink
              class="period-link"
              :to="{ name: 'weekly-report-detail', params: { reportId: report.id }, query: returnQuery }"
            >
              <strong>{{ formatPeriod(report.period_start, report.period_end) }}</strong>
            </RouterLink>
          </td>
          <td class="date-cell">{{ report.month_key }}</td>
          <td v-if="scope !== 'self'">{{ report.employee_name || "—" }}</td>
          <td>{{ getReportRoleName(report.role_code, report.role_name) }}</td>
          <td v-if="scope !== 'self'">{{ report.group_name || "—" }}</td>
          <td><ReportStatusTag :status="report.status" /></td>
          <td class="date-cell">{{ formatDateTime(report.updated_at) }}</td>
          <td v-if="hasActions()" class="action-cell">
            <button
              v-if="scope === 'self' && canFillDailyReport(report)"
              class="table-action"
              type="button"
              @click="emit('dailyTask', report)"
            >
              填写日报
            </button>
            <RouterLink
              v-if="canEditReport(report)"
              class="table-action"
              :to="editRoute(report)"
            >
              编辑
            </RouterLink>
            <button
              v-if="canSubmitReport(report)"
              class="table-action"
              type="button"
              @click="emit('submit', report)"
            >
              提交
            </button>
            <button
              v-if="canDeleteReport(report)"
              class="table-action table-action--danger"
              type="button"
              @click="emit('delete', report)"
            >
              删除
            </button>
          </td>
        </tr>
        <tr v-if="isLoading">
          <td :colspan="scope === 'self' ? 6 : 7" class="empty-row">正在加载周报数据</td>
        </tr>
        <tr v-else-if="!reports.length">
          <td :colspan="scope === 'self' ? 6 : 7" class="empty-row">{{ emptyMessage }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped src="./ReportListTable.css"></style>
