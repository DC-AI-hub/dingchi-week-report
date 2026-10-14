<script setup lang="ts">
import UnsavedChangesGuard from "@/components/navigation/UnsavedChangesGuard.vue"
import NoticeBridge from "@/components/feedback/NoticeBridge.vue"
import { computed, onMounted, ref } from "vue"
import { useRoute, useRouter } from "vue-router"

import { useDeliveryReportForm } from "@/features/weekly-report/delivery-specialist/useDeliveryReportForm"
import MonthlyGoalDisplay from "@/features/monthly-plan/components/MonthlyGoalDisplay.vue"
import WeeklyPlanGate from "@/features/monthly-plan/components/WeeklyPlanGate.vue"
import DailyTaskSection from "@/views/weekly-report/components/DailyTaskSection.vue"
import ReportSaveButton from "@/views/weekly-report/components/ReportSaveButton.vue"
import MonthlyPlanTaskPanel from "@/features/monthly-plan/components/MonthlyPlanTaskPanel.vue"

import ReportBasics from "./components/ReportBasics.vue"
import TaskCollectionSection from "./components/TaskCollectionSection.vue"

const route = useRoute()
const router = useRouter()
const reportId = computed(() => String(route.params.reportId || ""))
const form = useDeliveryReportForm(() => reportId.value)
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
  if (id) await router.push({ name: "weekly-report-detail", params: { reportId: id }, query: route.query })
}

onMounted(() => void form.load())
</script>

<template>
  <div class="delivery-report-page">
    <UnsavedChangesGuard :dirty="form.unsavedChanges.hasChanges.value" :enabled="!form.isLoading.value" :reset-key="form.unsavedChanges.resetKey.value" />
    <div v-if="form.isLoading.value" class="dashboard-card loading-card">正在加载周报</div>
    <template v-else>
      <ReportSaveButton :busy="form.isSaving.value" :disabled="!form.monthlyTasksState.approved.value || form.monthlyTasksState.isLoading.value" @save="save" />
      <ReportBasics
        :period-start="form.report.period_start"
        :period-end="form.report.period_end"
        :month-key="form.monthKey.value"
        :is-new="form.isNew.value"
        :min-period-start="currentPeriodStart"
        @update:period-start="form.setPeriodStart"
      />
      <NoticeBridge :warning-message="form.errorMessage.value" />

      <WeeklyPlanGate v-if="!form.monthlyTasksState.approved.value"
        :month="form.monthKey.value" :loading="form.monthlyTasksState.isLoading.value"
        :message="form.monthlyTasksState.errorMessage.value || form.monthlyTasksState.gateMessage.value"
        @retry="form.monthlyTasksState.load(form.monthKey.value)" />
      <template v-else>
      <MonthlyGoalDisplay :month="form.monthKey.value" :summary="form.monthlyTasksState.summary.value" />
      <MonthlyPlanTaskPanel
        template-code="delivery_specialist_v1"
        :tasks="form.monthlyTasksState.tasks.value"
        readonly
        :month-key="form.monthKey.value"
        :disabled="form.isSaving.value"
        :is-loading="form.monthlyTasksState.isLoading.value"
        :error-message="form.monthlyTasksState.errorMessage.value"
        @retry="form.monthlyTasksState.load(form.monthKey.value)"
      />
      <TaskCollectionSection :default-owner-id="form.authStore.user?.id || ''"
        v-model:tasks="form.weeklyTasks.value"
        title="本周工作任务"
        :owner-name="form.authStore.user?.display_name || ''"
        mode="weekly"
        column-preference-key="delivery_specialist_v1"
        :field-definitions="form.taskFields.value"
        :report-id="reportId"
      />
      <section class="dashboard-card weekly-summary">
        <label>本周总结<textarea v-model.trim="form.report.summary" rows="4" /></label>
      </section>
      <DailyTaskSection
        :report="form.report"
        v-model:daily-tasks="form.dailyTasks.value"
        :defer-save="form.isNew.value"
        can-edit
      />
      </template>
    </template>
  </div>
</template>

<style scoped src="./EditView.css"></style>
