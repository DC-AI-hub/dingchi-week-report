<script setup lang="ts">
import { computed, onMounted, ref } from "vue"
import { useRoute, useRouter } from "vue-router"

import { useDeliveryReportForm } from "@/features/weekly-report/delivery-specialist/useDeliveryReportForm"
import {
  deliveryMonthlyPlanSample,
  deliveryMonthlyPlanSampleFields,
} from "@/features/weekly-report/delivery-specialist/samples"
import ExamplePreviewButton from "@/components/feedback/ExamplePreviewButton.vue"

import ReportBasics from "./components/ReportBasics.vue"
import MonthlyPlanEditorDialog from "./components/MonthlyPlanEditorDialog.vue"
import TaskCollectionSection from "./components/TaskCollectionSection.vue"

const route = useRoute()
const router = useRouter()
const reportId = computed(() => String(route.params.reportId || ""))
const form = useDeliveryReportForm(() => reportId.value)
const monthlyPlanDialogOpen = ref(false)
const currentPeriodStart = (() => {
  const date = new Date()
  const day = date.getDay() || 7
  date.setDate(date.getDate() - day + 1)
  const month = String(date.getMonth() + 1).padStart(2, "0")
  const dayValue = String(date.getDate()).padStart(2, "0")
  return `${date.getFullYear()}-${month}-${dayValue}`
})()

async function save() {
  const id = await form.save()
  if (id) await router.push({ name: "weekly-report-detail", params: { reportId: id } })
}

function openMonthlyPlanDialog() {
  monthlyPlanDialogOpen.value = true
}

async function saveMonthlyPlan(summary: string) {
  if (await form.saveMonthlyPlanSummary(summary)) monthlyPlanDialogOpen.value = false
}

onMounted(() => void form.load())
</script>

<template>
  <div class="delivery-report-page">
    <div v-if="form.isLoading.value" class="dashboard-card loading-card">正在加载周报</div>
    <template v-else>
      <ReportBasics
        :period-start="form.report.period_start"
        :period-end="form.report.period_end"
        :month-key="form.monthKey.value"
        :is-new="form.isNew.value"
        :min-period-start="currentPeriodStart"
        @update:period-start="form.setPeriodStart"
      />
      <p v-if="form.errorMessage.value" class="page-alert" role="alert">{{ form.errorMessage.value }}</p>

      <section class="dashboard-card monthly-summary">
        <div class="monthly-summary__heading">
          <h2>月度计划</h2>
          <div class="monthly-summary__actions">
            <ExamplePreviewButton
              :content="deliveryMonthlyPlanSample"
              :fields="deliveryMonthlyPlanSampleFields"
              panel-title="月度计划填写样例"
            />
            <button class="ghost-button" type="button" @click="openMonthlyPlanDialog">编辑月度计划</button>
          </div>
        </div>
        <textarea :value="form.monthlySummary.value" rows="4" readonly />
      </section>
      <TaskCollectionSection
        v-model:tasks="form.weeklyTasks.value"
        title="本周工作任务"
        mode="weekly"
        :field-definitions="form.taskFields.value"
      />
      <section class="dashboard-card weekly-summary">
        <label>本周总结<textarea v-model.trim="form.report.summary" rows="4" /></label>
      </section>
      <footer class="form-actions"><button class="primary-button" type="button" :disabled="form.isSaving.value" @click="save">{{ form.isSaving.value ? "保存中" : "保存周报" }}</button></footer>
      <MonthlyPlanEditorDialog
        :open="monthlyPlanDialogOpen"
        :month-key="form.monthKey.value"
        :summary="form.monthlySummary.value"
        :busy="form.isMonthlyPlanSaving.value"
        :error-message="form.monthlyPlanErrorMessage.value"
        @close="monthlyPlanDialogOpen = false"
        @save="saveMonthlyPlan"
      />
    </template>
  </div>
</template>

<style scoped src="./EditView.css"></style>
