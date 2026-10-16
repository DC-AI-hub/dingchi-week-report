<script setup lang="ts">
import { computed, onMounted, ref } from "vue"
import { RouterLink, useRoute } from "vue-router"

import ScrollableTabs from "@/components/navigation/ScrollableTabs.vue"
import FullscreenPanel from "@/components/layout/FullscreenPanel.vue"
import NoticeBridge from "@/components/feedback/NoticeBridge.vue"
import { useAuthStore } from "@/features/auth/store"
import { getReportDetail, getReportTemplate } from "@/features/weekly-report/api"
import type { ReportTemplate, WeeklyReportDetail } from "@/features/weekly-report/types"
import { formatDateTime } from "@/utils/date"

import MetricSection from "./components/MetricSection.vue"
import MonthlyPlanTaskPanel from "@/features/monthly-plan/components/MonthlyPlanTaskPanel.vue"
import DailyTaskSection from "./components/DailyTaskSection.vue"
import ReportHeader from "./components/ReportHeader.vue"
import ReportStatusTag from "./components/ReportStatusTag.vue"
import ReportTaskTable from "./components/ReportTaskTable.vue"

const authStore = useAuthStore()
const route = useRoute()
const detail = ref<WeeklyReportDetail | null>(null)
const template = ref<ReportTemplate | null>(null)
const taskTableRef = ref<InstanceType<typeof ReportTaskTable> | null>(null)
const isLoading = ref(true)
const errorMessage = ref("")
const taskColumnPreferenceKey = computed(() =>
  `${authStore.user?.id || "anonymous"}:${detail.value?.report.template_code || "default"}`,
)

const canEdit = computed(() => Boolean(
  detail.value
  && detail.value.report.employee_id === authStore.user?.id
  && detail.value.report.status !== "completed",
))

async function load() {
  isLoading.value = true
  errorMessage.value = ""
  try {
    detail.value = await getReportDetail(String(route.params.reportId))
    template.value = detail.value.template
      || await getReportTemplate(detail.value.report.template_code)
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "周报详情加载失败。"
  } finally {
    isLoading.value = false
  }
}

function openTaskColumns() {
  taskTableRef.value?.openColumns()
}

onMounted(() => void load())
</script>

<template>
  <div class="report-detail-page">
    <div v-if="isLoading" class="loading-card dashboard-card">正在加载周报详情</div>
    <template v-else-if="detail">
      <ReportHeader
        :report="detail.report"
        :role-name="template?.role_name"
        :show-status="false"
        meta-layout="vertical"
      >
        <template #actions>
          <div :class="canEdit
            ? 'report-header-actions report-header-actions--vertical'
            : 'report-header-actions report-header-actions--status-only'">
            <div class="detail-status">
              <ReportStatusTag :status="detail.report.status" />
              <time class="detail-updated-at" :datetime="detail.report.updated_at">
                更新于 {{ formatDateTime(detail.report.updated_at) }}
              </time>
            </div>
            <RouterLink
              v-if="canEdit"
              class="primary-button"
              :to="{
                name: 'weekly-report-edit',
                params: { reportId: detail.report.id },
                query: route.query,
              }"
            >
              编辑周报
            </RouterLink>
          </div>
        </template>
      </ReportHeader>

      <section class="dashboard-card detail-card detail-monthly-plan">
        <div class="section-heading">
          <h2>月度目标</h2>
          <span v-if="detail.monthly_plan?.month_key" class="section-meta">
            {{ detail.monthly_plan.month_key }}
          </span>
        </div>
        <p class="summary-text">{{ detail.monthly_plan?.summary || "暂无月度目标" }}</p>
      </section>
      <MonthlyPlanTaskPanel
        :template-code="detail.report.template_code"
        :tasks="detail.monthly_plan_tasks || []"
        :month-key="detail.report.month_key"
        readonly
      />
      <FullscreenPanel title="本周工作任务" class="dashboard-card detail-card">
        <template #tabs>
          <ScrollableTabs v-if="taskTableRef?.deliveryMode" :items="taskTableRef.customers"
            :model-value="taskTableRef.activeCustomer" @update:model-value="taskTableRef && (taskTableRef.activeCustomer = $event)" />
        </template>
        <template #actions>
          <button class="ghost-button" type="button" @click="openTaskColumns">选择展示字段</button>
        </template>
        <ReportTaskTable
          ref="taskTableRef"
          :items="detail.items"
          :template-code="detail.report.template_code"
          :fields="template?.fields"
          :attachments="detail.attachments"
          :preference-key="taskColumnPreferenceKey"
          :show-columns-button="false"
          :show-customer-tabs="false"
        />
      </FullscreenPanel>
      <section class="dashboard-card detail-card">
        <div class="section-heading"><h2>本周总结</h2></div>
        <p class="summary-text">{{ detail.report.summary || "暂无总结" }}</p>
      </section>
      <DailyTaskSection
        :report="detail.report"
        :daily-tasks="detail.daily_tasks"
        :can-edit="canEdit"
      />
      <section class="dashboard-card detail-card">
        <div class="section-heading"><h2>职位指标</h2></div>
        <MetricSection
          :metrics="detail.metrics.map((metric) => ({ ...metric, metric_code: metric.metric_code }))"
          :template-metrics="template?.metrics || []"
          readonly
        />
      </section>
    </template>
    <div v-else class="detail-error-state">
      <NoticeBridge :warning-message="errorMessage || '未找到周报。'" />
    </div>
  </div>
</template>

<style scoped src="./DetailView.css"></style>
