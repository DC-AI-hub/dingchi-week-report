<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue"
import { useRouter } from "vue-router"

import { useAuthStore } from "@/features/auth/store"
import { deleteReport, getDailyTasks, submitReport } from "@/features/weekly-report/api"
import { useReportList } from "@/features/weekly-report/composables/useReportList"
import type { DailyWorkTask, ReportListFilters, WeeklyReport } from "@/features/weekly-report/types"
import AlertDialog from "@/components/feedback/AlertDialog.vue"
import ConfirmDialog from "@/components/feedback/ConfirmDialog.vue"
import NoticeBridge from "@/components/feedback/NoticeBridge.vue"

import ReportFilterBar from "../components/ReportFilterBar.vue"
import ReportListTable from "../components/ReportListTable.vue"
import ReportPagination from "../components/ReportPagination.vue"
import DailyTaskDialog from "../components/DailyTaskDialog.vue"

const authStore = useAuthStore()
const router = useRouter()
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
const confirmDialogOpen = ref(false)
const confirmDialogBusy = ref(false)
const confirmDialogAction = ref<"delete" | "submit">("submit")
const confirmDialogReport = ref<WeeklyReport | null>(null)
const templateWarningOpen = ref(false)

function openCreateReport() {
  if (!authStore.activeRole?.report_template_code?.trim()) {
    templateWarningOpen.value = true
    return
  }
  void router.push({ name: createRouteName.value })
}

function queryFilters(): ReportListFilters {
  return {
    month_key: filters.month_key || undefined,
    period_start: filters.period_start || undefined,
    period_end: filters.period_end || undefined,
  }
}

async function loadReports() {
  if (!authStore.isAuthenticated) return
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
  return report.status !== "completed" && report.employee_id === authStore.user?.id
}

function canDelete(report: WeeklyReport) {
  return canEdit(report)
}

function canSubmit(report: WeeklyReport) {
  return report.status === "in_progress" && report.employee_id === authStore.user?.id
}

function canFillDaily(report: WeeklyReport) {
  return canSubmit(report)
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
  confirmDialogAction.value = "delete"
  confirmDialogReport.value = report
  confirmDialogOpen.value = true
}

async function submitOwnReport(report: WeeklyReport) {
  confirmDialogAction.value = "submit"
  confirmDialogReport.value = report
  confirmDialogOpen.value = true
}

function closeConfirmDialog() {
  if (confirmDialogBusy.value) return
  confirmDialogOpen.value = false
  confirmDialogReport.value = null
}

async function confirmReportAction() {
  const report = confirmDialogReport.value
  if (!report) return
  confirmDialogBusy.value = true
  try {
    if (confirmDialogAction.value === "delete") await deleteReport(report.id)
    else await submitReport(report.id)
    confirmDialogBusy.value = false
    closeConfirmDialog()
    reportList.resetPage()
    await loadReports()
  } catch (error) {
    reportList.errorMessage.value = error instanceof Error
      ? error.message
      : confirmDialogAction.value === "delete" ? "删除周报失败。" : "提交周报失败。"
  } finally {
    confirmDialogBusy.value = false
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
        <button class="primary-button" type="button" @click="openCreateReport">填写周报</button>
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
        :can-submit="canSubmit"
        :can-delete="canDelete"
        :can-fill-daily="canFillDaily"
        empty-message="暂无个人周报"
        @delete="removeReport"
        @submit="submitOwnReport"
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
    <ConfirmDialog
      :open="confirmDialogOpen"
      :busy="confirmDialogBusy"
      :title="confirmDialogAction === 'delete' ? '确认删除周报' : '确认提交周报'"
      :message="confirmDialogAction === 'delete'
        ? '删除后周报及其任务、日报和附件将无法恢复，请确认。'
        : '提交后，周报内容将无法修改，请确认已完成本周期周报内容的录入。'"
      :confirm-label="confirmDialogAction === 'delete' ? '确认删除' : '确认提交'"
      :confirm-variant="confirmDialogAction === 'delete' ? 'danger' : 'primary'"
      @close="closeConfirmDialog"
      @confirm="confirmReportAction"
    />
    <AlertDialog
      :open="templateWarningOpen"
      title="无法填写周报"
      message="当前职位未配置周报模板，无法填写周报。"
      @close="templateWarningOpen = false"
    />
  </div>
</template>

<style scoped src="./IndexView.css"></style>
