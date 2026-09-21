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

<style scoped>
.week-range-picker { position: relative; display: flex; align-items: center; min-height: 46px; box-sizing: border-box; padding: 0 13px; border: 1px solid #cfe0f5; border-radius: 12px; background: #f7faff; color: #153562; }
.week-range-picker__trigger { width: 100%; min-height: 44px; border: 0; padding: 0; color: inherit; background: transparent; font: inherit; text-align: left; cursor: pointer; }
.week-range-picker__trigger:focus-visible { outline: 0; }
.week-range-picker__trigger:disabled { color: inherit; cursor: default; }
.week-range-picker__trigger output { display: block; overflow: hidden; width: 100%; white-space: nowrap; text-overflow: ellipsis; }
.week-range-picker__input { position: absolute; inset: 0; z-index: -1; width: 100%; height: 100%; border: 0; opacity: 0; pointer-events: none; }
.week-range-picker:focus-within { border-color: #2778e8; outline: 3px solid rgba(39, 120, 232, .13); }
.week-range-picker.is-disabled { opacity: .82; }
</style>
