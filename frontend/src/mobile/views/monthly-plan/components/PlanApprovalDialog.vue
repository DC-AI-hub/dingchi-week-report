<script setup lang="ts">
import { ref, watch } from "vue"
import BaseDialog from "@/mobile/components/overlay/BaseDialog.vue"
import { clearFieldValidity, reportFormValidity } from "@/utils/form-validation"
const props=defineProps<{open:boolean;reject:boolean;busy:boolean}>()
defineEmits<{close:[];confirm:[reason:string]}>()
const reason=ref(''),form=ref<HTMLFormElement|null>(null)
watch(()=>props.open,()=>{reason.value=''})
</script>
<template>
  <BaseDialog :open="open" :busy="busy" :title="reject?'驳回月度计划':'通过月度计划'" width="560px" @close="$emit('close')">
    <form id="monthly-plan-approval-form" ref="form" novalidate @input.capture="clearFieldValidity" @submit.prevent="reportFormValidity(form) && $emit('confirm',reason)">
      <label>{{reject?'驳回原因（必填）':'审批意见（可选）'}}<textarea v-model="reason" :required="reject" maxlength="2000" rows="5" :disabled="busy" /></label>
    </form>
    <template #actions><button class="ghost-button" type="button" :disabled="busy" @click="$emit('close')">取消</button><button class="ghost-button" type="submit" form="monthly-plan-approval-form" :disabled="busy">确定</button></template>
  </BaseDialog>
</template>
<style scoped src="./PlanApprovalDialog.css"></style>
