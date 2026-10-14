<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue"

import ExamplePreviewButton from "@/components/feedback/ExamplePreviewButton.vue"
import BaseDialog from "@/components/overlay/BaseDialog.vue"
import { listUserOptions } from "@/features/directory/api"
import type { DirectoryUserOption } from "@/features/directory/types"
import {
  itoSalesTaskFieldDefinitions,
  type ItoSalesTaskColumn,
  type ItoSalesTaskDraft,
  type ItoSalesTaskFieldDefinition,
} from "@/features/weekly-report/ito-sales/types"
import {
  itoSalesWeeklyTaskSample,
  itoSalesWeeklyTaskSampleFields,
} from "@/features/weekly-report/ito-sales/samples"
import { formatDateTime } from "@/utils/date"

import ReportPagination from "../../components/ReportPagination.vue"
import TaskEditorDialog from "./TaskEditorDialog.vue"

const props = defineProps<{
  title: string
  tasks: ItoSalesTaskDraft[]
  defaultOwnerId?: string; ownerName?: string
  fieldDefinitions?: ItoSalesTaskFieldDefinition[]
}>()
const emit = defineEmits<{ "update:tasks": [tasks: ItoSalesTaskDraft[]] }>()

const editorOpen = ref(false)
const editorKey = ref(0)
const columnsOpen = ref(false)
const editingIndex = ref(-1)
const editingTask = ref<ItoSalesTaskDraft | null>(null)
const detailOpen = ref(false)
const detailTask = ref<ItoSalesTaskDraft | null>(null)
const users = ref<DirectoryUserOption[]>([])
const customerFilter = ref("")
const plannedDateFilter = ref("")
const taskPage = ref(1)
const pageSize = 10
const selectedColumns = ref<ItoSalesTaskColumn[]>([])

const customerOptions = computed(() =>
  Array.from(new Set(props.tasks.map((task) => task.customer_name.trim()).filter(Boolean))).sort((left, right) =>
    left.localeCompare(right, "zh-CN"),
  ),
)
const filteredTaskEntries = computed(() =>
  props.tasks
    .map((task, index) => ({ task, index }))
    .filter(({ task }) =>
      (!customerFilter.value || task.customer_name === customerFilter.value) &&
      (!plannedDateFilter.value || task.planned_completion_date === plannedDateFilter.value),
    )
    .sort(
      (left, right) =>
        left.task.customer_name.localeCompare(right.task.customer_name, "zh-CN") || left.index - right.index,
    ),
)
const totalPages = computed(() => Math.ceil(filteredTaskEntries.value.length / pageSize))
const pagedTaskEntries = computed(() =>
  filteredTaskEntries.value.slice((taskPage.value - 1) * pageSize, taskPage.value * pageSize),
)
const availableFields = computed(() => {
  const source = props.fieldDefinitions?.length ? props.fieldDefinitions : itoSalesTaskFieldDefinitions
  return source
    .filter((field) => field.code !== "customer_name" && field.code !== "task_name")
    .sort((left, right) => left.sort_order - right.sort_order)
})
const selectedFields = computed(() => {
  const selected = new Set(selectedColumns.value)
  return availableFields.value.filter((field) => selected.has(field.code))
})

function defaultColumns(fields: ItoSalesTaskFieldDefinition[]) {
  const defaults = fields.filter((field) => field.default_visible).map((field) => field.code)
  return defaults.length ? defaults : fields.slice(0, 4).map((field) => field.code)
}

watch(availableFields, (fields) => {
  selectedColumns.value = defaultColumns(fields)
}, { immediate: true, deep: true })
watch([customerFilter, plannedDateFilter, () => props.tasks.length], () => {
  taskPage.value = 1
})
watch(customerOptions, (options) => {
  if (customerFilter.value && !options.includes(customerFilter.value)) customerFilter.value = ""
})
watch(totalPages, (total) => {
  taskPage.value = total ? Math.min(taskPage.value, total) : 1
}, { immediate: true })

async function loadUsers() {
  try {
    users.value = (await listUserOptions()).items
  } catch {
    users.value = []
  }
}

function addTask() {
  editingIndex.value = -1
  editingTask.value = null
  editorKey.value += 1
  editorOpen.value = true
}

function editTask(index: number) {
  editingIndex.value = index
  editingTask.value = { ...props.tasks[index] }
  editorKey.value += 1
  editorOpen.value = true
}

function localTimestamp() {
  const now = new Date()
  const pad = (value: number) => String(value).padStart(2, "0")
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`
}

function saveTask(task: ItoSalesTaskDraft, action: "close" | "next") {
  const progress = Math.min(100, Math.max(0, Math.round(Number(task.progress_percent || 0) / 5) * 5))
  const quality = Math.min(100, Math.max(0, Math.round(Number(task.quality_percent || 0) / 5) * 5))
  const normalized = {
    ...task,
    customer_name: task.customer_name.trim(),
    task_name: task.task_name.trim(),
    owner_name: task.owner_name || props.ownerName || "",
    updated_at: localTimestamp(),
    progress_percent: progress,
    quality_percent: quality,
    completion_rate: Math.round((progress + quality) / 2),
  }
  const next = [...props.tasks]
  if (editingIndex.value < 0) next.push(normalized)
  else next.splice(editingIndex.value, 1, normalized)
  emit("update:tasks", next)
  if (action === "close") editorOpen.value = false
  else {
    editingIndex.value = -1
    editingTask.value = null
    editorKey.value += 1
  }
}

function openDetail(task: ItoSalesTaskDraft) {
  detailTask.value = task
  detailOpen.value = true
}

function removeTask(index: number) {
  emit("update:tasks", props.tasks.filter((_, itemIndex) => itemIndex !== index))
}

function customerRowspan(index: number) {
  const entries = pagedTaskEntries.value
  const current = entries[index]?.task.customer_name || ""
  if (index > 0 && (entries[index - 1]?.task.customer_name || "") === current) return 0
  let rowspan = 1
  while (entries[index + rowspan]?.task.customer_name === current) rowspan += 1
  return rowspan
}

function displayValue(task: ItoSalesTaskDraft, column: ItoSalesTaskColumn) {
  if (column === "progress_percent" || column === "quality_percent" || column === "completion_rate") {
    return `${Math.round(Number(task[column] ?? 0))}%`
  }
  if (column === "on_time_status") {
    return ({
      pending: "待完成",
      in_progress: "进行中",
      on_time: "按时完成",
      late: "延期完成",
      overdue: "逾期未完成",
      completed: "已完成",
      not_applicable: "不适用",
    } as Record<string, string>)[task[column]] || "—"
  }
  return task[column] || "—"
}

onMounted(() => void loadUsers())
</script>

<template>
  <section class="dashboard-card task-section">
    <header class="task-section__header">
      <div><h2>{{ title }}</h2></div>
      <div class="task-section__actions">
        <ExamplePreviewButton
          :content="itoSalesWeeklyTaskSample"
          :fields="itoSalesWeeklyTaskSampleFields"
          panel-title="本周工作任务填写样例"
        />
        <button class="ghost-button" type="button" @click="columnsOpen = true">选择展示字段</button>
        <button class="primary-button" type="button" @click="addTask">新增任务</button>
      </div>
    </header>
    <div class="task-section__filters">
      <select v-model="customerFilter" aria-label="按客户筛选"><option value="">全部客户</option><option v-for="customer in customerOptions" :key="customer" :value="customer">{{ customer }}</option></select>
      <label><span>计划完成时间</span><input v-model="plannedDateFilter" type="date" aria-label="按计划完成时间筛选" /></label>
    </div>
    <div class="task-table-wrap">
      <table class="task-table">
        <thead><tr><th class="fixed-col serial-col">序号</th><th class="fixed-col customer-col">客户</th><th class="fixed-col task-col">工作任务</th><th v-for="field in selectedFields" :key="field.code" class="dynamic-column">{{ field.label }}</th><th class="fixed-col updated-at-col">更新时间</th><th class="fixed-col actions-col">操作</th></tr></thead>
        <tbody>
          <tr v-for="(entry, pageIndex) in pagedTaskEntries" :key="entry.task.client_key">
            <td class="fixed-col serial-col">{{ (taskPage - 1) * pageSize + pageIndex + 1 }}</td>
            <td v-if="customerRowspan(pageIndex) > 0" class="fixed-col customer-col customer-cell" :rowspan="customerRowspan(pageIndex)"><span class="cell-text" :title="entry.task.customer_name">{{ entry.task.customer_name || "未填写" }}</span></td>
            <td class="fixed-col task-col task-cell"><button class="task-link" type="button" :title="entry.task.task_name" @click="openDetail(entry.task)">{{ entry.task.task_name || "未填写" }}</button></td>
            <td v-for="field in selectedFields" :key="field.code" class="dynamic-column"><span class="cell-text" :title="displayValue(entry.task, field.code)">{{ displayValue(entry.task, field.code) }}</span><small v-if="field.code === 'document_links' && entry.task.attachments.length" class="attachment-count">{{ entry.task.attachments.length }} 个附件</small></td>
            <td class="fixed-col updated-at-col date-cell">{{ formatDateTime(entry.task.updated_at) }}</td>
            <td class="fixed-col actions-col"><button class="link-button" type="button" @click="editTask(entry.index)">编辑</button><button class="link-button danger" type="button" @click="removeTask(entry.index)">删除</button></td>
          </tr>
          <tr v-if="!filteredTaskEntries.length"><td :colspan="selectedFields.length + 5" class="empty">暂无任务，请新增</td></tr>
        </tbody>
      </table>
    </div>
    <ReportPagination :page="taskPage" :page-size="pageSize" :total="filteredTaskEntries.length" :total-pages="totalPages" @change="taskPage = $event" />
  </section>
  <TaskEditorDialog :key="editorKey" :open="editorOpen" :task="editingTask" :default-owner-id="defaultOwnerId" :owner-name="ownerName" :users="users" @close="editorOpen = false" @save="saveTask" />
  <TaskEditorDialog
    :open="detailOpen"
    :task="detailTask"
    :default-owner-id="defaultOwnerId" :owner-name="ownerName"
    :users="users"
    :readonly="true"
    @close="detailOpen = false"
  />
  <BaseDialog :open="columnsOpen" title="选择展示字段" width="640px" @close="columnsOpen = false">
    <div class="column-options"><label v-for="field in availableFields" :key="field.code"><input v-model="selectedColumns" :value="field.code" type="checkbox" />{{ field.label }}</label></div>
    <template #actions><button class="primary-button" type="button" @click="columnsOpen = false">确定</button></template>
  </BaseDialog>
</template>

<style scoped src="./TaskCollectionSection.css"></style>
