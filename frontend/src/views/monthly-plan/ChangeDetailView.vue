<script setup lang="ts">
import { computed,onMounted,ref } from "vue"
import { RouterLink,useRoute,useRouter } from "vue-router"
import { useAuthStore } from "@/features/auth/store"
import NoticeBridge from "@/components/feedback/NoticeBridge.vue"
import PlanComparison from "@/features/monthly-plan/components/PlanComparison.vue"
import { getPlanChange,createPlanChange } from "@/features/monthly-plan/api"
import { type ChangeDetail } from "@/features/monthly-plan/types"
import PlanDetailHeading from "./components/PlanDetailHeading.vue"
import ApprovalTimeline from "./components/ApprovalTimeline.vue"
const auth=useAuthStore(),router=useRouter(),busy=ref(false)
const canChange=computed(()=>detail.value?.plan.can_create_change && detail.value.plan.employee_id===auth.user?.id && auth.roles.some(role=>role.role_code===detail.value?.plan.role_code))
async function beginChange(){if(!detail.value)return;busy.value=true;try{const data=await createPlanChange(detail.value.plan.id);await router.push({name:"monthly-plan-change-edit",params:{changeId:data.change.id},query:{tab:route.query.tab}})}catch(cause){error.value=cause instanceof Error?cause.message:"申请变更失败。"}finally{busy.value=false}}
const route=useRoute(),detail=ref<ChangeDetail|null>(null),error=ref('')
const flow=computed(()=>detail.value?{...detail.value.plan,...detail.value.change}:null)
onMounted(async()=>{try{detail.value=await getPlanChange(String(route.params.changeId))}catch(cause){error.value=cause instanceof Error?cause.message:'变更申请加载失败。'}})
</script>
<template><div class="monthly-detail"><Teleport defer to="#weekly-report-header-actions"><div v-if="detail" class="detail-actions"><RouterLink v-if="detail.can_edit" class="ghost-button" :to="{name:'monthly-plan-change-edit',params:{changeId:detail.change.id}}">编辑</RouterLink><button v-if="canChange" class="ghost-button" :disabled="busy" @click="beginChange">申请变更</button></div></Teleport><NoticeBridge :warning-message="error" />
<div v-if="detail" class="detail-body"><div class="detail-content">
<PlanDetailHeading :plan="detail.plan" change :status="detail.change.status" :updated-at="detail.change.updated_at" :rejection-reason="detail.change.rejection_reason" />
<PlanComparison :before="detail.base_snapshot" :after="detail.snapshot" />
</div><ApprovalTimeline v-if="flow" class="detail-flow" :plan="flow" :record="detail.approvals[0]" /></div>
</div></template>
<style scoped src="./DetailView.css"></style>
