import { reportDraftValidity } from "@/utils/form-validation"
import { computed, reactive, ref, watch } from "vue"

import DeliveryCustomerSelect from "@/mobile/features/weekly-report/components/DeliveryCustomerSelect.vue"
import type { DirectoryUserOption } from "@/mobile/features/directory/types"
import {
  emptyDeliveryTask,
  type DeliveryTaskAttachment,
  type DeliveryTaskDraft,
} from "@/mobile/features/weekly-report/delivery-specialist/types"
import { deleteReportAttachment, uploadPendingReportAttachment } from "@/mobile/features/weekly-report/api"
import { useNoticeStore } from "@/app/stores/notice"

export interface FunctionalTaskFormProps {
  open: boolean
  task: DeliveryTaskDraft | null
  mode: "monthly" | "weekly"
  defaultOwnerId?: string
  ownerName: string
  users: DirectoryUserOption[]
  includeCustomer: boolean
  readonly: boolean
  reportId?: string
}
type FormEmit = {
  (event: "close"): void
  (event: "save", task: DeliveryTaskDraft, action: "close" | "next"): void
}

export function useFunctionalTaskForm(props: FunctionalTaskFormProps, emit: FormEmit) {
const form = reactive<DeliveryTaskDraft>(emptyDeliveryTask())
const ownerId = ref("")
const collaboratorIds = ref<string[]>([])
const unknownCollaboratorNames = ref<string[]>([])
const fileInputRef = ref<HTMLInputElement | null>(null)
const attachmentBusy = ref(false)
const noticeStore = useNoticeStore()
const formElement = ref<HTMLFormElement | null>(null)
const customerSelect = ref<InstanceType<typeof DeliveryCustomerSelect> | null>(null)





function cloneTask(task: DeliveryTaskDraft | null) {
  const next = emptyDeliveryTask(props.ownerName)
  if (!task) next.owner_id = props.defaultOwnerId || null
  if (!task) return next
  return {
    ...next,
    ...task,
    attachments: (task.attachments || []).map((attachment) => ({ ...attachment })),
  }
}

function splitNames(value: string) {
  return value
    .split(/[、,，]/)
    .map((name) => name.trim())
    .filter(Boolean)
}

function syncAssignmentFields() {
  const matchedOwner =
    props.users.find((user) => user.id === form.owner_id) ||
    props.users.find((user) => user.display_name === form.owner_name)
  ownerId.value = matchedOwner?.id || form.owner_id || ""

  const names = splitNames(form.collaborator_names)
  const matchedCollaborators = props.users.filter((user) => names.includes(user.display_name))
  collaboratorIds.value = matchedCollaborators.map((user) => user.id)
  unknownCollaboratorNames.value = names.filter(
    (name) => !matchedCollaborators.some((user) => user.display_name === name),
  )
}

watch(
  () => [props.open, props.task, props.ownerName, props.defaultOwnerId] as const,
  () => {
    Object.assign(form, cloneTask(props.task))
    syncAssignmentFields()
  },
  { immediate: true },
)

watch(() => props.users, syncAssignmentFields, { deep: true })

watch(ownerId, (value) => {
  form.owner_id = value || null
  const selected = props.users.find((user) => user.id === value)
  if (selected) form.owner_name = selected.display_name
  else if (!value) form.owner_name = ""
})

watch(
  collaboratorIds,
  (values) => {
    const names = props.users
      .filter((user) => values.includes(user.id))
      .map((user) => user.display_name)
    form.collaborator_names = [...unknownCollaboratorNames.value, ...names].join("、")
  },
  { deep: true },
)

function normalizeProgress(value: number | null) {
  const number = Number(value)
  if (!Number.isFinite(number)) return 0
  return Math.min(100, Math.max(0, Math.round(number / 5) * 5))
}

function submit(action: "close" | "next") {
  if (!reportDraftValidity(formElement.value)) return
  const customerName = props.includeCustomer ? form.customer_name.trim() : ""
  const taskName = form.task_name.trim()
  const workContent = form.work_content.trim()
  const outputDescription = form.output_description.trim()
  const plannedCompletionDate = String(form.planned_completion_date || "").trim()

  Object.assign(form, {
    customer_name: customerName,
    task_name: taskName,
    work_content: workContent,
    output_description: outputDescription,
    planned_completion_date: plannedCompletionDate,
    progress_percent: normalizeProgress(form.progress_percent),
  })
  emit("save", {
    ...form,
    attachments: form.attachments.map((attachment) => ({ ...attachment })),
  }, action)
}

function openFilePicker() {
  fileInputRef.value?.click()
}

async function handleFiles(event: Event) {
  const input = event.target as HTMLInputElement
  const files = Array.from(input.files || [])
  input.value = ""
  attachmentBusy.value = true
  try {
    for (const file of files) {
      const duplicate = form.attachments.some(
        (attachment) => attachment.file_name === file.name && attachment.file_size === file.size,
      )
      if (!duplicate) {
        const uploaded = await uploadPendingReportAttachment(file)
        form.attachments.push({ ...uploaded })
      }
    }
    if (files.length) noticeStore.reminder("附件上传成功。")
  } catch (error) {
    noticeStore.warning(error instanceof Error ? error.message : "附件上传失败。")
  } finally {
    attachmentBusy.value = false
  }
}

async function removeAttachment(index: number) {
  const attachment = form.attachments[index]
  if (!attachment?.id) return
  try {
    await deleteReportAttachment(attachment.id)
    form.attachments.splice(index, 1)
    noticeStore.reminder("附件已删除。")
  } catch (error) {
    noticeStore.warning(error instanceof Error ? error.message : "附件删除失败。")
  }
}

return { form, ownerId, collaboratorIds, fileInputRef, attachmentBusy, formElement, customerSelect, normalizeProgress, submit, openFilePicker, handleFiles, removeAttachment }
}
