import { computed, nextTick, onMounted, ref, watch } from "vue"
import { listUserOptions } from "@/features/directory/api"
import type { DirectoryUserOption } from "@/features/directory/types"
import type { EditableTask } from "../task-editing"
import { itoSalesTaskTemplates } from "../ito-sales/task-templates"
import { innovationSalesTaskTemplates } from "../innovation-sales/task-templates"
import { emptyItoSalesTask, itoSalesTaskFieldDefinitions, type ItoSalesTaskDraft, type ItoSalesTaskFieldDefinition, type ItoSalesTaskColumn } from "../ito-sales/types"
import { insertChild, patchSharedTasks, templateTask, type SharedTaskField } from "../task-groups"

export interface SalesCollectionProps {
  templateCode: "ito_sales_v1" | "innovation_sales_v1"
  title: string
  tasks: ItoSalesTaskDraft[]
  defaultOwnerId?: string
  ownerName?: string
  fieldDefinitions?: ItoSalesTaskFieldDefinition[]
}
export function useSalesTaskCollection(props: SalesCollectionProps, emit: (event: "update:tasks", tasks: ItoSalesTaskDraft[]) => void) {
  const templates = computed(() => props.templateCode === "innovation_sales_v1" ? innovationSalesTaskTemplates : itoSalesTaskTemplates)
  const quickFillOpen = ref(false)
  const columnsOpen = ref(false)
  const users = ref<DirectoryUserOption[]>([])
  const customerFilter = ref("")
  const plannedDateFilter = ref("")
  const taskPage = ref(1)
  const pageSize = 10
  const insertedKeys = ref(new Set<string>())
  const selectedColumns = ref<ItoSalesTaskColumn[]>([])
  const customerOptions = computed(() => [...new Set(props.tasks.map(task => task.customer_name).filter(Boolean))])
  const filteredTaskEntries = computed(() => props.tasks.map((task, index) => ({ task, index })).filter(({ task }) =>
    insertedKeys.value.has(task.client_key) || ((!customerFilter.value || task.customer_name === customerFilter.value) && (!plannedDateFilter.value || task.planned_completion_date === plannedDateFilter.value)),
  ))
  const totalPages = computed(() => Math.max(1, Math.ceil(filteredTaskEntries.value.length / pageSize)))
  const pagedTaskEntries = computed(() => filteredTaskEntries.value.slice((taskPage.value - 1) * pageSize, taskPage.value * pageSize))
  const availableFields = computed(() => (props.fieldDefinitions?.length ? props.fieldDefinitions : itoSalesTaskFieldDefinitions)
    .filter(field => field.code !== "customer_name" && field.code !== "task_name").sort((a, b) => a.sort_order - b.sort_order))
  const selectedFields = computed(() => availableFields.value.filter(field => selectedColumns.value.includes(field.code)))
  const storageKey = `weekly-report:visible-columns:${props.templateCode}:weekly:all-fields-v4`
  watch(availableFields, fields => {
    try {
      const stored: unknown = JSON.parse(localStorage.getItem(storageKey) || "null")
      selectedColumns.value = Array.isArray(stored) ? fields.filter(field => stored.includes(field.code)).map(field => field.code) : fields.map(field => field.code)
    } catch { selectedColumns.value = fields.map(field => field.code) }
  }, { immediate: true, deep: true })
  watch(selectedColumns, values => { try { localStorage.setItem(storageKey, JSON.stringify(values)) } catch { /* 存储不可用时保留当前选择。 */ } }, { deep: true })
  watch([customerFilter, plannedDateFilter], () => { insertedKeys.value.clear(); taskPage.value = 1 })
  watch(totalPages, value => { taskPage.value = Math.min(taskPage.value, value) })
  watch(customerOptions, values => { if (!values.includes(customerFilter.value)) customerFilter.value = "" })
  function newTask() { return { ...emptyItoSalesTask(props.ownerName), owner_id: props.defaultOwnerId || null } }
  async function showTask(key: string) {
    await nextTick()
    taskPage.value = Math.floor(Math.max(0, filteredTaskEntries.value.findIndex(entry => entry.task.client_key === key)) / pageSize) + 1
  }
  function addTemplates(_: string, indexes: number[]) {
    const tasks = [...indexes].sort((a, b) => a - b).map(index => ({ ...newTask(), ...templateTask(templates.value[index]!, "customer_name") }))
    for (const task of tasks) insertedKeys.value.add(task.client_key)
    emit("update:tasks", [...props.tasks, ...tasks])
    quickFillOpen.value = false
    if (tasks.length) void showTask(tasks[tasks.length - 1]!.client_key)
  }
  function insertTask(index: number, shared?: SharedTaskField) {
    const task = newTask()
    insertedKeys.value.add(task.client_key)
    emit("update:tasks", insertChild(props.tasks, index, task, shared, "customer_name"))
    void showTask(task.client_key)
  }
  function patchTask(key: string, value: Partial<EditableTask>) { emit("update:tasks", patchSharedTasks(props.tasks, key, value)) }
  function removeTask(index: number) { emit("update:tasks", props.tasks.filter((_, i) => i !== index)) }
  onMounted(async () => { try { users.value = (await listUserOptions()).items } catch { users.value = [] } })
  return { templates, quickFillOpen, columnsOpen, users, customerFilter, plannedDateFilter, taskPage, pageSize, selectedColumns, customerOptions, filteredTaskEntries, totalPages, pagedTaskEntries, availableFields, selectedFields, addTemplates, insertTask, patchTask, removeTask }
}
