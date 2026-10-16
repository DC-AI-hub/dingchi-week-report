<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from "vue"

import ExamplePreviewButton from "@/components/feedback/ExamplePreviewButton.vue"
import BaseDialog from "@/components/overlay/BaseDialog.vue"
import { listUserOptions } from "@/features/directory/api"
import type { DirectoryUserOption } from "@/features/directory/types"
import { recruitmentWeeklyTaskSample, recruitmentWeeklyTaskSampleFields } from "@/features/weekly-report/recruitment/samples"
import {
  emptyRecruitmentTask,
  recruitmentTaskFieldDefinitions,
  type RecruitmentTaskColumn,
  type RecruitmentTaskDraft,
  type RecruitmentTaskFieldDefinition,
} from "@/features/weekly-report/recruitment/types"
import EditableTaskTable from "@/features/weekly-report/components/EditableTaskTable.vue"
import TaskQuickFillDialog from "@/features/weekly-report/components/TaskQuickFillDialog.vue"
import { recruitmentTaskTemplates } from "@/features/weekly-report/recruitment/task-templates"
import type { EditableTask } from "@/features/weekly-report/task-editing"

import ReportPagination from "../../components/ReportPagination.vue"
import TaskEditorDialog from "./TaskEditorDialog.vue"

const props = defineProps<{
  title: string
  tasks: RecruitmentTaskDraft[]
  defaultOwnerId?: string; ownerName?: string
  fieldDefinitions?: RecruitmentTaskFieldDefinition[]
}>()
const emit = defineEmits<{ "update:tasks": [tasks: RecruitmentTaskDraft[]] }>()

const editorOpen = ref(false)
const quickFillOpen = ref(false)
const insertedKeys = ref(new Set<string>())
const editorKey = ref(0)
const columnsOpen = ref(false)
const editingIndex = ref(-1)
const editingTask = ref<RecruitmentTaskDraft | null>(null)
const detailOpen = ref(false)
const detailTask = ref<RecruitmentTaskDraft | null>(null)
const users = ref<DirectoryUserOption[]>([])
const dimensionFilter = ref("")
const plannedDateFilter = ref("")
const taskPage = ref(1)
const pageSize = 10
const selectedColumns = ref<RecruitmentTaskColumn[]>([])

const dimensionOptions = computed(() => Array.from(new Set(props.tasks.map((task) => task.dimension.trim()).filter(Boolean))).sort((left, right) => left.localeCompare(right, "zh-CN")))
const filteredTaskEntries = computed(() => props.tasks
  .map((task, index) => ({ task, index }))
  .filter(({ task }) =>
    insertedKeys.value.has(task.client_key) || ((!dimensionFilter.value || task.dimension === dimensionFilter.value) &&
    (!plannedDateFilter.value || task.planned_completion_date === plannedDateFilter.value)),
  )
)
const totalPages = computed(() => Math.ceil(filteredTaskEntries.value.length / pageSize))
const pagedTaskEntries = computed(() => filteredTaskEntries.value.slice((taskPage.value - 1) * pageSize, taskPage.value * pageSize))
const availableFields = computed(() => {
  const source = props.fieldDefinitions?.length ? props.fieldDefinitions : recruitmentTaskFieldDefinitions
  return source.filter((field) => field.code !== "dimension" && field.code !== "task_name").sort((left, right) => left.sort_order - right.sort_order)
})
const selectedFields = computed(() => {
  const selected = new Set(selectedColumns.value)
  return availableFields.value.filter((field) => selected.has(field.code))
})

function defaultColumns(fields: RecruitmentTaskFieldDefinition[]) {
  const defaults = fields.filter((field) => field.default_visible).map((field) => field.code)
  return defaults.length ? defaults : fields.slice(0, 4).map((field) => field.code)
}

const storageKey = "weekly-report:visible-columns:recruitment_v1:weekly"
watch(availableFields, fields => {
  try {
    const stored: unknown = JSON.parse(localStorage.getItem(storageKey) || "null")
    selectedColumns.value = Array.isArray(stored) ? stored.filter((code): code is RecruitmentTaskColumn => fields.some(field => field.code === code)) : defaultColumns(fields)
  } catch { selectedColumns.value = defaultColumns(fields) }
}, { immediate: true, deep: true })
watch(selectedColumns, columns => { try { localStorage.setItem(storageKey, JSON.stringify(columns)) } catch { /* 禁用存储时仍可编辑。 */ } }, { deep: true })
watch([dimensionFilter, plannedDateFilter], () => { insertedKeys.value = new Set() })
watch([dimensionFilter, plannedDateFilter, () => props.tasks.length], () => { taskPage.value = 1 })
watch(dimensionOptions, (options) => { if (dimensionFilter.value && !options.includes(dimensionFilter.value)) dimensionFilter.value = "" })
watch(totalPages, (total) => { taskPage.value = total ? Math.min(taskPage.value, total) : 1 }, { immediate: true })

async function loadUsers() {
  try { users.value = (await listUserOptions()).items } catch { users.value = [] }
}

function addTask() { quickFillOpen.value = true }
function editTask(index: number) { editingIndex.value = index; editingTask.value = { ...props.tasks[index] }; editorOpen.value = true }
function localTimestamp() { const now = new Date(); const pad = (value: number) => String(value).padStart(2, "0"); return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}` }

function saveTask(task: RecruitmentTaskDraft, action: "close" | "next") {
  const dimension = task.dimension.trim()
  const taskName = task.task_name.trim()
  const progress = Math.round(Number(task.progress_percent || 0) / 5) * 5
  const quality = Math.round(Number(task.quality_percent || 0) / 5) * 5
  const normalized = {
    ...emptyRecruitmentTask(props.ownerName),
    ...task,
    dimension,
    task_name: taskName,
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
  else { editingIndex.value = -1; editingTask.value = null; editorKey.value += 1 }
}

function openDetail(task: RecruitmentTaskDraft) { detailTask.value = task; detailOpen.value = true }
function removeTask(index: number) { emit("update:tasks", props.tasks.filter((_, itemIndex) => itemIndex !== index)) }
function patchTask(key: string, patch: Partial<EditableTask>) {
  emit("update:tasks", props.tasks.map(task => {
    if (task.client_key !== key) return task
    const next = { ...task, ...patch, updated_at: localTimestamp() }
    next.completion_rate = Math.round((Number(next.progress_percent || 0) + Number(next.quality_percent || 0)) / 2)
    return next
  }))
}
function newTask() {
  return { ...emptyRecruitmentTask(props.ownerName), owner_id: props.defaultOwnerId || null, updated_at: localTimestamp() }
}
async function showTask(key: string) {
  await nextTick()
  const index = filteredTaskEntries.value.findIndex(entry => entry.task.client_key === key)
  if (index >= 0) taskPage.value = Math.floor(index / pageSize) + 1
}
function insertTask(index: number) {
  const task = newTask()
  const tasks = [...props.tasks]
  tasks.splice(index + 1, 0, task)
  insertedKeys.value.add(task.client_key)
  emit("update:tasks", tasks)
  void showTask(task.client_key)
}
function addTemplates(_: string, indexes: number[]) {
  const tasks = [...indexes].sort((a, b) => a - b).map(index => {
    const template = recruitmentTaskTemplates[index]!
    const task = { ...newTask(), dimension: template.dimension, task_name: template.task, work_content: template.work }
    insertedKeys.value.add(task.client_key)
    return task
  })
  emit("update:tasks", [...props.tasks, ...tasks])
  quickFillOpen.value = false
  if (tasks.length) void showTask(tasks[tasks.length - 1]!.client_key)
}

onMounted(() => void loadUsers())
</script>

<template>
  <section class="dashboard-card task-section">
    <header class="task-section__header">
      <div><h2>{{ title }}</h2></div>
      <div class="task-section__actions"><ExamplePreviewButton :content="recruitmentWeeklyTaskSample" :fields="recruitmentWeeklyTaskSampleFields" panel-title="本周工作任务填写样例" /><button class="ghost-button" type="button" @click="columnsOpen = true">选择展示字段</button><button class="primary-button" type="button" @click="addTask">新增任务</button></div>
    </header>
    <div class="task-section__filters"><select v-model="dimensionFilter" aria-label="按维度筛选"><option value="">全部维度</option><option v-for="dimension in dimensionOptions" :key="dimension" :value="dimension">{{ dimension }}</option></select><label><span>计划完成时间</span><input v-model="plannedDateFilter" type="date" aria-label="按计划完成时间筛选" /></label></div>
    <EditableTaskTable :entries="pagedTaskEntries" :fields="selectedFields" :users="users" :offset="(taskPage - 1) * pageSize" scope-field="dimension" :templates="recruitmentTaskTemplates" @patch="patchTask" @edit="editTask" @view="openDetail" @remove="removeTask" @insert="insertTask" />
    <ReportPagination :page="taskPage" :page-size="pageSize" :total="filteredTaskEntries.length" :total-pages="totalPages" @change="taskPage = $event" />
  </section>
  <TaskQuickFillDialog :open="quickFillOpen" recruitment :templates="recruitmentTaskTemplates" @close="quickFillOpen = false" @confirm="addTemplates" />
  <TaskEditorDialog :key="editorKey" :open="editorOpen" :task="editingTask" :default-owner-id="defaultOwnerId" :owner-name="ownerName" :users="users" @close="editorOpen = false" @save="saveTask" />
  <TaskEditorDialog
    :open="detailOpen"
    :task="detailTask"
    :default-owner-id="defaultOwnerId" :owner-name="ownerName"
    :users="users"
    :readonly="true"
    @close="detailOpen = false"
  />
  <BaseDialog :open="columnsOpen" title="选择展示字段" width="640px" @close="columnsOpen = false"><div class="column-options"><label v-for="field in availableFields" :key="field.code"><input v-model="selectedColumns" :value="field.code" type="checkbox" />{{ field.label }}</label></div><template #actions><button class="primary-button" type="button" @click="columnsOpen = false">确定</button></template></BaseDialog>
</template>

<style scoped src="./TaskCollectionSection.css"></style>
