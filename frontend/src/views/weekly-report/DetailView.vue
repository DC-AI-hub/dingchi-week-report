<script setup lang="ts">
import { computed, onMounted, ref } from "vue"
import { RouterLink, useRoute, useRouter } from "vue-router"

import { useAuthStore } from "@/features/auth/store"
import { getReportDetail, getReportTemplate, reviewReport, submitReport } from "@/features/weekly-report/api"
import type { ReportTemplate, WeeklyReportDetail } from "@/features/weekly-report/types"

import MetricSection from "./components/MetricSection.vue"
import ReportHeader from "./components/ReportHeader.vue"
import ReviewTimeline from "./components/ReviewTimeline.vue"
import RiskPanel from "./components/RiskPanel.vue"
import TaskPlanTable from "./components/TaskPlanTable.vue"

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()
const detail = ref<WeeklyReportDetail | null>(null)
const template = ref<ReportTemplate | null>(null)
const isLoading = ref(true)
const isWorking = ref(false)
const errorMessage = ref("")
const successMessage = ref("")
const canReview = computed(() => Boolean(detail.value && detail.value.report.employee_id !== authStore.user?.id && ["team", "all"].includes(authStore.activeRole?.scope || "")))
const canSubmit = computed(() => Boolean(detail.value && detail.value.report.employee_id === authStore.user?.id && ["draft", "returned"].includes(detail.value.report.status)))

const statusLabels: Record<string, string> = { draft: "草稿", submitted: "待审核", approved: "已通过", returned: "已退回" }

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

async function submit() {
  if (!detail.value) return
  isWorking.value = true
  try { detail.value = await submitReport(detail.value.report.id); successMessage.value = "周报已提交，等待负责人审核。" } catch (error) { errorMessage.value = error instanceof Error ? error.message : "提交失败。" } finally { isWorking.value = false }
}

async function review(action: "approve" | "return") {
  if (!detail.value) return
  const comment = window.prompt(action === "approve" ? "请输入审核意见（可选）" : "请输入退回原因（必填）", "")
  if (comment === null || (action === "return" && !comment.trim())) return
  isWorking.value = true
  try { detail.value = await reviewReport(detail.value.report.id, action, comment.trim()); successMessage.value = action === "approve" ? "周报已审核通过。" : "周报已退回修改。" } catch (error) { errorMessage.value = error instanceof Error ? error.message : "审核失败。" } finally { isWorking.value = false }
}

onMounted(() => void load())
</script>

<template>
  <div class="report-detail-page">
    <div v-if="isLoading" class="loading-card dashboard-card">正在加载周报详情…</div>
    <template v-else-if="detail">
      <ReportHeader :report="detail.report" :role-name="template?.role_name" />
      <p v-if="errorMessage" class="page-alert" role="alert">{{ errorMessage }}</p>
      <p v-if="successMessage" class="page-success" role="status">{{ successMessage }}</p>

      <section class="dashboard-card detail-toolbar">
        <div><span class="toolbar-label">当前状态</span><strong>{{ statusLabels[detail.report.status] || detail.report.status }}</strong><span v-if="detail.report.review_comment" class="toolbar-comment">{{ detail.report.review_comment }}</span></div>
        <div class="toolbar-actions"><RouterLink v-if="canSubmit" class="ghost-button" :to="`/weekly-reports/${detail.report.id}/edit`">继续编辑</RouterLink><button v-if="canSubmit" class="primary-button" type="button" :disabled="isWorking" @click="submit">提交审核</button><button v-if="canReview && detail.report.status === 'submitted'" class="primary-button" type="button" :disabled="isWorking" @click="review('approve')">通过</button><button v-if="canReview && detail.report.status === 'submitted'" class="danger-button" type="button" :disabled="isWorking" @click="review('return')">退回</button></div>
      </section>

      <section class="dashboard-card detail-card"><div class="section-heading"><div><span class="section-caption">SUMMARY</span><h2>本周总结</h2></div></div><p class="summary-text">{{ detail.report.summary || "暂无总结" }}</p></section>
      <section class="dashboard-card detail-card"><div class="section-heading"><div><span class="section-caption">TASK PLAN</span><h2>工作任务</h2></div></div><TaskPlanTable :items="detail.items.map((item) => ({ ...item, task_code: item.task_code }))" :template-tasks="template?.tasks || []" readonly /></section>
      <section class="dashboard-card detail-card"><div class="section-heading"><div><span class="section-caption">METRICS</span><h2>角色指标</h2></div></div><MetricSection :metrics="detail.metrics.map((metric) => ({ ...metric, metric_code: metric.metric_code }))" :template-metrics="template?.metrics || []" readonly /></section>
      <section class="dashboard-card detail-card"><div class="section-heading"><div><span class="section-caption">RISK & ACTION</span><h2>风险与行动</h2></div></div><RiskPanel :model-value="detail.report" readonly /></section>
      <section class="dashboard-card detail-card"><div class="section-heading"><div><span class="section-caption">REVIEW HISTORY</span><h2>审核记录</h2></div></div><ReviewTimeline :history="detail.history" /></section>
    </template>
    <p v-else class="page-alert" role="alert">{{ errorMessage || "未找到周报。" }} <button class="text-button" type="button" @click="router.back">返回</button></p>
  </div>
</template>

<style scoped src="./DetailView.css"></style>
