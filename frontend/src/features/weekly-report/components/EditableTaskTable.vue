<script setup lang="ts" generic="T extends EditableTask">
import { computed, ref } from "vue"
import { Plus } from "lucide-vue-next"
import type { DirectoryUserOption } from "@/features/directory/types"
import type { EditableTask, EditableTaskColumn, EditableTaskField, TaskTemplateOption } from "@/features/weekly-report/task-editing"
import { formatDateTime } from "@/utils/date"
import TaskInlineField from "./TaskInlineField.vue"
import TaskTextFieldDialog from "@/features/weekly-report/delivery-specialist/components/TaskTextFieldDialog.vue"
import TaskEvidenceDialog from "./TaskEvidenceDialog.vue"
import type { DeliveryTaskAttachment } from "@/features/weekly-report/delivery-specialist/types"
import { deliveryTaskTemplates } from "@/features/weekly-report/delivery-specialist/task-templates"

const props = withDefaults(defineProps<{
  entries: { task: T; index: number }[]
  fields: EditableTaskField[]
  users: DirectoryUserOption[]
  offset: number
  scopeField?: "customer_name" | "dimension"
  templates?: readonly TaskTemplateOption[]
}>(), { scopeField: "customer_name", templates: () => deliveryTaskTemplates })
const emit = defineEmits<{
  patch: [key: string, value: Partial<EditableTask>]
  insert: [index: number]
  edit: [index: number]
  remove: [index: number]
  view: [task: T]
}>()
const textFields: EditableTaskColumn[] = ["task_name", "work_content", "output_description", "progress_text", "delay_reason", "document_links"]
const editing = ref<{ key: string; field: EditableTaskColumn; value: string } | null>(null)
const evidence = ref<{ key: string; links: string; attachments: DeliveryTaskAttachment[] } | null>(null)
const editingTitle = computed(() => editing.value ? (editing.value.field === "dimension" ? "维度" : editing.value.field === "task_name" ? "工作任务" : props.fields.find(field => field.code === editing.value?.field)?.label || "内容") : "")
const templateField = computed(() => {
  const field = editing.value?.field
  return field === "dimension" || field === "task_name" || field === "work_content" ? field : undefined
})
function editText(task: EditableTask, field: EditableTaskColumn) {
  if (field === "document_links") { editEvidence(task); return }
  editing.value = { key: task.client_key, field, value: String(task[field] || "") }
}
function editEvidence(task: EditableTask) {
  evidence.value = { key: task.client_key, links: task.document_links, attachments: task.attachments.map(item => ({ ...item })) }
}
function saveEvidence(links: string, attachments: DeliveryTaskAttachment[]) {
  if (!evidence.value) return
  emit("patch", evidence.value.key, { document_links: links, attachments })
  evidence.value = null
}
function saveText(value: string, templateIndex?: number) {
  if (!editing.value) return
  const patch: Partial<EditableTask> = { [editing.value.field]: value }
  const template = templateIndex === undefined ? undefined : props.templates[templateIndex]
  const task = props.entries.find(entry => entry.task.client_key === editing.value?.key)?.task
  if (template && task && templateField.value) {
    if (props.scopeField === "dimension" && editing.value.field !== "dimension" && !task.dimension?.trim()) patch.dimension = template.dimension || ""
    for (const [field, content] of [["task_name", template.task], ["work_content", template.work]] as const) {
      if (field !== editing.value.field && !task[field].trim()) patch[field] = content
    }
  }
  emit("patch", editing.value.key, patch)
  editing.value = null
}
</script>
<template>
  <div class="editable-table-wrap">
    <table class="editable-task-table">
      <thead><tr><th class="serial-col">序号</th><th class="customer-col">{{ scopeField === "dimension" ? "维度" : "客户" }}</th><th class="task-col">工作任务</th><th v-for="field in fields" :key="field.code" class="value-col" :class="{ 'multiline-col': textFields.includes(field.code) }">{{ field.label }}</th><th class="date-col">更新时间</th><th class="actions-col">操作</th></tr></thead>
      <tbody>
        <tr v-for="(entry, index) in entries" :key="entry.task.client_key" :class="{ 'blank-row': !entry.task.task_name }">
          <td class="serial-col">{{ offset + index + 1 }}</td>
          <td class="customer-col"><button v-if="scopeField === 'dimension'" class="text-cell" type="button" :aria-label="`编辑第 ${offset + index + 1} 行维度`" @click="editText(entry.task, 'dimension')">{{ entry.task.dimension || '点击填写维度' }}</button><TaskInlineField v-else :task="entry.task" field="customer_name" label="客户" :users="users" @patch="emit('patch', entry.task.client_key, $event)" /></td>
          <td class="task-col"><button class="text-cell" type="button" :aria-label="`编辑第 ${offset + index + 1} 行工作任务`" @click="editText(entry.task, 'task_name')">{{ entry.task.task_name || '点击填写工作任务' }}</button></td>
          <td v-for="field in fields" :key="field.code" class="value-col" :class="{ 'multiline-col': textFields.includes(field.code) }">
            <button v-if="textFields.includes(field.code)" class="text-cell" type="button" :aria-label="`编辑第 ${offset + index + 1} 行${field.label}`" @click="editText(entry.task, field.code)">{{ entry.task[field.code] || `点击填写${field.label}` }}</button>
            <TaskInlineField v-else :task="entry.task" :field="field.code" :label="field.label" :users="users" @patch="emit('patch', entry.task.client_key, $event)" />
            <button v-if="field.code === 'document_links'" type="button" class="link-button attachment-button" @click="editEvidence(entry.task)">{{ entry.task.attachments.length ? `${entry.task.attachments.length} 个附件` : '管理附件' }}</button>
          </td>
          <td class="date-col">{{ formatDateTime(entry.task.updated_at) }}</td>
          <td class="actions-col"><div class="row-actions"><button type="button" class="link-button" @click="emit('view', entry.task)">查看</button><button type="button" class="link-button" @click="emit('edit', entry.index)">编辑</button><button type="button" class="link-button danger" @click="emit('remove', entry.index)">删除</button><button type="button" class="insert-button" :aria-label="`在第 ${offset + index + 1} 行后插入任务`" title="在此行后插入任务" @click="emit('insert', entry.index)"><Plus :size="17" aria-hidden="true" /></button></div></td>
        </tr>
        <tr v-if="!entries.length"><td :colspan="fields.length + 5" class="empty">暂无任务，请新增</td></tr>
      </tbody>
    </table>
  </div>
  <TaskTextFieldDialog :open="Boolean(editing)" :title="editingTitle" :value="editing?.value || ''" :template-field="templateField" :templates="templates" :max-length="editing?.field === 'dimension' ? 64 : editing?.field === 'task_name' ? 255 : undefined" @close="editing = null" @save="saveText" />
  <TaskEvidenceDialog :open="Boolean(evidence)" :links="evidence?.links || ''" :attachments="evidence?.attachments || []" @close="evidence = null" @save="saveEvidence" />
</template>
<style scoped src="./EditableTaskTable.css"></style>
