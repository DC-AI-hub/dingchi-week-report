<script setup lang="ts">
import { CalendarDays, Flag, MoveRight } from "lucide-vue-next"

import type { TeamPlanEntry } from "../types"

defineProps<{ plans: TeamPlanEntry[] }>()
</script>

<template>
  <section class="team-panel team-plans-panel">
    <div class="team-panel-heading">
      <div class="team-panel-title">
        <span class="team-panel-icon team-panel-icon--purple"><CalendarDays :size="16" stroke-width="2" /></span>
        <div><span>下一步计划</span><strong>团队行动排期</strong></div>
      </div>
      <span class="team-panel-note"><Flag :size="14" />基于当前周报</span>
    </div>
    <div v-if="plans.length" class="team-plan-board">
      <div v-for="(plan, index) in plans" :key="plan.id" class="team-plan-row">
        <span class="team-plan-index">{{ String(index + 1).padStart(2, "0") }}</span>
        <div class="team-plan-copy"><strong>{{ plan.title }}</strong><span>{{ plan.owner }} · {{ plan.detail }}</span></div>
        <div class="team-plan-dates"><span>{{ plan.start || "未设定" }}</span><MoveRight :size="14" /><span>{{ plan.end || "未设定" }}</span></div>
        <span class="team-plan-status">{{ plan.status }}</span>
      </div>
    </div>
    <div v-else class="team-panel-empty team-plans-empty">暂无团队排期数据</div>
  </section>
</template>

<style scoped src="./TeamPlansPanel.css"></style>
