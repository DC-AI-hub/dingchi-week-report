<script setup lang="ts">
import { computed, onMounted } from "vue"
import { RouterLink, useRoute, useRouter } from "vue-router"
import NoticeBridge from "@/components/feedback/NoticeBridge.vue"
import UnsavedChangesGuard from "@/components/navigation/UnsavedChangesGuard.vue"
import MonthlyPlanTaskPanel from "@/features/monthly-plan/components/MonthlyPlanTaskPanel.vue"
import { useMonthlyPlanEditor } from "@/features/monthly-plan/useMonthlyPlanEditor"
import { useAuthStore } from "@/features/auth/store"
import MonthlyPlanBasics from "./components/MonthlyPlanBasics.vue"
import ApprovalTimeline from "./components/ApprovalTimeline.vue"

const route=useRoute(),router=useRouter()
const id=computed(()=>String(route.params.changeId || route.params.planId || ""))
const isChange=computed(()=>Boolean(route.params.changeId))
const editor=useMonthlyPlanEditor()
const auth=useAuthStore()
async function save(submit:boolean) {
  const result=await editor.save(submit)
  if(result)await router.push({name:isChange.value?(submit?'monthly-plan-change-detail':'monthly-plan-change-edit'):(submit?'monthly-plan-detail':'monthly-plan-edit'),params:isChange.value?{changeId:result}:{planId:result},query:{tab:route.query.tab}})
}
onMounted(()=>void editor.load(id.value,isChange.value))
</script>
<template>
  <div class="monthly-editor">
    <Teleport defer to="#weekly-report-header-actions">
      <div v-if="!editor.loading.value && editor.canEdit.value" class="monthly-editor-actions">
        <button class="ghost-button" type="button" :disabled="editor.busy.value" @click="save(false)">保存草稿</button>
        <button class="primary-button" type="button" :disabled="editor.busy.value" @click="save(true)">提交审批</button>
      </div>
    </Teleport>
    <UnsavedChangesGuard :dirty="editor.unsavedChanges.hasChanges.value" :enabled="!editor.loading.value" :reset-key="editor.unsavedChanges.resetKey.value" />
    <div v-if="editor.loading.value" class="dashboard-card loading">正在加载月度计划…</div>
    <template v-else>
      <NoticeBridge :warning-message="editor.error.value" />
      <section v-if="!editor.canEdit.value" class="dashboard-card loading" role="alert">{{editor.context.value?.warning || '当前计划不可编辑，请查看详情和审批状态。'}} <RouterLink :to="{name:'monthly-plans',query:{tab:route.query.tab}}">返回月度计划</RouterLink></section>
      <div v-else class="editor-body">
        <div class="editor-form">
        <MonthlyPlanBasics v-model:month="editor.input.month_key" v-model:summary="editor.input.summary" :existing="Boolean(editor.detail.value)" :busy="editor.busy.value" :template-code="editor.templateCode.value" />
        <MonthlyPlanTaskPanel v-model:tasks="editor.input.tasks" :month-key="editor.input.month_key" :template-code="editor.templateCode.value" :disabled="editor.busy.value" />
        </div>
        <ApprovalTimeline class="editor-approval" :managers="editor.context.value?.managers || []" :plan="editor.flowPlan.value" :record="editor.detail.value?.approvals[0]" :applicant="auth.user?.display_name" />
      </div>
    </template>
  </div>
</template>
<style scoped src="./EditView.css"></style>
