<script setup lang="ts">
import { computed, onMounted, ref } from "vue"
import { RouterLink, useRoute } from "vue-router"

import BackButton from "@/components/navigation/BackButton.vue"
import { useAuthStore } from "@/features/auth/store"
import { getReportDetail, getReportTemplate } from "@/features/weekly-report/api"
import type { ReportTemplate, WeeklyReportDetail } from "@/features/weekly-report/types"
import { formatDateTime } from "@/utils/date"

import MetricSection from "./components/MetricSection.vue"
import ReportHeader from "./components/ReportHeader.vue"
import ReportStatusTag from "./components/ReportStatusTag.vue"
import RiskPanel from "./components/RiskPanel.vue"
import TaskPlanTable from "./components/TaskPlanTable.vue"

const authStore = useAuthStore()
const route = useRoute()
const detail = ref<WeeklyReportDetail | null>(null)
const template = ref<ReportTemplate | null>(null)
const isLoading = ref(true)
const errorMessage = ref("")

const canEdit = computed(() => Boolean(
  detail.value
  && detail.value.report.employee_id === authStore.user?.id
  && detail.value.report.status === "active",
))

async function load() {
  isLoading.value = true
  errorMessage.value = ""
  try {
    detail.value = await getReportDetail(String(route.params.reportId))
    template.value = await getReportTemplate(detail.value.report.role_code)
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "周报详情加载失败。"
  } finally {
    isLoading.value = false
  }
}

onMounted(() => void load())
</script>

<template>
  <div class="report-detail-page">
    <div v-if="isLoading" class="loading-card dashboard-card">正在加载周报详情</div>
    <template v-else-if="detail">
      <BackButton :to="{ name: 'weekly-reports' }" />
      <ReportHeader :report="detail.report" :role-name="template?.role_name" />

      <section class="dashboard-card detail-toolbar">
        <div class="detail-status">
          <span>当前状态</span>
          <ReportStatusTag :status="detail.report.status" />
          <span>更新时间 {{ formatDateTime(detail.report.updated_at) }}</span>
        </div>
        <RouterLink
          v-if="canEdit"
          class="primary-button"
          :to="{
            name: detail.report.role_code === 'delivery_specialist'
              ? 'delivery-specialist-report-edit'
              : 'weekly-report-edit',
            params: { reportId: detail.report.id },
          }"
        >
          编辑周报
        </RouterLink>
      </section>

      <section class="dashboard-card detail-card">
        <div class="section-heading"><h2>本周总结</h2></div>
        <p class="summary-text">{{ detail.report.summary || "暂无总结" }}</p>
      </section>
      <section class="dashboard-card detail-card">
        <div class="section-heading"><h2>工作任务</h2></div>
        <TaskPlanTable
          :items="detail.items.map((item) => ({ ...item, task_code: item.task_code }))"
          :template-tasks="template?.tasks || []"
          readonly
        />
      </section>
      <section class="dashboard-card detail-card">
        <div class="section-heading"><h2>角色指标</h2></div>
        <MetricSection
          :metrics="detail.metrics.map((metric) => ({ ...metric, metric_code: metric.metric_code }))"
          :template-metrics="template?.metrics || []"
          readonly
        />
      </section>
      <section class="dashboard-card detail-card">
        <div class="section-heading"><h2>风险与行动</h2></div>
        <RiskPanel :model-value="detail.report" readonly />
      </section>
    </template>
    <p v-else class="page-alert" role="alert">
      {{ errorMessage || "未找到周报。" }}
      <BackButton />
    </p>
  </div>
</template>

<style scoped src="./DetailView.css"></style>
