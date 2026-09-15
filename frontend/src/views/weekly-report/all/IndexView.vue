<script setup lang="ts">
import { computed, onMounted, reactive, watch } from "vue"

import { listGroups } from "@/features/directory/api"
import type { DirectoryGroup } from "@/features/directory/types"
import { useAuthStore } from "@/features/auth/store"
import { useReportList } from "@/features/weekly-report/composables/useReportList"
import type { ReportListFilters, WeeklyReport } from "@/features/weekly-report/types"

import ReportFilterBar from "../components/ReportFilterBar.vue"
import ReportListTable from "../components/ReportListTable.vue"
import ReportPagination from "../components/ReportPagination.vue"

const authStore = useAuthStore()
const reportList = useReportList()
const groups = reactive<DirectoryGroup[]>([])
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

function queryFilters(): ReportListFilters {
  return {
    month_key: filters.month_key || undefined,
    period_start: filters.period_start || undefined,
    period_end: filters.period_end || undefined,
    group_id: filters.group_id || undefined,
  }
}

async function loadReports() {
  await reportList.load(queryFilters())
}

async function loadGroups() {
  try {
    groups.push(...(await listGroups()).items)
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

function changePage(page: number) {
  reportList.setPage(page)
  void loadReports()
}

function cannotEditOrDelete(_report: WeeklyReport) {
  return false
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
        <h1>全员周报</h1>
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
        scope="all"
        :is-loading="isLoading"
        :can-edit="cannotEditOrDelete"
        :can-delete="cannotEditOrDelete"
        empty-message="暂无符合条件的周报"
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
