import { computed, onMounted, reactive, ref, watch } from "vue"
import { useRouter } from "vue-router"

import { isSupportedTemplate } from "@/features/weekly-report/template-support"
import { useAuthStore } from "@/features/auth/store"
import { deleteReport, getDailyTasks, submitReport } from "@/features/weekly-report/api"
import { useReportCopy } from "@/features/weekly-report/composables/useReportCopy"
import { useReportList } from "@/features/weekly-report/composables/useReportList"
import type { DailyWorkTask, ReportListFilters, WeeklyReport } from "@/features/weekly-report/types"


export function useOwnReportList() {
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
  const reportCopy = useReportCopy(loadReports)
  const { busy: copyBusy, message: copyMessage, title: copyTitle } = reportCopy

  function openCreateReport() {
    if (!isSupportedTemplate(authStore.activeRole?.report_template_code?.trim())) {
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
  return {
    reports,
    isLoading,
    errorMessage,
    page,
    pageSize,
    total,
    totalPages,
    filters,
    openCreateReport,
    resetFilters,
    search,
    canEdit,
    canSubmit,
    canDelete,
    canFillDaily,
    authStore,
    copyBusy,
    reportCopy,
    copyMessage,
    copyTitle,
    removeReport,
    submitOwnReport,
    openDailyDialog,
    changePage,
    dailyDialogOpen,
    dailyDialogReport,
    dailyDialogTasks,
    closeDailyDialog,
    onDailySaved,
    confirmDialogOpen,
    confirmDialogBusy,
    confirmDialogAction,
    closeConfirmDialog,
    confirmReportAction,
    templateWarningOpen,
  }
}
