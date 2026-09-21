<script setup lang="ts">
import { ArrowUpRight, ClipboardCheck, CircleCheck, Clock3 } from "lucide-vue-next"

import type { TeamReportEntry } from "../types"

defineProps<{
  reports: TeamReportEntry[]
  myReport: TeamReportEntry | null
}>()

function statusText(value: string) {
  if (value.includes("待激活") || value === "pending") return "待激活"
  if (value.includes("激活") || value === "active") return "已提交"
  if (value.includes("归档") || value === "archived") return "已归档"
  if (value.includes("完成")) return "已完成"
  if (value.includes("延期") || value.includes("风险")) return "延期 / 风险"
  return "进行中"
}

function statusClass(value: string) {
  const text = statusText(value)
  return text === "已完成" ? "done" : text === "延期 / 风险" ? "risk" : "progress"
}
</script>

<template>
  <section class="team-report-grid">
    <article class="team-panel team-own-report-panel">
      <div class="team-panel-heading">
        <div class="team-panel-title">
          <span class="team-panel-icon team-panel-icon--blue"><ClipboardCheck :size="16" stroke-width="2" /></span>
          <div><span>我的周报</span><strong>本周提交情况</strong></div>
        </div>
        <span v-if="myReport" class="report-status" :class="`report-status--${statusClass(myReport.status)}`">{{ statusText(myReport.status) }}</span>
      </div>
      <div v-if="myReport" class="own-report-body">
        <div class="own-report-rate"><strong>{{ Math.round(myReport.completionRate) }}%</strong><span>个人完成率</span></div>
        <div class="own-report-copy"><strong>{{ myReport.summary || "本周暂无总结" }}</strong><span>{{ myReport.roleName }} · {{ myReport.groupName || "未分组" }}</span></div>
        <ArrowUpRight :size="18" class="report-arrow" aria-hidden="true" />
      </div>
      <div v-else class="team-panel-empty own-report-empty"><Clock3 :size="18" />本周尚未提交周报</div>
    </article>

    <article class="team-panel team-submission-panel">
      <div class="team-panel-heading">
        <div class="team-panel-title">
          <span class="team-panel-icon team-panel-icon--green"><CircleCheck :size="16" stroke-width="2" /></span>
          <div><span>团队周报</span><strong>成员提交情况</strong></div>
        </div>
        <span class="team-panel-note">已提交 {{ reports.length }} 人</span>
      </div>
      <div v-if="reports.length" class="submission-list">
        <div v-for="report in reports.slice(0, 6)" :key="report.id" class="submission-item">
          <span class="submission-avatar">{{ report.employeeName.slice(0, 1) }}</span>
          <div><strong>{{ report.employeeName }}</strong><small>{{ report.roleName }} · {{ report.groupName || "未分组" }}</small></div>
          <span class="report-status" :class="`report-status--${statusClass(report.status)}`">{{ statusText(report.status) }}</span>
        </div>
      </div>
      <div v-else class="team-panel-empty">暂无团队周报</div>
    </article>

    <article class="team-panel team-focus-panel">
      <div class="team-panel-heading">
        <div class="team-panel-title">
          <span class="team-panel-icon team-panel-icon--orange"><ArrowUpRight :size="16" stroke-width="2" /></span>
          <div><span>重点行动</span><strong>团队成果与风险</strong></div>
        </div>
      </div>
      <div v-if="reports.length" class="focus-list">
        <div v-for="report in reports.slice(0, 4)" :key="`focus-${report.id}`" class="focus-item">
          <div class="focus-item-main"><strong>{{ report.employeeName }}</strong><span>{{ report.summary || "暂无周报摘要" }}</span></div>
          <b :class="`focus-rate focus-rate--${statusClass(report.status)}`">{{ Math.round(report.completionRate) }}%</b>
        </div>
      </div>
      <div v-else class="team-panel-empty">暂无重点行动</div>
    </article>
  </section>
</template>

<style scoped src="./TeamReportsPanel.css"></style>
