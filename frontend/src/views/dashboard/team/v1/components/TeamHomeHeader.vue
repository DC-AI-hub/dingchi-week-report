<script setup lang="ts">
import { CalendarRange, Sparkles, UsersRound } from "lucide-vue-next"

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
  <header class="team-home-header">
    <div class="header-copy">
      <div class="header-title-line">
        <span class="title-mark" aria-hidden="true" />
        <div>
          <p class="header-eyebrow">TEAM OPERATING PULSE</p>
          <h1>智能周报 · 团队首页</h1>
          <p class="header-subtitle">看见团队进展 · 聚焦协同成果 · 驱动下一步行动</p>
        </div>
      </div>
      <div class="header-motto">
        <Sparkles :size="16" stroke-width="1.8" aria-hidden="true" />
        <span>让每一周 · 更进一步！</span>
      </div>
    </div>

    <img class="header-art" :src="heroDataColumns" alt="" aria-hidden="true" />

    <div class="header-period">
      <div class="period-label">本周周期</div>
      <strong>{{ formatPeriod(period.start) }} - {{ formatPeriod(period.end) }}</strong>
      <div class="period-owner">
        <CalendarRange :size="14" stroke-width="1.8" aria-hidden="true" />
        <span>{{ userName || "团队成员" }} · {{ roleName }}</span>
      </div>
      <div class="period-scope">
        <UsersRound :size="13" stroke-width="1.8" aria-hidden="true" />
        <span>团队视角</span>
      </div>
    </div>
  </header>
</template>

<style scoped src="./TeamHomeHeader.css"></style>
