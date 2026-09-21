<script setup lang="ts">
import { computed, ref } from "vue"

const props = defineProps<{ start: string; end: string; min: string; disabled?: boolean }>()
const emit = defineEmits<{ "update:start": [value: string] }>()
const periodInput = ref<HTMLInputElement | null>(null)
const rangeText = computed(() => `${props.start} 至 ${props.end}`)

function openPicker() {
  if (props.disabled || !periodInput.value) return
  const input = periodInput.value as HTMLInputElement & { showPicker?: () => void }
  if (input.showPicker) input.showPicker()
  else { input.focus(); input.click() }
}

function monday(value: string) {
  const date = new Date(`${value}T00:00:00`)
  date.setDate(date.getDate() - (date.getDay() || 7) + 1)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`
}

function change(event: Event) {
  const value = (event.target as HTMLInputElement).value
  if (value) emit("update:start", monday(value))
}
</script>

<template>
  <div class="week-range-picker" :class="{ 'is-disabled': disabled }">
    <button class="week-range-picker__trigger" type="button" :disabled="disabled" aria-label="选择周报周期" @click="openPicker"><output>{{ rangeText }}</output></button>
    <input ref="periodInput" class="week-range-picker__input" :value="start" :disabled="disabled" :min="min" step="7" type="date" tabindex="-1" aria-hidden="true" @change="change" />
  </div>
</template>

<style scoped src="./WeekRangePicker.css"></style>
