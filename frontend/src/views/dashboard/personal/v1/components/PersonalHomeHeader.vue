<script setup lang="ts">
import { CalendarRange, Sparkles } from "lucide-vue-next"

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
  <header class="personal-home-header">
    <div class="header-copy">
      <div class="header-title-line">
        <span class="title-mark" aria-hidden="true" />
        <div>
          <p class="header-eyebrow">PERSONAL OPERATING PULSE</p>
          <h1>智能周报 · 个人首页</h1>
          <p class="header-subtitle">聚焦我的进展 · 沉淀工作成果 · 规划下周行动</p>
        </div>
      </div>
      <div class="header-motto">
        <Sparkles :size="17" stroke-width="1.8" aria-hidden="true" />
        <span>持续进步，遇见更好的自己！</span>
      </div>
    </div>

    <img class="header-art" :src="heroDataColumns" alt="" aria-hidden="true" />

    <div class="header-period">
      <div class="period-label">本周周期</div>
      <strong>{{ formatPeriod(period.start) }} - {{ formatPeriod(period.end) }}</strong>
      <div class="period-owner">
        <CalendarRange :size="15" stroke-width="1.8" aria-hidden="true" />
        <span>{{ userName || "个人用户" }} · {{ roleName }}</span>
      </div>
    </div>
  </header>
</template>

<style scoped src="./PersonalHomeHeader.css"></style>
