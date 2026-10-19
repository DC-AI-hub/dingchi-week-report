<script setup lang="ts">
import { computed, defineAsyncComponent, ref, watch } from "vue"
import { isSupportedTemplate } from "@/features/weekly-report/template-support"
import { Plus } from "lucide-vue-next"

import ExamplePreviewButton from "@/components/feedback/ExamplePreviewButton.vue"
import { createId } from "@/utils/id"
import DeliveryQuickFillDialog from "@/features/weekly-report/components/TaskQuickFillDialog.vue"
import { deliveryAssistantTaskTemplates } from "@/features/weekly-report/delivery-assistant/task-templates"
import { deliveryTaskTemplates } from "@/features/weekly-report/delivery-specialist/task-templates"
import { itoSalesMonthlyTaskTemplates } from "@/features/weekly-report/ito-sales/task-templates"
import { innovationSalesTaskTemplates } from "@/features/weekly-report/innovation-sales/task-templates"
import TemplateCustomerCell from "@/features/weekly-report/components/TemplateCustomerCell.vue"
import { functionalTaskTemplates } from "@/features/weekly-report/functional-group/task-templates"
import { recruitmentMonthlyTaskTemplates } from "@/features/weekly-report/recruitment/task-templates"
import { monthlyPlanScopeLabel } from "@/features/weekly-report/monthly-plan/template-fields"
import { monthlyPlanSampleFields } from "@/features/weekly-report/monthly-plan/samples"
import type { MonthlyPlanTask, MonthlyPlanTaskPayload } from "@/features/weekly-report/monthly-plan/types"

import ReportPagination from "@/components/navigation/PaginationBar.vue"
import ScrollableTabs from "@/components/navigation/ScrollableTabs.vue"
import TemplateDimensionCell from "@/features/weekly-report/components/TemplateDimensionCell.vue"
import TemplateTaskCell from "@/features/weekly-report/components/TemplateTaskCell.vue"
import { previewTaskTemplate } from "@/features/weekly-report/task-texts"
import type { TaskTemplateOption } from "@/features/weekly-report/task-editing"
import type { EditableTask } from "@/features/weekly-report/task-editing"
import TaskTextFieldDialog from "@/features/weekly-report/delivery-specialist/components/TaskTextFieldDialog.vue"

const MonthlyPlanTaskDialog = defineAsyncComponent(() => import("./MonthlyPlanTaskDialog.vue"))

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
const deliveryTemplate = computed(() => ["delivery_specialist_v1", "delivery_assistant_v1"].includes(props.templateCode || ""))
const recruitmentTemplate = computed(() => props.templateCode === "recruitment_v1")
const salesTemplate = computed(() => ["ito_sales_v1", "innovation_sales_v1"].includes(props.templateCode || ""))
const functionalTemplate = computed(() => props.templateCode === "functional_group_v1")
const editableTemplate = computed(() => deliveryTemplate.value || recruitmentTemplate.value || salesTemplate.value || functionalTemplate.value)
const taskTemplates = computed<readonly TaskTemplateOption[]>(() => functionalTemplate.value ? functionalTaskTemplates : salesTemplate.value ? (props.templateCode === "innovation_sales_v1" ? innovationSalesTaskTemplates : itoSalesMonthlyTaskTemplates) : recruitmentTemplate.value ? recruitmentMonthlyTaskTemplates : props.templateCode === "delivery_assistant_v1" ? deliveryAssistantTaskTemplates : deliveryTaskTemplates)
const viewing = ref(false)
const selectedTask = ref<MonthlyPlanTask | null>(null)
const editingText = ref<MonthlyPlanTask | null>(null)
const editingField = ref<"scope_name" | "work_task">("work_task")
function openText(task: MonthlyPlanTask, field: "scope_name" | "work_task") {
  editingField.value = field
  editingText.value = task
}
const activeCustomer = ref("")
const customers = computed(() => [...new Set(props.tasks.map(task => task.scope_name || ""))]
  .sort((a, b) => a.localeCompare(b, "zh-CN"))
  .map(id => ({ id, name: id || "未选择客户" })))
const filteredTasks = computed(() => deliveryTemplate.value
  ? props.tasks.filter(task => (task.scope_name || "") === activeCustomer.value) : props.tasks)
const totalPages = computed(() => Math.max(1, Math.ceil(filteredTasks.value.length / pageSize)))
const entries = computed(() => filteredTasks.value.slice((page.value - 1) * pageSize, page.value * pageSize))
watch(customers, tabs => {
  if (!tabs.some(tab => tab.id === activeCustomer.value)) activeCustomer.value = tabs[0]?.id || ""
}, { immediate: true })
watch(activeCustomer, () => { page.value = 1 })
function displayTask(task: MonthlyPlanTask) {
  return task.task_source === "template" && task.task_template
    ? previewTaskTemplate(task.task_template, task.task_values || []) : task.work_task
}
function patchTemplate(id: string, value: Partial<EditableTask>) {
  patch(id, { work_task: value.task_name, task_values: value.task_values })
}
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

function saveText(value: string, templateIndex?: number) {
  if (editingText.value) {
    const current = props.tasks.find(task => task.id === editingText.value?.id)
    const template = templateIndex === undefined ? undefined : taskTemplates.value[templateIndex]
    const fields: Partial<MonthlyPlanTask> = { [editingField.value]: value }
    if (salesTemplate.value && template) {
      if (editingField.value === "scope_name" || !current?.scope_name?.trim()) Object.assign(fields, {
        scope_name: template.customer || "", customer_source: "template", customer_template: template.customer || "",
        customer_values: Array((template.customer || "").split(/[?？]/).length - 1).fill(""),
      })
      if (editingField.value === "work_task" || !current?.work_task.trim()) Object.assign(fields, {
        task_source: "template", task_template: template.task, work_task: template.task,
        task_values: Array(template.task.split(/[?？]/).length - 1).fill(""),
      })
    }
    if (recruitmentTemplate.value && template) {
      if (editingField.value === "scope_name" || !current?.scope_name?.trim()) Object.assign(fields, {
        scope_name: template.dimension || "", dimension_source: "template", dimension_template: template.dimension || "",
        dimension_values: Array((template.dimension || "").split(/[?？]/).length - 1).fill(""),
      })
      if (editingField.value === "work_task" || !current?.work_task.trim()) Object.assign(fields, {
        task_source: "template", task_template: template.task, work_task: template.task,
        task_values: Array(template.task.split(/[?？]/).length - 1).fill(""),
      })
    }
    if ((deliveryTemplate.value || functionalTemplate.value) && editingField.value === "work_task") {
      Object.assign(fields, template ? {
        task_source: "template", task_template: template.task,
        task_values: Array(template.task.split(/[?？]/).length - 1).fill(""), work_task: template.task,
      } : { task_source: "custom", task_template: "", task_values: [] })
    }
    patch(editingText.value.id, fields)
  }
  editingText.value = null
}

function insertAfter(id: string) {
  if (unavailable.value || props.readonly) return
  const tasks = [...props.tasks]
  const index = tasks.findIndex(task => task.id === id)
  if (index < 0) return
  tasks.splice(index + 1, 0, { id: `draft-${createId()}`, scope_name: deliveryTemplate.value ? tasks[index]?.scope_name || activeCustomer.value : "", work_task: "", task_source: "custom" })
  emit("update:tasks", tasks)
  page.value = Math.floor((filteredTasks.value.findIndex(task => task.id === id) + 1) / pageSize) + 1
}

function addPlans(customer: string, indexes: number[]) {
  if (unavailable.value || props.readonly) return
  const tasks = indexes.map(index => ({ id: `draft-${createId()}`, scope_name: salesTemplate.value ? taskTemplates.value[index]!.customer : recruitmentTemplate.value ? recruitmentMonthlyTaskTemplates[index]!.dimension : customer, work_task: taskTemplates.value[index]!.task,
    ...(editableTemplate.value ? { task_source: "template" as const, task_template: taskTemplates.value[index]!.task,
      task_values: Array(taskTemplates.value[index]!.task.split(/[?？]/).length - 1).fill("") } : {}),
    ...(salesTemplate.value ? { customer_source: "template" as const, customer_template: taskTemplates.value[index]!.customer || "", customer_values: Array((taskTemplates.value[index]!.customer || "").split(/[?？]/).length - 1).fill("") } : {}),
    ...(recruitmentTemplate.value ? { dimension_source: "template" as const, dimension_template: recruitmentMonthlyTaskTemplates[index]!.dimension, dimension_values: Array(recruitmentMonthlyTaskTemplates[index]!.dimension.split(/[?？]/).length - 1).fill("") } : {}) }))
  emit("update:tasks", [...props.tasks, ...tasks])
  quickFillOpen.value = false
  if (deliveryTemplate.value) activeCustomer.value = customer
  page.value = Math.ceil(((deliveryTemplate.value ? props.tasks.filter(task => task.scope_name === customer).length : props.tasks.length) + tasks.length) / pageSize)
}
</script>

<template>
  <section v-if="readonly || isSupportedTemplate(templateCode)" class="dashboard-card monthly-task-panel">
    <header class="monthly-task-header">
      <div class="monthly-task-heading"><h2>月度计划</h2><span>{{ monthKey }}</span></div>
      <div v-if="!readonly" class="monthly-task-actions">
        <ExamplePreviewButton content="" :fields="sampleFields" panel-title="月度计划填写样例" />
        <button class="primary-button" type="button" :disabled="unavailable" @click="editableTemplate ? quickFillOpen = true : open(null)">新增计划</button>
      </div>
    </header>
    <ScrollableTabs v-if="deliveryTemplate && customers.length" v-model="activeCustomer" :items="customers" class="monthly-customer-tabs" />
    <div v-if="isLoading" class="monthly-task-empty" aria-live="polite">正在加载月度计划…</div>
    <div v-else-if="errorMessage" class="monthly-task-empty" role="alert">
      <p>{{ errorMessage }}</p>
      <button class="ghost-button" type="button" :disabled="disabled" @click="emit('retry')">重试</button>
    </div>
    <template v-else>
      <div class="monthly-task-table-wrap">
        <table class="monthly-task-table" :class="{ 'delivery-table': editableTemplate, 'delivery-monthly-table': deliveryTemplate }">
          <thead><tr><th scope="col" class="serial">序号</th><th v-if="scopeLabel && !deliveryTemplate" scope="col" class="customer">{{ scopeLabel }}</th><th scope="col">工作任务</th><th v-if="!readonly" scope="col" class="actions">操作</th></tr></thead>
          <tbody>
            <tr v-for="(task, index) in entries" :key="task.id">
              <td class="serial">{{ (page - 1) * pageSize + index + 1 }}</td>
              <td v-if="scopeLabel && !deliveryTemplate" class="customer-name"><template v-if="salesTemplate"><span v-if="readonly || unavailable" class="monthly-task-plain">{{ task.customer_source === 'template' ? previewTaskTemplate(task.customer_template || '', task.customer_values || []) : task.scope_name || '—' }}</span><TemplateCustomerCell :label="scopeLabel" v-else-if="task.customer_source === 'template'" :task="{ ...task, customer_name: task.scope_name }" @patch="patch(task.id, { scope_name: $event.customer_name, customer_values: $event.customer_values })" /><button v-else class="monthly-task-text-cell" type="button" :aria-label="`编辑${scopeLabel}`" @click="openText(task, 'scope_name')">{{ task.scope_name || `点击填写${scopeLabel}` }}</button></template><template v-else><TemplateDimensionCell v-if="recruitmentTemplate && !readonly && !unavailable && task.dimension_source === 'template'" :task="{ ...task, dimension: task.scope_name }" @patch="patch(task.id, { scope_name: $event.dimension, dimension_values: $event.dimension_values })" /><span v-else-if="recruitmentTemplate && (readonly || unavailable)" class="monthly-task-plain">{{ task.dimension_source === 'template' ? previewTaskTemplate(task.dimension_template || '', task.dimension_values || []) : task.scope_name || '—' }}</span><button v-else-if="recruitmentTemplate && !readonly" class="monthly-task-text-cell" type="button" :disabled="unavailable" aria-label="编辑维度" @click="openText(task, 'scope_name')">{{ task.scope_name || '点击填写维度' }}</button><template v-else>{{ task.scope_name || "—" }}</template></template></td>
              <td>
                <template v-if="editableTemplate">
                  <span v-if="readonly || unavailable" class="monthly-task-plain">{{ displayTask(task) || "—" }}</span>
                  <TemplateTaskCell v-else-if="task.task_source === 'template' && task.task_template"
                    :task="{ task_name: task.work_task, task_template: task.task_template, task_values: task.task_values }"
                    @patch="patchTemplate(task.id, $event)" />
                  <button v-else class="monthly-task-text-cell" type="button" @click="openText(task, 'work_task')">{{ task.work_task || "点击填写工作任务" }}</button>
                </template>
                <button v-else :class="editableTemplate && !readonly ? 'monthly-task-text-cell' : 'monthly-task-link'" type="button" :disabled="unavailable" @click="editableTemplate && !readonly ? openText(task, 'work_task') : open(task, true)">{{ task.work_task || "点击填写工作任务" }}</button>
              </td>
              <td v-if="!readonly" class="actions">
                <button v-if="!editableTemplate" class="link-button" type="button" :disabled="unavailable" @click="open(task, true)">查看</button>
                <button v-if="!editableTemplate" class="link-button" type="button" :disabled="unavailable" @click="open(task)">编辑</button>
                <button class="link-button danger" type="button" :disabled="unavailable" @click="remove(task.id)">删除</button>
                <button v-if="editableTemplate" class="link-button insert-button" type="button" :disabled="unavailable" aria-label="在此计划后新增一行" title="在此计划后新增一行" @click="insertAfter(task.id)"><Plus :size="18" aria-hidden="true" /></button>
              </td>
            </tr>
            <tr v-if="!filteredTasks.length"><td :colspan="2 + (scopeLabel && !deliveryTemplate ? 1 : 0) + (readonly ? 0 : 1)" class="monthly-task-empty">{{ readonly ? "暂无月度计划" : "暂无月度计划，请新增计划" }}</td></tr>
          </tbody>
        </table>
      </div>
      <ReportPagination :page="page" :page-size="pageSize" :total="filteredTasks.length" :total-pages="totalPages" @change="page = $event" />
    </template>
  </section>
  <MonthlyPlanTaskDialog v-if="!editableTemplate && (readonly || isSupportedTemplate(templateCode))" :template-code="templateCode" :open="editorOpen" :task="selectedTask" :readonly="viewing" @close="editorOpen = false" @save="save" />
  <TaskTextFieldDialog v-if="isSupportedTemplate(templateCode)" :customer-label="scopeLabel" :open="Boolean(editingText)" :title="editingField === 'scope_name' ? scopeLabel : '工作任务'" :value="editingText?.[editingField] || ''" :max-length="editingField === 'scope_name' ? 255 : editableTemplate ? undefined : 2000" :template-field="editingField === 'scope_name' ? (salesTemplate ? 'customer_name' : 'dimension') : 'task_name'" :templates="taskTemplates" @close="editingText = null" @save="saveText" />
  <DeliveryQuickFillDialog v-if="editableTemplate" :open="quickFillOpen" :customer-label="scopeLabel" monthly :scope-less="functionalTemplate" :sales="salesTemplate" :recruitment="recruitmentTemplate" :templates="taskTemplates" @close="quickFillOpen = false" @confirm="addPlans" />
</template>

<style scoped src="./MonthlyPlanTaskPanel.css"></style>
