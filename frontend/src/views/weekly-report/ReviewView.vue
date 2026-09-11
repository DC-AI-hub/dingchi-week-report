<script setup lang="ts">
import { computed, onMounted, ref } from "vue"

import { useAuthStore } from "@/features/auth/store"
import { getReportDetail, getReportTemplate, listReports, reviewReport } from "@/features/weekly-report/api"
import type { ReportTemplate, WeeklyReport, WeeklyReportDetail } from "@/features/weekly-report/types"

import MetricSection from "./components/MetricSection.vue"
import ReportHeader from "./components/ReportHeader.vue"
import RiskPanel from "./components/RiskPanel.vue"
import TaskPlanTable from "./components/TaskPlanTable.vue"

const authStore = useAuthStore()
const reports = ref<WeeklyReport[]>([])
const selected = ref<WeeklyReportDetail | null>(null)
const template = ref<ReportTemplate | null>(null)
const isLoading = ref(true)
const isWorking = ref(false)
const errorMessage = ref("")
const successMessage = ref("")
const canReview = computed(() => ["team", "all"].includes(authStore.activeRole?.scope || ""))

async function loadReports() {
  isLoading.value = true
  errorMessage.value = ""
  try { reports.value = (await listReports("submitted")).items; if (reports.value.length) await selectReport(reports.value[0]) } catch (error) { errorMessage.value = error instanceof Error ? error.message : "审核列表加载失败。" } finally { isLoading.value = false }
}

async function selectReport(report: WeeklyReport) {
  try { selected.value = await getReportDetail(report.id); template.value = await getReportTemplate(report.role_code) } catch (error) { errorMessage.value = error instanceof Error ? error.message : "周报详情加载失败。" }
}

async function review(action: "approve" | "return") {
  if (!selected.value) return
  const comment = window.prompt(action === "approve" ? "请输入审核意见（可选）" : "请输入退回原因（必填）", "")
  if (comment === null || (action === "return" && !comment.trim())) return
  isWorking.value = true
  try { selected.value = await reviewReport(selected.value.report.id, action, comment.trim()); successMessage.value = action === "approve" ? "已通过该周报。" : "已退回该周报。"; await loadReports() } catch (error) { errorMessage.value = error instanceof Error ? error.message : "审核失败。" } finally { isWorking.value = false }
}

onMounted(() => void loadReports())
</script>

<template>
  <div class="review-page">
    <section class="review-hero"><div><span class="section-caption">REVIEW QUEUE</span><h1>待我审核</h1><p>只展示当前激活角色有权限审核的下属周报。</p></div><div class="review-count"><strong>{{ reports.length }}</strong><span>待处理</span></div></section>
    <p v-if="errorMessage" class="page-alert" role="alert">{{ errorMessage }}</p>
    <p v-if="successMessage" class="page-success" role="status">{{ successMessage }}</p>
    <section v-if="!canReview" class="page-alert">当前角色没有团队审核权限，请切换到经理、总裁或系统管理员角色。</section>
    <div v-else class="review-layout">
      <section class="dashboard-card queue-card">
        <div class="section-heading"><div><span class="section-caption">SUBMITTED</span><h2>审核队列</h2></div><button class="ghost-button" type="button" :disabled="isLoading" @click="loadReports">刷新</button></div>
        <div class="queue-list">
          <button v-for="report in reports" :key="report.id" type="button" class="queue-item" :class="{ 'is-active': selected?.report.id === report.id }" @click="selectReport(report)"><strong>{{ report.employee_name }}</strong><span>{{ report.period_start }} · {{ report.role_code }}</span><small>{{ report.summary || "暂无总结" }}</small></button>
          <p v-if="!reports.length && !isLoading" class="queue-empty">暂无待审核周报。</p>
          <p v-if="isLoading" class="queue-empty">正在加载…</p>
        </div>
      </section>
      <section v-if="selected" class="review-detail">
        <ReportHeader :report="selected.report" :role-name="template?.role_name" />
        <div class="dashboard-card review-actions"><div><span>审核状态</span><strong>待审核</strong></div><div><button class="danger-button" type="button" :disabled="isWorking" @click="review('return')">退回修改</button><button class="primary-button" type="button" :disabled="isWorking" @click="review('approve')">审核通过</button></div></div>
        <section class="dashboard-card review-card"><div class="section-heading"><div><span class="section-caption">SUMMARY</span><h2>本周总结</h2></div></div><p class="summary-text">{{ selected.report.summary || "暂无总结" }}</p></section>
        <section class="dashboard-card review-card"><div class="section-heading"><div><span class="section-caption">TASK PLAN</span><h2>工作任务</h2></div></div><TaskPlanTable :items="selected.items.map((item) => ({ ...item, task_code: item.task_code }))" :template-tasks="template?.tasks || []" readonly /></section>
        <section class="dashboard-card review-card"><div class="section-heading"><div><span class="section-caption">METRICS</span><h2>角色指标</h2></div></div><MetricSection :metrics="selected.metrics.map((metric) => ({ ...metric, metric_code: metric.metric_code }))" :template-metrics="template?.metrics || []" readonly /></section>
        <section class="dashboard-card review-card"><div class="section-heading"><div><span class="section-caption">RISK & ACTION</span><h2>风险与行动</h2></div></div><RiskPanel :model-value="selected.report" readonly /></section>
      </section>
    </div>
  </div>
</template>

<style scoped src="./ReviewView.css"></style>
