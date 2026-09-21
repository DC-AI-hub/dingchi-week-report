<script setup lang="ts">
import { ListChecks, ArrowUpRight } from "lucide-vue-next"
import { RouterLink } from "vue-router"

import type { DashboardItem } from "@/features/dashboard/types"

const props = defineProps<{
  plans: DashboardItem[]
  period: { start: string; end: string }
}>()

function dayColumn(dateValue: string | null) {
  if (!dateValue || !props.period.start) return 1
  const target = new Date(`${dateValue.slice(0, 10)}T00:00:00`)
  const start = new Date(`${props.period.start.slice(0, 10)}T00:00:00`)
  const day = Math.floor((target.getTime() - start.getTime()) / 86400000)
  return Math.min(5, Math.max(1, day + 1))
}

function dateLabel(value: string | null) {
  return value ? value.slice(0, 10) : "待安排"
}
</script>

<template>
  <article class="personal-content-panel personal-plans-panel">
    <div class="content-panel-heading">
      <div class="content-panel-title">
        <span class="content-panel-icon content-panel-icon--cyan" aria-hidden="true"><ListChecks :size="17" /></span>
        <div>
          <span class="content-kicker">下一步安排</span>
          <h2>我的下周计划</h2>
        </div>
      </div>
      <RouterLink class="panel-link" to="/weekly-reports">打开周报 <ArrowUpRight :size="14" aria-hidden="true" /></RouterLink>
    </div>

    <div v-if="!props.plans.length" class="content-empty">暂无下一步计划</div>
    <div v-else class="plan-board">
      <div class="plan-list">
        <div v-for="(plan, index) in props.plans" :key="plan.id" class="plan-item">
          <span class="plan-index">{{ String(index + 1).padStart(2, "0") }}</span>
          <div>
            <strong :title="plan.task_name_snapshot">{{ plan.task_name_snapshot }}</strong>
            <small>{{ dateLabel(plan.planned_completion_date) }} · {{ plan.progress_text || "待持续推进" }}</small>
          </div>
        </div>
      </div>
      <div class="plan-timeline" aria-label="计划排期">
        <div class="timeline-head"><span>周一</span><span>周二</span><span>周三</span><span>周四</span><span>周五</span></div>
        <div v-for="plan in props.plans" :key="`timeline-${plan.id}`" class="timeline-row">
          <span class="timeline-bar" :style="{ gridColumn: `${dayColumn(plan.planned_completion_date)} / span ${Math.max(1, 5 - dayColumn(plan.planned_completion_date) + 1)}` }" />
        </div>
      </div>
    </div>
  </article>
</template>

<style scoped src="./PersonalPlansPanel.css"></style>
