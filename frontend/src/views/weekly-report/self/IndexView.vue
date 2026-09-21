<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue"
import { RouterLink } from "vue-router"

import { useAuthStore } from "@/features/auth/store"
import { deleteReport, getDailyTasks } from "@/features/weekly-report/api"
import { useReportList } from "@/features/weekly-report/composables/useReportList"
import type { DailyWorkTask, ReportListFilters, WeeklyReport } from "@/features/weekly-report/types"
import NoticeBridge from "@/components/feedback/NoticeBridge.vue"

import ReportFilterBar from "../components/ReportFilterBar.vue"
import ReportListTable from "../components/ReportListTable.vue"
import ReportPagination from "../components/ReportPagination.vue"
import DailyTaskDialog from "../components/DailyTaskDialog.vue"

const authStore = useAuthStore()
const reportList = useReportList()
const filters = reactive({
  month_key: "",
  period_start: "",
  period_end: "",
})
const reports = computed(() => reportList.reports.value)
const isLoading = computed(() => reportList.isLoading.value)
const errorMessage = computed(() => reportList.errorMessage.value)
const page = computed(() => reportList.page.value)
const pageSize = computed(() => reportList.pageSize.value)
const total = computed(() => reportList.total.value)
const totalPages = computed(() => reportList.totalPages.value)
// 周报页面由当前角色绑定的 report_template_code 在路由目标内部解析，
// 列表页不再按角色编码硬编码分流。
const createRouteName = computed(() => "weekly-report-new")
const dailyDialogOpen = ref(false)
const dailyDialogReport = ref<WeeklyReport | null>(null)
const dailyDialogTasks = ref<DailyWorkTask[]>([])

function queryFilters(): ReportListFilters {
  return {
    month_key: filters.month_key || undefined,
    period_start: filters.period_start || undefined,
    period_end: filters.period_end || undefined,
  }
}

async function loadReports() {
  await reportList.load(queryFilters())
}

function search() {
  reportList.resetPage()
  void loadReports()
}

function resetFilters() {
  filters.month_key = ""
  filters.period_start = ""
  filters.period_end = ""
  search()
}

function canEdit(report: WeeklyReport) {
  return report.status === "active" && report.employee_id === authStore.user?.id
}

function canDelete(report: WeeklyReport) {
  return canEdit(report)
}

function canFillDaily(report: WeeklyReport) {
  return canEdit(report)
}

async function openDailyDialog(report: WeeklyReport) {
  try {
    const response = await getDailyTasks(report.id)
    dailyDialogReport.value = report
    dailyDialogTasks.value = response.items
    dailyDialogOpen.value = true
  } catch (error) {
    reportList.errorMessage.value = error instanceof Error ? error.message : "日报加载失败。"
  }
}

function closeDailyDialog() {
  dailyDialogOpen.value = false
  dailyDialogReport.value = null
  dailyDialogTasks.value = []
}

function onDailySaved(task: DailyWorkTask) {
  const index = dailyDialogTasks.value.findIndex((item) => item.id === task.id)
  if (index === -1) dailyDialogTasks.value = [...dailyDialogTasks.value, task]
  else dailyDialogTasks.value.splice(index, 1, task)
}

async function removeReport(report: WeeklyReport) {
  if (!window.confirm("确认删除这份周报吗？删除后不可恢复。")) return
  try {
    await deleteReport(report.id)
    reportList.resetPage()
    await loadReports()
  } catch (error) {
    reportList.errorMessage.value = error instanceof Error ? error.message : "删除周报失败。"
  }
}

function changePage(page: number) {
  reportList.setPage(page)
  void loadReports()
}

onMounted(() => void loadReports())
watch(() => authStore.activeRole?.role_code, () => {
  reportList.resetPage()
  void loadReports()
})
</script>

<template>
  <div class="weekly-report-page">
    <NoticeBridge :warning-message="errorMessage" />

    <section class="dashboard-card report-list-card">
      <div class="report-list-heading">
        <h1>我的周报</h1>
        <RouterLink class="primary-button" :to="{ name: createRouteName }">填写周报</RouterLink>
      </div>
      <ReportFilterBar
        v-model:month-key="filters.month_key"
        v-model:period-start="filters.period_start"
        v-model:period-end="filters.period_end"
        @reset="resetFilters"
        @search="search"
      />
      <ReportListTable
        :reports="reports"
        scope="self"
        :is-loading="isLoading"
        :can-edit="canEdit"
        :can-delete="canDelete"
        :can-fill-daily="canFillDaily"
        empty-message="暂无个人周报"
        @delete="removeReport"
        @daily-task="openDailyDialog"
      />
      <ReportPagination
        :page="page"
        :page-size="pageSize"
        :total="total"
        :total-pages="totalPages"
        :disabled="isLoading"
        @change="changePage"
      />
    </section>
    <DailyTaskDialog
      :open="dailyDialogOpen"
      :report="dailyDialogReport"
      :existing-tasks="dailyDialogTasks"
      @close="closeDailyDialog"
      @saved="onDailySaved"
    />
  </div>
</template>

<style scoped src="./IndexView.css"></style>
