<script setup lang="ts">
import { computed, onMounted, ref } from "vue"
import { RouterLink, useRoute, useRouter } from "vue-router"
import { useAuthStore } from "@/features/auth/store"
import NoticeBridge from "@/components/feedback/NoticeBridge.vue"
import MonthlyPlanTaskPanel from "@/features/monthly-plan/components/MonthlyPlanTaskPanel.vue"
import { getManagedPlan, createPlanChange } from "@/features/monthly-plan/api"
import { type PlanDetail } from "@/features/monthly-plan/types"
import PlanDetailHeading from "./components/PlanDetailHeading.vue"
import PlanChangeHistory from "./components/PlanChangeHistory.vue"
import ApprovalTimeline from "./components/ApprovalTimeline.vue"
const auth=useAuthStore()
const editableChange=computed(()=>{const plan=detail.value?.plan;return plan && plan.employee_id===auth.user?.id && auth.roles.some(role=>role.role_code===plan.role_code) ? plan.children?.find(child=>["draft","rejected"].includes(child.status)) : undefined})
const router=useRouter(),busy=ref(false)
async function beginChange(){if(!detail.value)return;busy.value=true;try{const data=await createPlanChange(detail.value.plan.id);await router.push({name:'monthly-plan-change-edit',params:{changeId:data.change.id},query:{tab:route.query.tab}})}catch(cause){error.value=cause instanceof Error?cause.message:'申请变更失败。'}finally{busy.value=false}}
const route=useRoute(),detail=ref<PlanDetail|null>(null),error=ref('')
async function load(){try{detail.value=await getManagedPlan(String(route.params.planId))}catch(cause){error.value=cause instanceof Error?cause.message:'计划加载失败。'}}
onMounted(()=>void load())
</script>
<template>
  <div class="monthly-detail">
    <Teleport defer to="#weekly-report-header-actions"><template v-if="detail"><div class="detail-actions"><RouterLink v-if="detail.can_edit" class="ghost-button" :to="{name:'monthly-plan-edit',params:{planId:detail.plan.id},query:{tab:route.query.tab}}">编辑</RouterLink><RouterLink v-if="editableChange" class="ghost-button" :to="{name:'monthly-plan-change-edit',params:{changeId:editableChange.id},query:{tab:route.query.tab}}">编辑变更</RouterLink><button v-if="detail.can_create_change" class="ghost-button" :disabled="busy" @click="beginChange">申请变更</button></div></template></Teleport>
    <NoticeBridge :warning-message="error" />
    <template v-if="detail">
      <div class="detail-body"><div class="detail-content"><PlanDetailHeading :plan="detail.plan" :rejection-reason="detail.plan.rejection_reason" />
      <section class="dashboard-card detail-goal"><h2>月度目标</h2><p>{{detail.plan.summary}}</p></section>
      <MonthlyPlanTaskPanel :tasks="detail.tasks" :month-key="detail.plan.month_key" :template-code="detail.plan.template_code" readonly />
      <PlanChangeHistory :history="detail.history" /></div><ApprovalTimeline class="detail-flow" :plan="detail.plan" :record="detail.approvals[0]" /></div>
    </template><div v-else-if="!error" class="dashboard-card detail-goal">正在加载月度计划…</div>
  </div>
</template>
<style scoped src="./DetailView.css"></style>
