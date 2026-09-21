<script setup lang="ts">
import { CalendarRange, Crown, Sparkles } from "lucide-vue-next"

import heroDataColumns from "@/assets/dashboard/hero-data-columns.png"

defineProps<{
  period: { start: string; end: string }
  roleName: string
  userName: string
}>()

function formatPeriod(value: string) {
  return value ? value.replaceAll("-", ".") : "—"
}
</script>

<template>
  <header class="leader-home-header">
    <div class="leader-header-copy">
      <div class="leader-title-line">
        <span class="leader-title-mark" aria-hidden="true" />
        <div>
          <p class="leader-eyebrow">LEADERSHIP OPERATING PULSE</p>
          <h1>智能周报 · 领导首页</h1>
          <p class="leader-subtitle">总览经营执行 · 聚焦输出成果 · 统筹下周重点</p>
        </div>
      </div>
      <div class="leader-motto">
        <Sparkles :size="16" stroke-width="1.8" aria-hidden="true" />
        <span>让每一周都有新进展！</span>
      </div>
    </div>

    <img class="leader-header-art" :src="heroDataColumns" alt="" aria-hidden="true" />

    <div class="leader-header-period">
      <div class="leader-week-button">
        <CalendarRange :size="15" stroke-width="1.8" aria-hidden="true" />
        <span>本周</span>
        <strong>{{ formatPeriod(period.start) }} - {{ formatPeriod(period.end) }}</strong>
      </div>
      <p>把握进展 · 凝聚合力 · 共创更大价值</p>
      <div class="leader-period-owner">
        <Crown :size="13" stroke-width="1.8" aria-hidden="true" />
        <span>{{ userName || "领导视角" }} · {{ roleName }}</span>
      </div>
    </div>
  </header>
</template>

<style scoped src="./LeaderHomeHeader.css"></style>
