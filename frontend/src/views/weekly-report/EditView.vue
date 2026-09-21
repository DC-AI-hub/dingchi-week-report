<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue"
import { useRoute } from "vue-router"

import NoticeBridge from "@/components/feedback/NoticeBridge.vue"
import { useAuthStore } from "@/features/auth/store"
import { createReport, getReportDetail, getReportTemplate, updateReport } from "@/features/weekly-report/api"
import type { DailyWorkTask, ReportItem, ReportMetric, ReportPayload, ReportTemplate, WeeklyReportDetail } from "@/features/weekly-report/types"

import MetricSection from "./components/MetricSection.vue"
import ReportHeader from "./components/ReportHeader.vue"
import RiskPanel from "./components/RiskPanel.vue"
import TaskPlanTable from "./components/TaskPlanTable.vue"
import DailyTaskSection from "./components/DailyTaskSection.vue"

type TaskDraft = Partial<ReportItem> & { task_code: string }
type MetricDraft = Partial<ReportMetric> & { metric_code: string }

const authStore = useAuthStore()
const route = useRoute()
const template = ref<ReportTemplate | null>(null)
const reportId = computed(() => String(route.params.reportId || ""))
const isNew = computed(() => !reportId.value)
const isAllScope = computed(() => authStore.activeRole?.scope === "all")
const isReadOnly = computed(() => {
  if (isAllScope.value) return true
  if (isNew.value) return false
  return report.status !== "active"
    || report.employee_id !== authStore.user?.id
    || report.role_code !== authStore.activeRole?.role_code
})
const isLoading = ref(true)
const isSaving = ref(false)
const errorMessage = ref("")
const successMessage = ref("")
const currentPeriodStart = mondayOf(new Date())
const report = reactive({
  id: "",
  role_code: "",
  employee_id: "",
  period_start: currentPeriodStart,
  period_end: sundayOf(new Date()),
  as_of_date: isoDate(new Date()),
  summary: "",
  risk_level: "none",
  risk_blocked: false,
  risk_reason: "",
  next_action: "",
  support_needed: "",
  expected_resolve_date: null as string | null,
  status: "active",
})
const items = ref<TaskDraft[]>([])
const metrics = ref<MetricDraft[]>([])
const dailyTasks = ref<DailyWorkTask[]>([])

function isoDate(value: Date) {
  const year = value.getFullYear()
  const month = String(value.getMonth() + 1).padStart(2, "0")
  const day = String(value.getDate()).padStart(2, "0")
  return year + "-" + month + "-" + day
}

function mondayOf(value: Date) {
  const date = new Date(value)
  const day = date.getDay() || 7
  date.setDate(date.getDate() - day + 1)
  return isoDate(date)
}

function sundayOf(value: Date) {
  const date = new Date(value)
  const day = date.getDay() || 7
  date.setDate(date.getDate() - day + 7)
  return isoDate(date)
}

function taskDraft(task: ReportItem | undefined, config: ReportTemplate["tasks"][number]): TaskDraft {
  return {
    ...(task || {}),
    task_code: task?.task_code || config.task_code,
    section_code: task?.section_code || config.section_code,
    task_name_snapshot: task?.task_name_snapshot || config.label,
    guidance_snapshot: task?.guidance_snapshot || config.guidance,
    scope_type: task?.scope_type || config.scope_type,
    progress_percent: task?.progress_percent ?? null,
    quality_percent: task?.quality_percent ?? null,
    on_time_status: task?.on_time_status || "in_progress",
    planned_completion_date: task?.planned_completion_date || "",
    actual_completion_date: task?.actual_completion_date || "",
    expected_completion_date: task?.expected_completion_date || "",
    customer_name_snapshot: task?.customer_name_snapshot || "",
    output_description: task?.output_description || "",
    progress_text: task?.progress_text || "",
    delay_reason: task?.delay_reason || "",
    next_action: task?.next_action || "",
    sort_order: task?.sort_order ?? config.sort_order,
  }
}

function metricDraft(metric: ReportMetric | undefined, config: ReportTemplate["metrics"][number]): MetricDraft {
  return {
    ...(metric || {}),
    metric_code: metric?.metric_code || config.task_code,
    metric_name_snapshot: metric?.metric_name_snapshot || config.label,
    value_type: metric?.value_type || config.value_type,
    unit: metric?.unit || config.unit,
    target_value_decimal: metric?.target_value_decimal ?? null,
    actual_value_decimal: metric?.actual_value_decimal ?? null,
    value_text: metric?.value_text || "",
    note: metric?.note || "",
  }
}

function applyDetail(detail: WeeklyReportDetail) {
  Object.assign(report, {
    id: detail.report.id,
    role_code: detail.report.role_code,
    employee_id: detail.report.employee_id,
    period_start: detail.report.period_start,
    period_end: detail.report.period_end,
    as_of_date: detail.report.as_of_date,
    summary: detail.report.summary || "",
    risk_level: detail.report.risk_level || "none",
    risk_blocked: detail.report.risk_blocked,
    risk_reason: detail.report.risk_reason || "",
    next_action: detail.report.next_action || "",
    support_needed: detail.report.support_needed || "",
    expected_resolve_date: detail.report.expected_resolve_date,
    status: detail.report.status,
  })
  items.value = template.value?.tasks.map((task) =>
    taskDraft(detail.items.find((item) => item.task_code === task.task_code), task),
  ) || detail.items.map((item) => ({ ...item, task_code: item.task_code }))
  metrics.value = template.value?.metrics.map((metric) =>
    metricDraft(detail.metrics.find((item) => item.metric_code === metric.task_code), metric),
  ) || detail.metrics.map((metric) => ({ ...metric, metric_code: metric.metric_code }))
  dailyTasks.value = detail.daily_tasks || []
}

function buildPayload(): ReportPayload {
  return {
    period_start: report.period_start,
    period_end: report.period_end,
    as_of_date: report.as_of_date,
    summary: report.summary,
    risk_level: report.risk_level,
    risk_blocked: report.risk_blocked,
    risk_reason: report.risk_reason,
    next_action: report.next_action,
    support_needed: report.support_needed,
    expected_resolve_date: report.expected_resolve_date,
    items: items.value.map((item) => ({ ...item, task_code: item.task_code })),
    metrics: metrics.value.map((metric) => ({ ...metric, metric_code: metric.metric_code })),
    attachments: [],
    daily_tasks: dailyTasks.value.map((task) => ({
      id: task.id.startsWith("draft-") ? undefined : task.id,
      work_date: task.work_date,
      work_content: task.work_content,
    })),
  }
}

async function save() {
  if (isReadOnly.value) return
  isSaving.value = true
  errorMessage.value = ""
  successMessage.value = ""
  try {
    const payload = buildPayload()
    const detail = report.id
      ? await updateReport(report.id, payload)
      : await createReport(payload)
    applyDetail(detail)
    successMessage.value = "周报已保存。"
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "保存周报失败。"
  } finally {
    isSaving.value = false
  }
}

async function load() {
  isLoading.value = true
  errorMessage.value = ""
  try {
    if (reportId.value) {
      const detail = await getReportDetail(reportId.value)
      template.value = detail.template
        || await getReportTemplate(detail.report.template_code)
      applyDetail(detail)
    } else {
      const templateCode = authStore.activeRole?.report_template_code || ""
      if (!templateCode) throw new Error("当前角色未配置周报模板。")
      template.value = await getReportTemplate(templateCode)
      items.value = template.value.tasks.map((task) => taskDraft(undefined, task))
      metrics.value = template.value.metrics.map((metric) => metricDraft(undefined, metric))
      dailyTasks.value = []
    }
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "周报加载失败。"
  } finally {
    isLoading.value = false
  }
}

onMounted(() => void load())
</script>

<template>
  <div class="report-edit-page">
    <div v-if="isLoading" class="loading-card dashboard-card">正在加载周报</div>
    <template v-else>
      <ReportHeader :report="report" :role-name="template?.role_name" />
      <NoticeBridge :warning-message="errorMessage" :reminder-message="successMessage" />

      <section class="dashboard-card form-card">
        <div class="section-heading"><h2>报告基本信息</h2></div>
        <div class="base-form-grid">
          <label>周期开始<input v-model="report.period_start" :disabled="!isNew" :min="currentPeriodStart" type="date" /></label>
          <label>周期结束<input v-model="report.period_end" :disabled="!isNew" type="date" /></label>
          <label class="summary-field">本周总结<textarea v-model="report.summary" :disabled="isReadOnly" rows="3" placeholder="概括本周关键进展和结果" /></label>
        </div>
      </section>

      <DailyTaskSection
        :report="report"
        v-model:daily-tasks="dailyTasks"
        :defer-save="isNew"
        :can-edit="!isReadOnly"
      />

      <section class="dashboard-card form-card">
        <div class="section-heading"><h2>本周工作任务</h2></div>
        <TaskPlanTable :items="items" :template-tasks="template?.tasks || []" :readonly="isReadOnly" />
      </section>

      <section class="dashboard-card form-card">
        <div class="section-heading"><h2>角色指标</h2></div>
        <MetricSection :metrics="metrics" :template-metrics="template?.metrics || []" :readonly="isReadOnly" />
      </section>

      <section class="dashboard-card form-card">
        <div class="section-heading"><h2>风险与下周行动</h2></div>
        <RiskPanel :model-value="report" :readonly="isReadOnly" />
      </section>

      <footer v-if="!isReadOnly" class="form-actions">
        <button class="primary-button" type="button" :disabled="isSaving" @click="save">
          {{ isSaving ? "保存中" : "保存周报" }}
        </button>
      </footer>
    </template>
  </div>
</template>

<style scoped src="./EditView.css"></style>
