<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue"
import { useRoute, useRouter } from "vue-router"

import { useAuthStore } from "@/features/auth/store"
import { createReport, getReportDetail, getReportTemplate, submitReport, updateReport } from "@/features/weekly-report/api"
import type { ReportItem, ReportMetric, ReportPayload, ReportTemplate, WeeklyReportDetail } from "@/features/weekly-report/types"

import MetricSection from "./components/MetricSection.vue"
import ReportHeader from "./components/ReportHeader.vue"
import RiskPanel from "./components/RiskPanel.vue"
import TaskPlanTable from "./components/TaskPlanTable.vue"

type TaskDraft = Partial<ReportItem> & { task_code: string }
type MetricDraft = Partial<ReportMetric> & { metric_code: string }

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()
const template = ref<ReportTemplate | null>(null)
const reportId = computed(() => String(route.params.reportId || ""))
const isNew = computed(() => !reportId.value)
const isReadOnly = ref(false)
const isLoading = ref(true)
const isSaving = ref(false)
const errorMessage = ref("")
const successMessage = ref("")
const report = reactive({
  id: "",
  period_start: mondayOf(new Date()),
  period_end: sundayOf(new Date()),
  as_of_date: isoDate(new Date()),
  summary: "",
  risk_level: "none",
  risk_blocked: false,
  risk_reason: "",
  next_action: "",
  support_needed: "",
  expected_resolve_date: null as string | null,
  status: "draft",
})
const items = ref<TaskDraft[]>([])
const metrics = ref<MetricDraft[]>([])

function isoDate(value: Date) { return value.toISOString().slice(0, 10) }
function mondayOf(value: Date) { const date = new Date(value); date.setDate(date.getDate() - date.getDay() + (date.getDay() === 0 ? -6 : 1)); return isoDate(date) }
function sundayOf(value: Date) { const date = new Date(`${mondayOf(value)}T00:00:00`); date.setDate(date.getDate() + 6); return isoDate(date) }

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
  items.value = template.value?.tasks.map((task) => taskDraft(detail.items.find((item) => item.task_code === task.task_code), task)) || detail.items.map((item) => ({ ...item, task_code: item.task_code }))
  metrics.value = template.value?.metrics.map((metric) => metricDraft(detail.metrics.find((item) => item.metric_code === metric.task_code), metric)) || detail.metrics.map((metric) => ({ ...metric, metric_code: metric.metric_code }))
  isReadOnly.value = !isNew.value && !["draft", "returned"].includes(detail.report.status)
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
    evidence: [],
  }
}

async function save(shouldSubmit = false) {
  if (isReadOnly.value) return
  isSaving.value = true
  errorMessage.value = ""
  successMessage.value = ""
  try {
    const payload = buildPayload()
    const detail = report.id ? await updateReport(report.id, payload) : await createReport(payload)
    applyDetail(detail)
    if (shouldSubmit) {
      const submitted = await submitReport(detail.report.id)
      applyDetail(submitted)
      successMessage.value = "周报已提交，等待负责人审核。"
    } else {
      successMessage.value = "草稿已保存。"
    }
    if (!report.id) report.id = detail.report.id
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "保存失败，请检查填写内容。"
  } finally {
    isSaving.value = false
  }
}

async function load() {
  isLoading.value = true
  errorMessage.value = ""
  try {
    const roleCode = authStore.activeRole?.role_code || ""
    template.value = await getReportTemplate(roleCode)
    if (reportId.value) {
      applyDetail(await getReportDetail(reportId.value))
    } else {
      items.value = template.value.tasks.map((task) => taskDraft(undefined, task))
      metrics.value = template.value.metrics.map((metric) => metricDraft(undefined, metric))
    }
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "模板加载失败，请稍后重试。"
  } finally {
    isLoading.value = false
  }
}

onMounted(() => void load())
</script>

<template>
  <div class="report-edit-page">
    <div v-if="isLoading" class="loading-card dashboard-card">正在加载周报模板…</div>
    <template v-else>
      <ReportHeader :report="report" :role-name="template?.role_name" />
      <p v-if="errorMessage" class="page-alert" role="alert">{{ errorMessage }}</p>
      <p v-if="successMessage" class="page-success" role="status">{{ successMessage }}</p>
      <p v-if="isReadOnly" class="page-alert">该周报已提交或审核完成，当前仅支持查看。</p>

      <section class="dashboard-card form-card">
        <div class="section-heading"><div><span class="section-caption">PERIOD</span><h2>报告基本信息</h2></div></div>
        <div class="base-form-grid">
          <label>周期开始<input v-model="report.period_start" :disabled="isReadOnly" type="date" /></label>
          <label>周期结束<input v-model="report.period_end" :disabled="isReadOnly" type="date" /></label>
          <label>统计截至<input v-model="report.as_of_date" :disabled="isReadOnly" type="date" /></label>
          <label class="summary-field">本周总结<textarea v-model="report.summary" :disabled="isReadOnly" rows="3" placeholder="用一句话概括本周关键进展和结果" /></label>
        </div>
      </section>

      <section class="dashboard-card form-card">
        <div class="section-heading"><div><span class="section-caption">TASK PLAN</span><h2>本周工作任务</h2></div><span class="section-note">进度与质量均按 0—100 填写</span></div>
        <TaskPlanTable :items="items" :template-tasks="template?.tasks || []" :readonly="isReadOnly" />
      </section>

      <section class="dashboard-card form-card">
        <div class="section-heading"><div><span class="section-caption">METRICS</span><h2>角色指标</h2></div></div>
        <MetricSection :metrics="metrics" :template-metrics="template?.metrics || []" :readonly="isReadOnly" />
      </section>

      <section class="dashboard-card form-card">
        <div class="section-heading"><div><span class="section-caption">RISK & ACTION</span><h2>风险与下周行动</h2></div></div>
        <RiskPanel :model-value="report" :readonly="isReadOnly" />
      </section>

      <footer v-if="!isReadOnly" class="form-actions">
        <button class="ghost-button" type="button" :disabled="isSaving" @click="save(false)">{{ isSaving ? "保存中…" : "保存草稿" }}</button>
        <button class="primary-button" type="button" :disabled="isSaving" @click="save(true)">{{ isSaving ? "提交中…" : "保存并提交" }}</button>
      </footer>
    </template>
  </div>
</template>

<style scoped src="./EditView.css"></style>
