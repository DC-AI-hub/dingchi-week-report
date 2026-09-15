<script setup lang="ts">
import BackButton from "@/components/navigation/BackButton.vue"

import WeekRangePicker from "./WeekRangePicker.vue"

defineProps<{
  periodStart: string
  periodEnd: string
  monthKey: string
  isNew: boolean
  minPeriodStart: string
}>()
const emit = defineEmits<{
  "update:periodStart": [value: string]
}>()
</script>

<template>
  <section class="dashboard-card basics-card">
    <div class="basics-card__title"><BackButton :to="{ name: 'weekly-reports' }" /></div>
    <div class="basics-grid">
      <label class="period-field">周报周期<WeekRangePicker :start="periodStart" :end="periodEnd" :disabled="!isNew" :min="minPeriodStart" @update:start="emit('update:periodStart', $event)" /></label>
      <label>所属月度<input :value="monthKey" disabled /></label>
    </div>
  </section>
</template>

<style scoped src="./ReportBasics.css"></style>
