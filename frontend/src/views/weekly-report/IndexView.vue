<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue"
import { RouterLink } from "vue-router"

import { useAuthStore } from "@/features/auth/store"
import { listReports } from "@/features/weekly-report/api"
import type { WeeklyReport } from "@/features/weekly-report/types"

const authStore = useAuthStore()
const reports = ref<WeeklyReport[]>([])
const activeStatus = ref("")
const isLoading = ref(false)
const errorMessage = ref("")
const statusOptions = [
  { value: "", label: "全部状态" },
  { value: "draft", label: "草稿" },
  { value: "submitted", label: "待审核" },
  { value: "approved", label: "已通过" },
  { value: "returned", label: "已退回" },
]
const canReview = computed(() => ["team", "all"].includes(authStore.activeRole?.scope || ""))

const statusLabels: Record<string, string> = { draft: "草稿", submitted: "待审核", approved: "已通过", returned: "已退回" }

async function loadReports() {
  isLoading.value = true
  errorMessage.value = ""
  try {
    reports.value = (await listReports(activeStatus.value || undefined)).items
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "周报列表加载失败。"
  } finally {
    isLoading.value = false
  }
}

function statusLabel(status: string) { return statusLabels[status] || status }
function reportTitle(report: WeeklyReport) { return `${report.period_start || "未设置周期"} 周报` }

onMounted(() => void loadReports())
watch(activeStatus, () => void loadReports())
watch(() => authStore.activeRole?.role_code, () => void loadReports())
</script>

<template>
  <div class="reports-page">
    <section class="reports-hero">
      <div>
        <span class="section-caption">WEEKLY WORKSPACE</span>
        <h1>周报工作台</h1>
        <p>按当前角色填写、提交并回顾每周行动，管理者可查看团队周报。</p>
      </div>
      <div class="hero-actions">
        <RouterLink v-if="canReview" class="ghost-button" to="/weekly-reports/review">待我审核</RouterLink>
        <RouterLink class="primary-button" to="/weekly-reports/new">填写本周周报</RouterLink>
      </div>
    </section>

    <p v-if="errorMessage" class="page-alert" role="alert">{{ errorMessage }}</p>

    <section class="dashboard-card reports-card">
      <div class="section-heading section-heading--wide">
        <div><span class="section-caption">REPORTS</span><h2>{{ canReview ? "可见周报" : "我的周报" }}</h2></div>
        <div class="filter-row">
          <label for="report-status">状态</label>
          <select id="report-status" v-model="activeStatus"><option v-for="option in statusOptions" :key="option.value" :value="option.value">{{ option.label }}</option></select>
          <button class="ghost-button" type="button" :disabled="isLoading" @click="loadReports">{{ isLoading ? "加载中" : "刷新" }}</button>
        </div>
      </div>
      <div class="reports-table-wrap">
        <table class="reports-table">
          <thead><tr><th>周期</th><th>填写人</th><th>角色</th><th>分组</th><th>状态</th><th>提交时间</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="report in reports" :key="report.id">
              <td><strong>{{ reportTitle(report) }}</strong><small>{{ report.period_end || "—" }}</small></td>
              <td>{{ report.employee_name || "本人" }}</td>
              <td>{{ report.role_code }}</td>
              <td>{{ report.group_name || "—" }}</td>
              <td><span :class="`status-pill status-pill--${report.status}`">{{ statusLabel(report.status) }}</span></td>
              <td>{{ report.submitted_at || "未提交" }}</td>
              <td class="action-cell"><RouterLink :to="`/weekly-reports/${report.id}`">查看</RouterLink><RouterLink v-if="['draft', 'returned'].includes(report.status)" :to="`/weekly-reports/${report.id}/edit`">编辑</RouterLink></td>
            </tr>
            <tr v-if="!reports.length && !isLoading"><td colspan="7" class="empty-row">暂无符合条件的周报，点击右上角开始填写。</td></tr>
            <tr v-if="isLoading"><td colspan="7" class="empty-row">正在加载周报数据…</td></tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="report-tip"><strong>填写提示</strong><span>每个任务请记录输出成果、进度和质量；延期任务必须补充原因、下一步行动和预计完成日期。</span></section>
  </div>
</template>

<style scoped src="./IndexView.css"></style>
