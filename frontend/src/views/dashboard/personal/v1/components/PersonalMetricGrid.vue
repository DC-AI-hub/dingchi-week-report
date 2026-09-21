<script setup lang="ts">
import { CheckCircle2, ClipboardList, CalendarDays, Target } from "lucide-vue-next"
import type { Component } from "vue"

defineProps<{
  plannedTasks: number
  completionRate: number
  completedTasks: number
  planCount: number
}>()

const cards: Array<{
  label: string
  hint: string
  tone: "blue" | "purple" | "green" | "cyan"
  icon: Component
  key: "plannedTasks" | "completionRate" | "completedTasks" | "planCount"
  suffix?: string
}> = [
  { label: "本周条目", hint: "计划任务总数", tone: "blue", icon: ClipboardList, key: "plannedTasks" },
  { label: "个人完成率", hint: "进度与质量综合", tone: "purple", icon: Target, key: "completionRate", suffix: "%" },
  { label: "已完成任务", hint: "按时完成", tone: "green", icon: CheckCircle2, key: "completedTasks" },
  { label: "下周计划", hint: "提前安排下一步", tone: "cyan", icon: CalendarDays, key: "planCount" },
]
</script>

<template>
  <section class="personal-metric-grid" aria-label="本周指标">
    <article v-for="card in cards" :key="card.label" class="personal-metric-card" :class="`personal-metric-card--${card.tone}`">
      <span class="metric-icon" aria-hidden="true">
        <component :is="card.icon" :size="28" stroke-width="1.7" />
      </span>
      <div class="metric-copy">
        <h2>{{ card.label }}</h2>
        <strong>{{ Math.round($props[card.key]) }}{{ card.suffix || "" }}</strong>
        <span>{{ card.hint }}</span>
      </div>
      <span class="metric-glow" aria-hidden="true" />
    </article>
  </section>
</template>

<style scoped src="./PersonalMetricGrid.css"></style>
