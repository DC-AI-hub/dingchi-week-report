<script setup lang="ts">
import { computed, ref, watch } from "vue"
import { Plus } from "lucide-vue-next"

import ExamplePreviewButton from "@/components/feedback/ExamplePreviewButton.vue"
import { createId } from "@/utils/id"
import DeliveryQuickFillDialog from "@/features/weekly-report/delivery-specialist/components/DeliveryQuickFillDialog.vue"
import { deliveryTaskTemplates } from "@/features/weekly-report/delivery-specialist/task-templates"
import { monthlyPlanScopeLabel } from "@/features/weekly-report/monthly-plan/template-fields"
import { monthlyPlanSampleFields } from "@/features/weekly-report/monthly-plan/samples"
import type { MonthlyPlanTask, MonthlyPlanTaskPayload } from "@/features/weekly-report/monthly-plan/types"

import ReportPagination from "@/components/navigation/PaginationBar.vue"
import MonthlyPlanTaskDialog from "./MonthlyPlanTaskDialog.vue"
import MonthlyPlanCustomerCell from "./MonthlyPlanCustomerCell.vue"
import TaskTextFieldDialog from "@/features/weekly-report/delivery-specialist/components/TaskTextFieldDialog.vue"

const props = defineProps<{
  tasks: MonthlyPlanTask[]
  monthKey: string
  templateCode?: string
  readonly?: boolean
  disabled?: boolean
  isLoading?: boolean
  errorMessage?: string
}>()
const emit = defineEmits<{ "update:tasks": [tasks: MonthlyPlanTask[]]; retry: [] }>()
const page = ref(1)
const pageSize = 10
const editorOpen = ref(false)
const quickFillOpen = ref(false)
const deliveryTemplate = computed(() => props.templateCode === "delivery_specialist_v1")
const viewing = ref(false)
const selectedTask = ref<MonthlyPlanTask | null>(null)
const editingText = ref<MonthlyPlanTask | null>(null)
const totalPages = computed(() => Math.ceil(props.tasks.length / pageSize))
const entries = computed(() => props.tasks.slice((page.value - 1) * pageSize, page.value * pageSize))
const scopeLabel = computed(() => monthlyPlanScopeLabel(props.templateCode || ""))
const sampleFields = computed(() => monthlyPlanSampleFields(props.templateCode || ""))
const unavailable = computed(() => props.disabled || props.isLoading || Boolean(props.errorMessage))

watch([() => props.monthKey, () => props.isLoading], () => { editorOpen.value = false; editingText.value = null; quickFillOpen.value = false; page.value = 1 })
watch(totalPages, (total) => { page.value = Math.max(1, Math.min(page.value, total)) })

function open(task: MonthlyPlanTask | null, readonly = false) {
  selectedTask.value = task
  viewing.value = readonly
  editorOpen.value = true
}

function save(payload: MonthlyPlanTaskPayload, action: "close" | "next") {
  if (unavailable.value || props.readonly) return
  const tasks = [...props.tasks]
  const index = selectedTask.value ? tasks.findIndex((task) => task.id === selectedTask.value?.id) : -1
  const task = { ...(selectedTask.value || {}), id: selectedTask.value?.id || `draft-${createId()}`, ...payload }
  if (index >= 0) tasks.splice(index, 1, task)
  else tasks.push(task)
  emit("update:tasks", tasks)
  if (index < 0) page.value = Math.ceil(tasks.length / pageSize)
  if (action === "close") editorOpen.value = false
  else selectedTask.value = null
}

function remove(id: string) {
  if (!unavailable.value && !props.readonly) emit("update:tasks", props.tasks.filter((task) => task.id !== id))
}

function patch(id: string, fields: Partial<MonthlyPlanTask>) {
  if (unavailable.value || props.readonly) return
  emit("update:tasks", props.tasks.map(task => task.id === id ? { ...task, ...fields } : task))
}

function saveText(value: string) {
  if (editingText.value) patch(editingText.value.id, { work_task: value })
  editingText.value = null
}

function insertAfter(id: string) {
  if (unavailable.value || props.readonly) return
  const tasks = [...props.tasks]
  const index = tasks.findIndex(task => task.id === id)
  if (index < 0) return
  tasks.splice(index + 1, 0, { id: `draft-${createId()}`, scope_name: "", work_task: "" })
  emit("update:tasks", tasks)
  page.value = Math.floor((index + 1) / pageSize) + 1
}

function addPlans(customer: string, indexes: number[]) {
  if (unavailable.value || props.readonly) return
  const tasks = indexes.map(index => ({ id: `draft-${createId()}`, scope_name: customer, work_task: deliveryTaskTemplates[index]!.task }))
  emit("update:tasks", [...props.tasks, ...tasks])
  quickFillOpen.value = false
  page.value = Math.ceil((props.tasks.length + tasks.length) / pageSize)
}
</script>

<template>
  <section class="dashboard-card monthly-task-panel">
    <header class="monthly-task-header">
      <div class="monthly-task-heading"><h2>月度计划</h2><span>{{ monthKey }}</span></div>
      <div v-if="!readonly" class="monthly-task-actions">
        <ExamplePreviewButton content="" :fields="sampleFields" panel-title="月度计划填写样例" />
        <button class="primary-button" type="button" :disabled="unavailable" @click="deliveryTemplate ? quickFillOpen = true : open(null)">新增计划</button>
      </div>
    </header>
    <div v-if="isLoading" class="monthly-task-empty" aria-live="polite">正在加载月度计划…</div>
    <div v-else-if="errorMessage" class="monthly-task-empty" role="alert">
      <p>{{ errorMessage }}</p>
      <button class="ghost-button" type="button" :disabled="disabled" @click="emit('retry')">重试</button>
    </div>
    <template v-else>
      <div class="monthly-task-table-wrap">
        <table class="monthly-task-table" :class="{ 'delivery-table': deliveryTemplate }">
          <thead><tr><th scope="col" class="serial">序号</th><th v-if="scopeLabel" scope="col" class="customer">{{ scopeLabel }}</th><th scope="col">工作任务</th><th v-if="!readonly" scope="col" class="actions">操作</th></tr></thead>
          <tbody>
            <tr v-for="(task, index) in entries" :key="task.id">
              <td class="serial">{{ (page - 1) * pageSize + index + 1 }}</td>
              <td v-if="scopeLabel" class="customer-name"><MonthlyPlanCustomerCell v-if="deliveryTemplate && !readonly && !unavailable" :value="task.scope_name || ''" @change="patch(task.id, { scope_name: $event })" /><template v-else>{{ task.scope_name || "—" }}</template></td>
              <td><button :class="deliveryTemplate && !readonly ? 'monthly-task-text-cell' : 'monthly-task-link'" type="button" :disabled="unavailable" :aria-label="deliveryTemplate && !readonly ? `编辑第 ${(page - 1) * pageSize + index + 1} 行工作任务` : undefined" @click="deliveryTemplate && !readonly ? editingText = task : open(task, true)">{{ task.work_task || "点击填写工作任务" }}</button></td>
              <td v-if="!readonly" class="actions">
                <button v-if="deliveryTemplate" class="link-button" type="button" :disabled="unavailable" @click="open(task, true)">查看</button>
                <button class="link-button" type="button" :disabled="unavailable" @click="open(task)">编辑</button>
                <button class="link-button danger" type="button" :disabled="unavailable" @click="remove(task.id)">删除</button>
                <button v-if="deliveryTemplate" class="link-button insert-button" type="button" :disabled="unavailable" aria-label="在此计划后新增一行" title="在此计划后新增一行" @click="insertAfter(task.id)"><Plus :size="18" aria-hidden="true" /></button>
              </td>
            </tr>
            <tr v-if="!tasks.length"><td :colspan="2 + (scopeLabel ? 1 : 0) + (readonly ? 0 : 1)" class="monthly-task-empty">{{ readonly ? "暂无月度计划" : "暂无月度计划，请新增计划" }}</td></tr>
          </tbody>
        </table>
      </div>
      <ReportPagination :page="page" :page-size="pageSize" :total="tasks.length" :total-pages="totalPages" @change="page = $event" />
    </template>
  </section>
  <MonthlyPlanTaskDialog :template-code="templateCode" :open="editorOpen" :task="selectedTask" :readonly="viewing" @close="editorOpen = false" @save="save" />
  <TaskTextFieldDialog :open="Boolean(editingText)" title="工作任务" :value="editingText?.work_task || ''" :max-length="2000" template-field="task_name" @close="editingText = null" @save="saveText" />
  <DeliveryQuickFillDialog v-if="deliveryTemplate" :open="quickFillOpen" monthly @close="quickFillOpen = false" @confirm="addPlans" />
</template>

<style scoped src="./MonthlyPlanTaskPanel.css"></style>
