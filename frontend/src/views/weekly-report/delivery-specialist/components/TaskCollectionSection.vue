<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue"

import ExamplePreviewButton, {
  type ExamplePreviewField,
} from "@/components/feedback/ExamplePreviewButton.vue"
import BaseDialog from "@/components/overlay/BaseDialog.vue"
import { listUserOptions } from "@/features/directory/api"
import type { DirectoryUserOption } from "@/features/directory/types"
import {
  deliveryWeeklyTaskSample,
  deliveryWeeklyTaskSampleFields,
} from "@/features/weekly-report/delivery-specialist/samples"
import {
  deliveryTaskFieldDefinitions,
  emptyDeliveryTask,
  type DeliveryTaskColumn,
  type DeliveryTaskDraft,
  type DeliveryTaskFieldDefinition,
} from "@/features/weekly-report/delivery-specialist/types"
import { formatDateTime } from "@/utils/date"

import ReportPagination from "../../components/ReportPagination.vue"
import TaskEditorDialog from "./TaskEditorDialog.vue"

const props = withDefaults(defineProps<{
  title: string
  mode: "monthly" | "weekly"
  tasks: DeliveryTaskDraft[]
  ownerName?: string
  /** 后端按角色返回的列配置；未返回时使用 Excel 顺序的内置配置。 */
  fieldDefinitions?: DeliveryTaskFieldDefinition[]
  /** 客户是交付专员模板专属字段；职能组模板不展示客户列。 */
  includeCustomer?: boolean
  sampleContent?: string
  sampleFields?: ReadonlyArray<ExamplePreviewField>
}>(), {
  includeCustomer: true,
  sampleContent: deliveryWeeklyTaskSample,
  sampleFields: () => deliveryWeeklyTaskSampleFields,
})
const emit = defineEmits<{ "update:tasks": [tasks: DeliveryTaskDraft[]] }>()
const editorOpen = ref(false)
const editorKey = ref(0)
const columnsOpen = ref(false)
const editingIndex = ref(-1)
const editingTask = ref<DeliveryTaskDraft | null>(null)
const detailOpen = ref(false)
const detailTask = ref<DeliveryTaskDraft | null>(null)
const users = ref<DirectoryUserOption[]>([])
const customerFilter = ref("")
const plannedDateFilter = ref("")
const taskPage = ref(1)
const taskPageSize = 10
const monthlyColumns: DeliveryTaskColumn[] = ["customer_name", "task_name", "work_content", "planned_completion_date", "owner_name"]
const weeklyFallbackColumns: DeliveryTaskColumn[] = [
  "output_description",
  "planned_completion_date",
  "progress_percent",
  "on_time_status",
]
const selectedColumns = ref<DeliveryTaskColumn[]>([])
const showCustomer = computed(() => props.includeCustomer)

const customerOptions = computed(() =>
  Array.from(
    new Set(props.tasks.map((task) => task.customer_name.trim()).filter(Boolean)),
  ).sort((left, right) => left.localeCompare(right, "zh-CN")),
)

const filteredTaskEntries = computed(() =>
  props.tasks
    .map((task, index) => ({ task, index }))
    .filter(({ task }) =>
      (!customerFilter.value || task.customer_name === customerFilter.value) &&
      (!plannedDateFilter.value || task.planned_completion_date === plannedDateFilter.value),
    )
    // 列表按客户归组，保证同一客户的连续行可以使用 rowspan 合并展示。
    .sort((left, right) => {
      if (!showCustomer.value) return left.index - right.index
      const customerOrder = left.task.customer_name.localeCompare(
        right.task.customer_name,
        "zh-CN",
      )
      return customerOrder || left.index - right.index
    }),
)

const totalTaskPages = computed(() => Math.ceil(filteredTaskEntries.value.length / taskPageSize))

const pagedTaskEntries = computed(() => {
  const start = (taskPage.value - 1) * taskPageSize
  return filteredTaskEntries.value.slice(start, start + taskPageSize)
})

const availableFields = computed<DeliveryTaskFieldDefinition[]>(() => {
  const source = props.fieldDefinitions?.length
    ? props.fieldDefinitions
    : deliveryTaskFieldDefinitions
  const monthlyAllowed = new Set(monthlyColumns)
  const fields = source
    .filter((field) => (showCustomer.value ? true : field.code !== "customer_name"))
    .filter((field) => field.code !== "task_name")
    .filter((field) => props.mode === "weekly" || monthlyAllowed.has(field.code))
    .sort((left, right) => left.sort_order - right.sort_order)
  if (fields.length) return fields
  const fallback = props.mode === "monthly" ? monthlyColumns : weeklyFallbackColumns
  return deliveryTaskFieldDefinitions.filter((field) => fallback.includes(field.code))
})

const selectedFields = computed(() => {
  const selected = new Set(selectedColumns.value)
  return availableFields.value.filter((field) => selected.has(field.code))
})

function defaultColumns(fields: DeliveryTaskFieldDefinition[]) {
  const defaults = fields
    .filter((field) => props.mode === "monthly" ? monthlyColumns.includes(field.code) : field.default_visible)
    .map((field) => field.code)
  if (defaults.length) return defaults
  const fallback = props.mode === "monthly" ? monthlyColumns : weeklyFallbackColumns
  return fields.filter((field) => fallback.includes(field.code)).map((field) => field.code)
}

watch(availableFields, (fields) => {
  // 字段配置变化时重新按 sort_order 建立默认展示列；用户勾选不会触发此监听。
  selectedColumns.value = defaultColumns(fields)
}, { immediate: true, deep: true })

watch([customerFilter, plannedDateFilter, () => props.tasks.length], () => {
  taskPage.value = 1
})

watch(customerOptions, (options) => {
  if (customerFilter.value && !options.includes(customerFilter.value)) {
    customerFilter.value = ""
  }
})

watch(totalTaskPages, (total) => {
  taskPage.value = total ? Math.min(taskPage.value, total) : 1
}, { immediate: true })

async function loadUsers() {
  try {
    users.value = (await listUserOptions()).items
  } catch {
    // 用户选项接口不可用时仍允许保存文本值，不阻断周报填写。
    users.value = []
  }
}

function addTask() {
  editingIndex.value = -1
  editingTask.value = null
  editorOpen.value = true
}

function editTask(index: number) {
  editingIndex.value = index
  editingTask.value = { ...props.tasks[index] }
  editorOpen.value = true
}

function currentLocalTimestamp() {
  const value = new Date()
  const pad = (part: number) => String(part).padStart(2, "0")
  return `${value.getFullYear()}-${pad(value.getMonth() + 1)}-${pad(value.getDate())}T${pad(value.getHours())}:${pad(value.getMinutes())}:${pad(value.getSeconds())}`
}

function saveTask(task: DeliveryTaskDraft, action: "close" | "next") {
  const normalizedTask: DeliveryTaskDraft = {
    ...emptyDeliveryTask(props.ownerName),
    ...task,
    customer_name: task.customer_name.trim(),
    task_name: task.task_name.trim(),
    owner_name: task.owner_name || props.ownerName || "",
    updated_at: currentLocalTimestamp(),
  }
  const next = [...props.tasks]
  if (editingIndex.value < 0) {
    next.push(normalizedTask)
  }
  else next.splice(editingIndex.value, 1, normalizedTask)
  emit("update:tasks", next)
  if (action === "close") {
    editorOpen.value = false
    return
  }

  // 继续填写时重新创建编辑器，清空上一条任务的表单并保留弹窗打开状态。
  editingIndex.value = -1
  editingTask.value = null
  editorKey.value += 1
}

function openTaskDetail(task: DeliveryTaskDraft) {
  detailTask.value = task
  detailOpen.value = true
}

function removeTask(index: number) {
  emit("update:tasks", props.tasks.filter((_, itemIndex) => itemIndex !== index))
}

function customerRowspan(index: number) {
  if (!showCustomer.value) return 1
  const entries = pagedTaskEntries.value
  const currentCustomer = entries[index]?.task.customer_name || ""
  if (index > 0 && (entries[index - 1]?.task.customer_name || "") === currentCustomer) return 0
  let rowspan = 1
  while (entries[index + rowspan]?.task.customer_name === currentCustomer) rowspan += 1
  return rowspan
}

function displayValue(task: DeliveryTaskDraft, column: DeliveryTaskColumn) {
  if (column === "customer_name") return task.customer_name || "未填写"
  if (column === "progress_percent") return `${Math.round(Number(task.progress_percent ?? 0))}%`
  if (column === "on_time_status") return ({ in_progress: "进行中", on_time: "按时完成", late: "延期完成", overdue: "逾期未完成", not_applicable: "不适用" })[task[column]] || "—"
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
          :content="sampleContent"
          :fields="sampleFields"
          panel-title="本周工作任务填写样例"
        />
        <button class="ghost-button" type="button" @click="columnsOpen = true">选择展示字段</button>
        <button class="primary-button" type="button" @click="addTask">新增任务</button>
      </div>
    </header>
    <div class="task-section__filters">
      <select v-if="showCustomer" v-model="customerFilter" aria-label="按客户筛选">
        <option value="">全部客户</option>
        <option v-for="customer in customerOptions" :key="customer" :value="customer">{{ customer }}</option>
      </select>
      <label>
        <span>计划完成时间</span>
        <input v-model="plannedDateFilter" type="date" aria-label="按计划完成时间筛选" />
      </label>
    </div>
    <div class="task-table-wrap">
      <table class="task-table">
        <thead>
          <tr>
            <th class="fixed-col serial-col">序号</th>
            <th v-if="showCustomer" class="fixed-col customer-col">客户</th>
            <th
              class="fixed-col task-col"
              :class="{ 'task-col--without-customer': !showCustomer }"
            >工作任务</th>
            <th v-for="field in selectedFields" :key="field.code" class="dynamic-column">{{ field.label }}</th>
            <th class="fixed-col updated-at-col">更新时间</th>
            <th class="fixed-col actions-col">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(entry, pageIndex) in pagedTaskEntries" :key="entry.task.client_key">
            <td class="fixed-col serial-col">{{ (taskPage - 1) * taskPageSize + pageIndex + 1 }}</td>
            <td
              v-if="showCustomer && customerRowspan(pageIndex) > 0"
              class="fixed-col customer-col customer-cell"
              :rowspan="customerRowspan(pageIndex)"
            >
              <span class="cell-text" :title="displayValue(entry.task, 'customer_name')">{{ displayValue(entry.task, "customer_name") }}</span>
            </td>
            <td
              class="fixed-col task-col task-cell"
              :class="{ 'task-col--without-customer': !showCustomer }"
            >
              <button class="task-link" type="button" :title="displayValue(entry.task, 'task_name')" @click="openTaskDetail(entry.task)">
                {{ displayValue(entry.task, "task_name") }}
              </button>
            </td>
            <template v-for="field in selectedFields" :key="field.code">
              <td class="dynamic-column">
                <span class="cell-text" :title="displayValue(entry.task, field.code)">{{ displayValue(entry.task, field.code) }}</span>
                <small v-if="field.code === 'document_links' && entry.task.attachments.length" class="attachment-count">{{ entry.task.attachments.length }} 个附件</small>
              </td>
            </template>
            <td class="fixed-col updated-at-col date-cell">{{ formatDateTime(entry.task.updated_at) }}</td>
            <td class="fixed-col actions-col"><button class="link-button" type="button" @click="editTask(entry.index)">编辑</button><button class="link-button danger" type="button" @click="removeTask(entry.index)">删除</button></td>
          </tr>
          <tr v-if="!filteredTaskEntries.length"><td :colspan="selectedFields.length + (showCustomer ? 5 : 4)" class="empty">暂无任务，请新增</td></tr>
        </tbody>
      </table>
    </div>
    <ReportPagination
      :page="taskPage"
      :page-size="taskPageSize"
      :total="filteredTaskEntries.length"
      :total-pages="totalTaskPages"
      @change="taskPage = $event"
    />
  </section>

  <TaskEditorDialog :key="editorKey" :open="editorOpen" :task="editingTask" :mode="mode" :owner-name="ownerName" :users="users" :include-customer="showCustomer" @close="editorOpen = false" @save="saveTask" />
  <TaskEditorDialog
    :open="detailOpen"
    :task="detailTask"
    :mode="mode"
    :owner-name="ownerName"
    :users="users"
    :include-customer="showCustomer"
    :readonly="true"
    @close="detailOpen = false"
  />
  <BaseDialog :open="columnsOpen" title="选择展示字段" width="620px" @close="columnsOpen = false">
    <div class="column-options">
      <label v-for="field in availableFields" :key="field.code"><input v-model="selectedColumns" :value="field.code" type="checkbox" />{{ field.label }}</label>
    </div>
    <template #actions><button class="primary-button" type="button" @click="columnsOpen = false">确定</button></template>
  </BaseDialog>
</template>

<style scoped src="./TaskCollectionSection.css"></style>
