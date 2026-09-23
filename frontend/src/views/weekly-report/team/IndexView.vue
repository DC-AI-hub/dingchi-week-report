<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue"
import { useRoute, useRouter } from "vue-router"

import { listGroups } from "@/features/directory/api"
import type { DirectoryGroup } from "@/features/directory/types"
import { useAuthStore } from "@/features/auth/store"
import { deleteReport, submitReport } from "@/features/weekly-report/api"
import { useReportList } from "@/features/weekly-report/composables/useReportList"
import type { ReportListFilters, WeeklyReport } from "@/features/weekly-report/types"
import AlertDialog from "@/components/feedback/AlertDialog.vue"
import ConfirmDialog from "@/components/feedback/ConfirmDialog.vue"
import NoticeBridge from "@/components/feedback/NoticeBridge.vue"

import ReportFilterBar from "../components/ReportFilterBar.vue"
import ReportListTable from "../components/ReportListTable.vue"
import ReportPagination from "../components/ReportPagination.vue"

type ReportTab = "self" | "team"

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()
const reportList = useReportList()
const activeTab = ref<ReportTab>("self")
const groups = ref<DirectoryGroup[]>([])
const confirmDialogOpen = ref(false)
const confirmDialogBusy = ref(false)
const confirmDialogAction = ref<"delete" | "submit">("submit")
const confirmDialogReport = ref<WeeklyReport | null>(null)
const templateWarningOpen = ref(false)
const filters = reactive({
  month_key: "",
  period_start: "",
  period_end: "",
  group_id: "",
  employee_id: "",
})
const reports = computed(() => reportList.reports.value)
const isLoading = computed(() => reportList.isLoading.value)
const errorMessage = computed(() => reportList.errorMessage.value)
const page = computed(() => reportList.page.value)
const pageSize = computed(() => reportList.pageSize.value)
const total = computed(() => reportList.total.value)
const totalPages = computed(() => reportList.totalPages.value)
const createRouteName = computed(() => "weekly-report-new")

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
    group_id: filters.group_id || undefined,
    employee_id: filters.employee_id || undefined,
    employee_scope: activeTab.value,
  }
}

function queryValue(value: unknown) {
  return Array.isArray(value) ? String(value[0] || "") : String(value || "")
}

function syncRouteFilters() {
  filters.month_key = queryValue(route.query.month_key)
  filters.period_start = queryValue(route.query.period_start)
  filters.period_end = queryValue(route.query.period_end)
  filters.group_id = queryValue(route.query.group_id)
  filters.employee_id = queryValue(route.query.employee_id)

  const currentEmployeeId = String(authStore.user?.id || "")
  if (filters.employee_id && filters.employee_id === currentEmployeeId) {
    activeTab.value = "self"
  } else if (filters.employee_id || filters.group_id) {
    activeTab.value = "team"
  }
}

async function loadReports() {
  await reportList.load(queryFilters())
}

async function loadGroups() {
  try {
    groups.value = (await listGroups()).items
  } catch (error) {
    reportList.errorMessage.value = error instanceof Error ? error.message : "分组加载失败。"
  }
}

function search() {
  reportList.resetPage()
  void loadReports()
}

function resetFilters() {
  filters.month_key = ""
  filters.period_start = ""
  filters.period_end = ""
  filters.group_id = ""
  filters.employee_id = ""
  search()
}

function switchTab(tab: ReportTab) {
  if (activeTab.value === tab) return
  activeTab.value = tab
  // 清除首页跳转带入的目标人员/分组，避免切换到“我的周报”后仍沿用团队筛选。
  filters.employee_id = ""
  if (tab === "self") filters.group_id = ""
  reportList.resetPage()
  void loadReports()
}

function canEdit(report: WeeklyReport) {
  return activeTab.value === "self" && report.status !== "completed" && report.employee_id === authStore.user?.id
}

function canDelete(report: WeeklyReport) {
  return canEdit(report)
}

function canSubmit(report: WeeklyReport) {
  return activeTab.value === "self" && report.status === "in_progress" && report.employee_id === authStore.user?.id
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

onMounted(() => {
  syncRouteFilters()
  void Promise.all([loadReports(), loadGroups()])
})
watch(() => authStore.activeRole?.role_code, () => {
  reportList.resetPage()
  void loadReports()
})
watch(() => route.query, () => {
  syncRouteFilters()
  reportList.resetPage()
  void loadReports()
}, { deep: true })
</script>

<template>
  <div class="weekly-report-page">
    <NoticeBridge :warning-message="errorMessage" />

    <section class="dashboard-card report-list-card">
      <div class="report-list-heading">
        <h1>团队周报</h1>
        <button v-if="activeTab === 'self'" class="primary-button" type="button" @click="openCreateReport">填写周报</button>
      </div>
      <div class="report-tabs" role="tablist" aria-label="周报范围">
        <button
          class="report-tab"
          :class="{ 'is-active': activeTab === 'self' }"
          type="button"
          role="tab"
          :aria-selected="activeTab === 'self'"
          @click="switchTab('self')"
        >
          我的周报
        </button>
        <button
          class="report-tab"
          :class="{ 'is-active': activeTab === 'team' }"
          type="button"
          role="tab"
          :aria-selected="activeTab === 'team'"
          @click="switchTab('team')"
        >
          团队周报
        </button>
      </div>
      <ReportFilterBar
        v-model:month-key="filters.month_key"
        v-model:period-start="filters.period_start"
        v-model:period-end="filters.period_end"
        v-model:group-id="filters.group_id"
        :group-options="groups"
        show-group
        @reset="resetFilters"
        @search="search"
      />
      <ReportListTable
        :reports="reports"
        :scope="activeTab === 'self' ? 'self' : 'team'"
        :is-loading="isLoading"
        :can-edit="canEdit"
        :can-submit="canSubmit"
        :can-delete="canDelete"
        :empty-message="activeTab === 'self' ? '暂无个人周报' : '暂无团队成员周报'"
        @delete="removeReport"
        @submit="submitOwnReport"
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
      message="当前角色未配置周报模板，无法填写周报。"
      @close="templateWarningOpen = false"
    />
  </div>
</template>

<style scoped src="./IndexView.css"></style>
