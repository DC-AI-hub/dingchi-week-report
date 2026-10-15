<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue"

import DeliveryCustomerSelect from "@/features/weekly-report/components/DeliveryCustomerSelect.vue"
import { monthlyPlanScopeLabel, usesConfiguredCustomers } from "@/features/weekly-report/monthly-plan/template-fields"
import { clearFieldValidity, reportFormValidity } from "@/utils/form-validation"
import BaseDialog from "@/components/overlay/BaseDialog.vue"
import type { MonthlyPlanTask, MonthlyPlanTaskPayload } from "@/features/weekly-report/monthly-plan/types"
import TaskTemplatePopover from "@/features/weekly-report/delivery-specialist/components/TaskTemplatePopover.vue"
import { deliveryTaskTemplates } from "@/features/weekly-report/delivery-specialist/task-templates"

const props = defineProps<{ open: boolean; task: MonthlyPlanTask | null; readonly?: boolean; templateCode?: string }>()
const emit = defineEmits<{ close: []; save: [task: MonthlyPlanTaskPayload, action: "close" | "next"] }>()
const customerSelect = ref<InstanceType<typeof DeliveryCustomerSelect> | null>(null)
const scopeLabel = computed(() => monthlyPlanScopeLabel(props.templateCode || ""))
const configuredCustomers = computed(() => usesConfiguredCustomers(props.templateCode || ""))
const customerName = ref("")
const workTask = ref("")
const input = ref<HTMLTextAreaElement | null>(null)
const formElement = ref<HTMLFormElement | null>(null)
const pickerOpen = ref(false)
const pickerTrigger = ref<HTMLButtonElement | null>(null)
const anchor = ref<HTMLElement | null>(null)
const selectedTemplate = ref("")
function togglePicker() {
  anchor.value = formElement.value?.closest<HTMLElement>('[role="dialog"]') || null
  pickerOpen.value = !pickerOpen.value
}
async function fillTemplate(index: number) {
  const template = deliveryTaskTemplates[index]
  if (!template) return
  workTask.value = template.task
  selectedTemplate.value = String(index)
  pickerOpen.value = false
  await nextTick()
  input.value?.dispatchEvent(new Event("input", { bubbles: true }))
  input.value?.focus()
}

watch(() => [props.open, props.task] as const, () => {
  pickerOpen.value = false
  selectedTemplate.value = ""
  if (!props.open) return
  customerName.value = props.task?.scope_name || ""
  workTask.value = props.task?.work_task || ""
  if (!props.readonly) void nextTick(() => input.value?.focus())
}, { immediate: true })

function save(action: "close" | "next") {
  if (!reportFormValidity(formElement.value)) return
  const value = workTask.value.trim()
  emit("save", {
    scope_name: scopeLabel.value ? customerName.value.trim() : "",
    work_task: value,
  }, action)
  if (action === "next") {
    workTask.value = ""
    void nextTick(() => input.value?.focus())
  }
}
</script>

<template>
  <BaseDialog
    :open="open"
    :title="readonly ? '月度计划详情' : task ? '编辑月度计划' : '新增月度计划'"
    width="680px"
    @close="emit('close')"
  >
    <form ref="formElement" novalidate @input.capture="clearFieldValidity" @change.capture="clearFieldValidity" id="monthly-plan-task-form" class="monthly-task-form" @submit.prevent="save('close')">
      <template v-if="scopeLabel">
        <label for="monthly-plan-customer">{{ scopeLabel }}<span v-if="!readonly" class="required"> *</span></label>
        <DeliveryCustomerSelect v-if="configuredCustomers" ref="customerSelect" v-model="customerName" :readonly="readonly" required />
        <input v-else id="monthly-plan-customer" v-model="customerName" maxlength="255" :readonly="readonly" :required="!readonly" :placeholder="`请输入${scopeLabel}`" />
      </template>
      <div class="monthly-task-field-heading"><label for="monthly-plan-work-task">工作任务<span v-if="!readonly" class="required"> *</span></label><button v-if="!readonly && templateCode === 'delivery_specialist_v1'" ref="pickerTrigger" class="monthly-template-button" type="button" :aria-expanded="pickerOpen" aria-haspopup="dialog" @click="togglePicker">选择模板</button></div>
      <textarea
        id="monthly-plan-work-task"
        ref="input"
        v-model="workTask"
        rows="6"
        maxlength="2000"
        :readonly="readonly"
        :required="!readonly"
        placeholder="请输入本月计划开展的工作任务"
      />
    </form>
    <template #actions>
      <button class="ghost-button" type="button" @click="emit('close')">
        {{ readonly ? "关闭" : "取消" }}
      </button>
      <template v-if="!readonly">
        <button class="ghost-button" type="submit" form="monthly-plan-task-form">确定</button>
        <button v-if="!task" class="ghost-button" type="button" @click="save('next')">确定并继续添加</button>
      </template>
    </template>
  </BaseDialog>
  <TaskTemplatePopover :open="open && pickerOpen" :anchor="anchor" :trigger="pickerTrigger" :selected="selectedTemplate" @close="pickerOpen = false" @select="fillTemplate" />
</template>

<style scoped src="./MonthlyPlanTaskDialog.css"></style>
