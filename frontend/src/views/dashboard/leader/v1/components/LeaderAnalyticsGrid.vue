<script setup lang="ts">
import { BarChart3, Building2, ListChecks, PieChart } from "lucide-vue-next"

import type { DashboardDistribution, DashboardTrendPoint } from "@/features/dashboard/types"

import LeaderGaugeChart from "./LeaderGaugeChart.vue"
import LeaderOutputChart from "./LeaderOutputChart.vue"
import LeaderTrendChart from "./LeaderTrendChart.vue"
import type { LeaderDepartment } from "../types"

const props = defineProps<{
  trend: DashboardTrendPoint[]
  departments: LeaderDepartment[]
  outputDistribution: DashboardDistribution[]
  outputTotal: number
  completionRate: number
}>()
</script>

<template>
  <section class="leader-analytics-grid">
    <article class="leader-panel leader-panel--trend">
      <div class="leader-panel-heading">
        <span class="leader-panel-icon leader-panel-icon--blue"><BarChart3 :size="16" /></span>
        <div><span class="leader-panel-kicker">执行走势</span><h2 class="leader-panel-title">总体执行趋势</h2></div>
      </div>
      <LeaderTrendChart :points="props.trend" />
    </article>

    <article class="leader-panel">
      <div class="leader-panel-heading">
        <span class="leader-panel-icon leader-panel-icon--purple"><Building2 :size="16" /></span>
        <div><span class="leader-panel-kicker">团队表现</span><h2 class="leader-panel-title">部门完成情况</h2></div>
      </div>
      <div v-if="!props.departments.length" class="leader-panel-empty">暂无部门数据</div>
      <div v-else class="department-list">
        <div v-for="department in props.departments" :key="department.name" class="department-row">
          <div class="department-row__meta"><span>{{ department.name }}</span><strong>{{ department.rate }}%</strong></div>
          <div class="department-track"><span :style="{ width: `${Math.min(100, Math.max(0, department.rate))}%` }" /></div>
          <small>{{ department.taskCount }} 项任务</small>
        </div>
      </div>
    </article>

    <article class="leader-panel leader-panel--output">
      <div class="leader-panel-heading">
        <span class="leader-panel-icon leader-panel-icon--green"><PieChart :size="16" /></span>
        <div><span class="leader-panel-kicker">成果沉淀</span><h2 class="leader-panel-title">输出成果构成</h2></div>
      </div>
      <div class="output-layout">
        <LeaderOutputChart :data="props.outputDistribution" :total="props.outputTotal" />
        <div v-if="props.outputDistribution.length" class="output-legend">
          <div v-for="item in props.outputDistribution" :key="item.name" class="output-legend__item">
            <span :style="{ backgroundColor: item.color }" />
            <span class="output-legend__name" :title="item.name">{{ item.name }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
        <div v-else class="leader-panel-empty">暂无成果数据</div>
      </div>
    </article>

    <article class="leader-panel leader-panel--completion">
      <div class="leader-panel-heading">
        <span class="leader-panel-icon leader-panel-icon--amber"><ListChecks :size="16" /></span>
        <div><span class="leader-panel-kicker">计划执行</span><h2 class="leader-panel-title">按计划完成情况</h2></div>
      </div>
      <LeaderGaugeChart :value="props.completionRate" />
      <p class="completion-note">按当前周报任务的计划完成情况计算</p>
    </article>
  </section>
</template>

<style scoped src="./LeaderAnalyticsGrid.css"></style>
