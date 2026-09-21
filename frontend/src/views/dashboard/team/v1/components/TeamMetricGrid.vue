<script setup lang="ts">
import type { Component } from "vue"

defineProps<{
  cards: Array<{
    label: string
    value: string | number
    hint: string
    tone: "blue" | "purple" | "green" | "orange" | "red"
    icon: Component
  }>
}>()
</script>

<template>
  <section class="team-metric-grid" aria-label="团队关键指标">
    <article v-for="card in cards" :key="card.label" class="team-metric-card" :class="`team-metric-card--${card.tone}`">
      <div class="metric-copy">
        <span class="metric-label">{{ card.label }}</span>
        <strong class="metric-value">{{ card.value }}</strong>
        <span class="metric-hint">{{ card.hint }}</span>
      </div>
      <span class="metric-icon" aria-hidden="true">
        <component :is="card.icon" :size="32" stroke-width="1.9" />
      </span>
    </article>
  </section>
</template>

<style scoped src="./TeamMetricGrid.css"></style>
