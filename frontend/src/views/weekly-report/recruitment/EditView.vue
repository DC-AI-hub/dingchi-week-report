<script setup lang="ts">
import NoticeBridge from "@/components/feedback/NoticeBridge.vue"
import { computed, onMounted, ref } from "vue"
import { useRoute, useRouter } from "vue-router"

import { useRecruitmentReportForm } from "@/features/weekly-report/recruitment/useRecruitmentReportForm"
import { recruitmentMonthlyPlanSample, recruitmentMonthlyPlanSampleFields } from "@/features/weekly-report/recruitment/samples"
import MonthlyPlanSection from "@/views/weekly-report/components/MonthlyPlanSection.vue"
import DailyTaskSection from "@/views/weekly-report/components/DailyTaskSection.vue"

import ReportBasics from "./components/ReportBasics.vue"
import TaskCollectionSection from "./components/TaskCollectionSection.vue"

const route = useRoute()
const router = useRouter()
const reportId = computed(() => String(route.params.reportId || ""))
const form = useRecruitmentReportForm(() => reportId.value)
const monthlyPlanDialogOpen = ref(false)
const currentPeriodStart = (() => {
  const date = new Date()
  date.setDate(date.getDate() - (date.getDay() || 7) + 1)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`
})()

async function save() {
  const id = await form.save()
  if (id) await router.push({ name: "weekly-report-detail", params: { reportId: id } })
}

async function saveMonthlyPlan(summary: string) {
  if (await form.saveMonthlyPlanSummary(summary)) monthlyPlanDialogOpen.value = false
}

onMounted(() => void form.load())
</script>

<template>
  <div class="recruitment-report-page">
    <div v-if="form.isLoading.value" class="dashboard-card loading-card">正在加载周报</div>
    <template v-else>
      <ReportBasics :period-start="form.report.period_start" :period-end="form.report.period_end" :month-key="form.monthKey.value" :is-new="form.isNew.value" :min-period-start="currentPeriodStart" @update:period-start="form.setPeriodStart" />
      <NoticeBridge :warning-message="form.errorMessage.value" />
      <MonthlyPlanSection :editor-open="monthlyPlanDialogOpen" :month-key="form.monthKey.value" :summary="form.monthlySummary.value" :locked="form.monthlyPlanLocked.value" :sample-content="recruitmentMonthlyPlanSample" :sample-fields="recruitmentMonthlyPlanSampleFields" :busy="form.isMonthlyPlanSaving.value" :error-message="form.monthlyPlanErrorMessage.value" @open="monthlyPlanDialogOpen = true" @close="monthlyPlanDialogOpen = false" @save="saveMonthlyPlan" />
      <TaskCollectionSection v-model:tasks="form.weeklyTasks.value" title="本周工作任务" :owner-name="form.authStore.user?.display_name || ''" :field-definitions="form.taskFields.value" />
      <section class="dashboard-card weekly-summary"><label>本周总结<textarea v-model.trim="form.report.summary" rows="4" /></label></section>
      <DailyTaskSection
        :report="form.report"
        v-model:daily-tasks="form.dailyTasks.value"
        :defer-save="form.isNew.value"
        can-edit
      />
      <footer class="form-actions"><button class="primary-button" type="button" :disabled="form.isSaving.value" @click="save">{{ form.isSaving.value ? "保存中" : "保存周报" }}</button></footer>
    </template>
  </div>
</template>

<style scoped src="./EditView.css"></style>
