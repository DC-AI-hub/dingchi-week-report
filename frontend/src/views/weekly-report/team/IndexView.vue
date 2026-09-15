<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue"
import { RouterLink } from "vue-router"

import { listGroups } from "@/features/directory/api"
import type { DirectoryGroup } from "@/features/directory/types"
import { useAuthStore } from "@/features/auth/store"
import { deleteReport } from "@/features/weekly-report/api"
import { useReportList } from "@/features/weekly-report/composables/useReportList"
import type { ReportListFilters, WeeklyReport } from "@/features/weekly-report/types"

import ReportFilterBar from "../components/ReportFilterBar.vue"
import ReportListTable from "../components/ReportListTable.vue"
import ReportPagination from "../components/ReportPagination.vue"

type ReportTab = "self" | "team"

const authStore = useAuthStore()
const reportList = useReportList()
const activeTab = ref<ReportTab>("self")
const groups = ref<DirectoryGroup[]>([])
const filters = reactive({
  month_key: "",
  period_start: "",
  period_end: "",
  group_id: "",
})
const reports = computed(() => reportList.reports.value)
const isLoading = computed(() => reportList.isLoading.value)
const errorMessage = computed(() => reportList.errorMessage.value)
const page = computed(() => reportList.page.value)
const pageSize = computed(() => reportList.pageSize.value)
const total = computed(() => reportList.total.value)
const totalPages = computed(() => reportList.totalPages.value)
const createRouteName = computed(() => authStore.activeRole?.role_code === "delivery_specialist"
  ? "delivery-specialist-report-new"
  : "weekly-report-new")

function queryFilters(): ReportListFilters {
  return {
    month_key: filters.month_key || undefined,
    period_start: filters.period_start || undefined,
    period_end: filters.period_end || undefined,
    group_id: filters.group_id || undefined,
    employee_scope: activeTab.value,
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
  search()
}

function switchTab(tab: ReportTab) {
  if (activeTab.value === tab) return
  activeTab.value = tab
  reportList.resetPage()
  void loadReports()
}

function canEdit(report: WeeklyReport) {
  return activeTab.value === "self" && report.status === "active" && report.employee_id === authStore.user?.id
}

function canDelete(report: WeeklyReport) {
  return canEdit(report)
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

onMounted(() => {
  void Promise.all([loadReports(), loadGroups()])
})
watch(() => authStore.activeRole?.role_code, () => {
  reportList.resetPage()
  void loadReports()
})
</script>

<template>
  <div class="weekly-report-page">
    <p v-if="errorMessage" class="page-alert" role="alert">{{ errorMessage }}</p>

    <section class="dashboard-card report-list-card">
      <div class="report-list-heading">
        <h1>团队周报</h1>
        <RouterLink v-if="activeTab === 'self'" class="primary-button" :to="{ name: createRouteName }">填写周报</RouterLink>
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
        :can-delete="canDelete"
        :empty-message="activeTab === 'self' ? '暂无个人周报' : '暂无团队成员周报'"
        @delete="removeReport"
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
  </div>
</template>

<style scoped src="./IndexView.css"></style>
