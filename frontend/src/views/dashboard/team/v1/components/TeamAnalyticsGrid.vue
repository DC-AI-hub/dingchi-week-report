<script setup lang="ts">
import { Activity, BarChart3, PieChart, UsersRound } from "lucide-vue-next"

import type { DashboardDistribution, DashboardTrendPoint } from "@/features/dashboard/types"

import TeamStatusChart from "./TeamStatusChart.vue"
import TeamTrendChart from "./TeamTrendChart.vue"
import type { TeamMemberSummary } from "../types"

defineProps<{
  trend: DashboardTrendPoint[]
  statusDistribution: DashboardDistribution[]
  taskTotal: number
  members: TeamMemberSummary[]
}>()
</script>

<template>
  <section class="team-analytics-grid">
    <article class="team-panel team-trend-panel">
      <div class="team-panel-heading">
        <div class="team-panel-title">
          <span class="team-panel-icon team-panel-icon--blue"><BarChart3 :size="16" stroke-width="2" /></span>
          <div><span>团队趋势</span><strong>本周完成进展</strong></div>
        </div>
        <span class="team-panel-note"><Activity :size="14" />进展 / 完成率</span>
      </div>
      <TeamTrendChart :points="trend" />
    </article>

    <article class="team-panel team-member-panel">
      <div class="team-panel-heading">
        <div class="team-panel-title">
          <span class="team-panel-icon team-panel-icon--purple"><UsersRound :size="16" stroke-width="2" /></span>
          <div><span>成员进展</span><strong>已提交成员完成情况</strong></div>
        </div>
      </div>
      <div v-if="members.length" class="member-progress-list">
        <div v-for="member in members.slice(0, 5)" :key="member.employeeId" class="member-progress-item">
          <div class="member-progress-name">
            <span class="member-avatar">{{ member.employeeName.slice(0, 1) }}</span>
            <div><strong>{{ member.employeeName }}</strong><small>{{ member.roleName }}</small></div>
            <b>{{ Math.round(member.completionRate) }}%</b>
          </div>
          <div class="member-progress-track"><i :style="{ width: `${Math.min(100, Math.max(0, member.completionRate))}%` }" /></div>
        </div>
      </div>
      <div v-else class="team-panel-empty">暂无已提交的团队周报</div>
    </article>

    <article class="team-panel team-status-panel">
      <div class="team-panel-heading">
        <div class="team-panel-title">
          <span class="team-panel-icon team-panel-icon--green"><PieChart :size="16" stroke-width="2" /></span>
          <div><span>任务状态</span><strong>状态分布</strong></div>
        </div>
      </div>
      <div class="status-panel-body">
        <TeamStatusChart :data="statusDistribution" :total="taskTotal" />
        <div class="status-legend">
          <div v-for="item in statusDistribution" :key="item.name" class="status-legend-item">
            <i :style="{ background: item.color }" /><span>{{ item.name }}</span><strong>{{ item.value }}</strong>
          </div>
          <span v-if="!statusDistribution.length" class="team-panel-empty">暂无状态数据</span>
        </div>
      </div>
    </article>
  </section>
</template>

<style scoped src="./TeamAnalyticsGrid.css"></style>
