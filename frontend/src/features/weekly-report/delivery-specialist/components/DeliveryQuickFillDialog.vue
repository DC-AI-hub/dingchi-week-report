<script setup lang="ts">
import { ref, watch } from "vue"
import BaseDialog from "@/components/overlay/BaseDialog.vue"
import DeliveryCustomerSelect from "@/features/weekly-report/components/DeliveryCustomerSelect.vue"
import { reportFormValidity } from "@/utils/form-validation"
import { deliveryTaskTemplates } from "../task-templates"

const props = defineProps<{ open: boolean; monthly?: boolean }>()
const emit = defineEmits<{ close: []; confirm: [customer: string, indexes: number[]] }>()
const customer = ref("")
const selected = ref<number[]>([])
const formElement = ref<HTMLFormElement | null>(null)
const taskInputs = ref<HTMLInputElement[]>([])
watch(() => props.open, (open) => {
  if (open) { customer.value = ""; selected.value = [] }
})
function clearTaskValidity() {
  taskInputs.value.forEach(input => input.setCustomValidity(""))
}
function toggleAll() {
  selected.value = selected.value.length === deliveryTaskTemplates.length ? [] : deliveryTaskTemplates.map((_, index) => index)
  clearTaskValidity()
}
function confirm() {
  clearTaskValidity()
  taskInputs.value[0]?.setCustomValidity(selected.value.length ? "" : "请至少选择一项工作任务。")
  if (!reportFormValidity(formElement.value)) return
  emit("confirm", customer.value, [...selected.value].sort((a, b) => a - b))
}
</script>

<template>
  <BaseDialog :open="open" title="快速填写任务" width="960px" height="90vh" @close="emit('close')">
    <form ref="formElement" id="delivery-quick-fill-form" class="quick-fill" novalidate @submit.prevent="confirm">
      <label>客户 <span class="required">*</span></label>
      <DeliveryCustomerSelect v-if="open" v-model="customer" required />
      <div class="selection-heading"><strong>选择工作任务（已选 {{ selected.length }} / {{ deliveryTaskTemplates.length }}）</strong><button class="link-button" type="button" @click="toggleAll">{{ selected.length === deliveryTaskTemplates.length ? '取消全选' : '全选' }}</button></div>
      <label v-for="(item, index) in deliveryTaskTemplates" :key="index" class="template-option" :class="{ selected: selected.includes(index) }">
        <input ref="taskInputs" v-model="selected" type="checkbox" :value="index" :aria-label="`选择任务 ${index + 1}`" @change="clearTaskValidity" />
        <span class="template-content">
          <span class="template-section task-section"><span class="section-label">工作任务</span><strong class="section-text">{{ item.task }}</strong></span>
          <span class="template-section work-section"><span class="section-label">主要工作内容<span v-if="monthly" class="reference-label">仅供参考</span></span><span class="section-text">{{ item.work }}</span></span>
        </span>
      </label>
    </form>
    <template #actions><button class="ghost-button" type="button" @click="emit('close')">取消</button><button class="primary-button" type="submit" form="delivery-quick-fill-form">确定</button></template>
  </BaseDialog>
</template>

<style scoped src="./DeliveryQuickFillDialog.css"></style>
