<script setup lang="ts">
import { onMounted, ref } from "vue"

import BackButton from "@/components/navigation/BackButton.vue"
import { getMonthlyPlan, saveMonthlyPlan } from "@/features/weekly-report/api"

function currentMonth() {
  const date = new Date()
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`
}

const monthKey = ref(currentMonth())
const summary = ref("")
const isLoading = ref(true)
const isSaving = ref(false)
const errorMessage = ref("")

async function load() {
  isLoading.value = true
  errorMessage.value = ""
  try {
    summary.value = (await getMonthlyPlan(monthKey.value))?.summary || ""
  } catch {
    // 月度计划尚未建表或尚未填写时按空白计划打开，保存时再提示真实错误。
    summary.value = ""
  } finally {
    isLoading.value = false
  }
}

async function save() {
  isSaving.value = true
  errorMessage.value = ""
  try {
    await saveMonthlyPlan(monthKey.value, summary.value)
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "保存失败。"
  } finally {
    isSaving.value = false
  }
}

function changeMonth() {
  void load()
}

onMounted(() => void load())
</script>

<template>
  <div class="monthly-plan-page">
    <section class="dashboard-card monthly-plan-card">
      <div class="monthly-plan-card__header"><BackButton :to="{ name: 'weekly-reports' }" /></div>
      <label>月度<input v-model="monthKey" type="month" @change="changeMonth" /></label>
      <textarea v-model.trim="summary" :disabled="isLoading" rows="16" />
      <p v-if="errorMessage" class="page-alert" role="alert">{{ errorMessage }}</p>
      <div class="monthly-plan-actions"><button class="primary-button" type="button" :disabled="isLoading || isSaving" @click="save">{{ isSaving ? "保存中" : "保存" }}</button></div>
    </section>
  </div>
</template>

<style scoped>
.monthly-plan-page { display: grid; padding-bottom: 32px; }
.monthly-plan-card { padding: 28px; }
.monthly-plan-card__header { display: flex; align-items: center; gap: 18px; margin-bottom: 26px; }
.monthly-plan-card > label { display: grid; gap: 9px; max-width: 260px; color: #173764; font-weight: 700; }
.monthly-plan-card input,
.monthly-plan-card textarea { box-sizing: border-box; width: 100%; border: 1px solid #cfe0f5; border-radius: 12px; background: #f7faff; color: #153562; padding: 12px 14px; font: inherit; }
.monthly-plan-card textarea { margin-top: 18px; min-height: 320px; resize: vertical; }
.monthly-plan-actions { display: flex; justify-content: flex-end; margin-top: 18px; }
</style>
