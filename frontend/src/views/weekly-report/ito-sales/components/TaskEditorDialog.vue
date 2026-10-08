<script setup lang="ts">
import NoticeBridge from "@/components/feedback/NoticeBridge.vue"
import AttachmentDownloadLink from "@/components/file/AttachmentDownloadLink.vue"
import { computed, reactive, ref, watch } from "vue"

import SearchableSelect from "@/components/form/SearchableSelect.vue"
import BaseDialog from "@/components/overlay/BaseDialog.vue"
import type { DirectoryUserOption } from "@/features/directory/types"
import { useNoticeStore } from "@/app/stores/notice"
import { deleteReportAttachment, uploadPendingReportAttachment } from "@/features/weekly-report/api"
import {
  emptyItoSalesTask,
  type ItoSalesTaskAttachment,
  type ItoSalesTaskDraft,
} from "@/features/weekly-report/ito-sales/types"
import { useItoSalesCustomerHistory } from "@/features/weekly-report/ito-sales/useCustomerHistory"

const props = withDefaults(
  defineProps<{
    open: boolean
    task: ItoSalesTaskDraft | null
    ownerName?: string
    users?: DirectoryUserOption[]
    readonly?: boolean
  }>(),
  { ownerName: "", users: () => [], readonly: false },
)
const emit = defineEmits<{ close: []; save: [task: ItoSalesTaskDraft, action: "close" | "next"] }>()
const form = reactive<ItoSalesTaskDraft>(emptyItoSalesTask())
const ownerId = ref("")
const collaboratorIds = ref<string[]>([])
const unknownCollaboratorNames = ref<string[]>([])
const fileInputRef = ref<HTMLInputElement | null>(null)
const attachmentBusy = ref(false)
const noticeStore = useNoticeStore()
const customerHistoryOpen = ref(false)
const validationMessage = ref("")
const { customerHistory, refresh: refreshCustomerHistory, remember: rememberCustomer } = useItoSalesCustomerHistory()

const userOptions = computed(() => props.users.map((user) => ({
  value: user.id,
  label: user.display_name,
  description: [user.employee_no, user.username].filter(Boolean).join(" · "),
})))
const filteredCustomerHistory = computed(() => {
  const keyword = form.customer_name.trim().toLocaleLowerCase()
  return customerHistory.value.filter((name) => !keyword || name.toLocaleLowerCase().includes(keyword)).slice(0, 10)
})
const completionRate = computed(() => Math.round(((Number(form.progress_percent) || 0) + (Number(form.quality_percent) || 0)) / 2))

function cloneTask(task: ItoSalesTaskDraft | null) {
  const next = emptyItoSalesTask(props.ownerName)
  return task ? { ...next, ...task, attachments: (task.attachments || []).map((attachment) => ({ ...attachment })) } : next
}

function splitNames(value: string) { return value.split(/[、,，]/).map((name) => name.trim()).filter(Boolean) }

function syncAssignmentFields() {
  const owner = props.users.find((user) => user.id === form.owner_id) || props.users.find((user) => user.display_name === form.owner_name)
  ownerId.value = owner?.id || form.owner_id || ""
  const names = splitNames(form.collaborator_names)
  const matched = props.users.filter((user) => names.includes(user.display_name))
  collaboratorIds.value = matched.map((user) => user.id)
  unknownCollaboratorNames.value = names.filter((name) => !matched.some((user) => user.display_name === name))
}

watch(() => [props.open, props.task, props.ownerName] as const, () => {
  Object.assign(form, cloneTask(props.task))
  validationMessage.value = ""
  syncAssignmentFields()
}, { immediate: true })
watch(() => props.users, syncAssignmentFields, { deep: true })
watch(() => [form.customer_name, form.task_name], () => { validationMessage.value = "" })
watch(ownerId, (value) => {
  form.owner_id = value || null
  const user = props.users.find((item) => item.id === value)
  if (user) form.owner_name = user.display_name
  else if (!value) form.owner_name = ""
})
watch(collaboratorIds, (values) => {
  form.collaborator_names = [...unknownCollaboratorNames.value, ...props.users.filter((user) => values.includes(user.id)).map((user) => user.display_name)].join("、")
}, { deep: true })

function normalizePercent(value: number | null) {
  const number = Number(value)
  return Number.isFinite(number) ? Math.min(100, Math.max(0, Math.round(number / 5) * 5)) : 0
}

function localTimestamp() {
  const now = new Date()
  const pad = (value: number) => String(value).padStart(2, "0")
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`
}

function submit(action: "close" | "next") {
  const customer = form.customer_name.trim()
  const task = form.task_name.trim()
  const workContent = form.work_content.trim()
  const outputDescription = form.output_description.trim()
  const plannedCompletionDate = String(form.planned_completion_date || "").trim()
  const missingFields = [
    !customer && "客户",
    !task && "工作任务",
    !workContent && "主要工作指引",
    !outputDescription && "输出成果",
    !plannedCompletionDate && "计划完成时间",
  ].filter(Boolean)
  if (missingFields.length) {
    validationMessage.value = `${missingFields.join("、")}不能为空。`
    return
  }
  const progress = normalizePercent(form.progress_percent)
  const quality = normalizePercent(form.quality_percent)
  Object.assign(form, {
    customer_name: customer,
    task_name: task,
    work_content: workContent,
    output_description: outputDescription,
    planned_completion_date: plannedCompletionDate,
    progress_percent: progress,
    quality_percent: quality,
    completion_rate: Math.round((progress + quality) / 2),
    updated_at: localTimestamp(),
  })
  rememberCustomer(customer)
  customerHistoryOpen.value = false
  emit("save", { ...form, attachments: form.attachments.map((attachment) => ({ ...attachment })) }, action)
}

function openCustomerHistory() { refreshCustomerHistory(); customerHistoryOpen.value = true }
function scheduleCustomerHistoryClose() { globalThis.setTimeout(() => { customerHistoryOpen.value = false }, 120) }
function selectCustomer(value: string) { form.customer_name = value; customerHistoryOpen.value = false }
function openFilePicker() { fileInputRef.value?.click() }

async function handleFiles(event: Event) {
  const input = event.target as HTMLInputElement
  const files = Array.from(input.files || [])
  input.value = ""
  attachmentBusy.value = true
  try {
    for (const file of files) {
      if (!form.attachments.some((attachment) => attachment.file_name === file.name && attachment.file_size === file.size)) {
        form.attachments.push({ ...(await uploadPendingReportAttachment(file)) })
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
</script>

<template>
  <BaseDialog :open="open" :title="readonly ? '任务详情' : (task ? '编辑任务' : '新增任务')" width="1020px" height="88vh" @close="emit('close')">
    <form class="task-editor" @submit.prevent="submit('close')">
      <div class="task-editor__row">
        <div class="task-editor__field task-editor__customer-field">
          <label for="ito-task-customer"><span class="task-editor__label">客户<span v-if="!readonly" class="required-mark" aria-hidden="true">*</span></span></label>
          <div class="customer-input-wrap">
            <input id="ito-task-customer" v-model.trim="form.customer_name" maxlength="255" required autocomplete="off" aria-autocomplete="list" aria-controls="ito-customer-history" :readonly="readonly" :aria-expanded="customerHistoryOpen" @focus="!readonly && openCustomerHistory()" @click="!readonly && openCustomerHistory()" @blur="scheduleCustomerHistoryClose" />
            <div v-if="customerHistoryOpen && filteredCustomerHistory.length" id="ito-customer-history" class="customer-history" role="listbox">
              <button v-for="customer in filteredCustomerHistory" :key="customer" class="customer-history__option" type="button" role="option" @mousedown.prevent="selectCustomer(customer)">{{ customer }}</button>
            </div>
          </div>
        </div>
        <label class="task-editor__field"><span class="task-editor__label">工作任务<span v-if="!readonly" class="required-mark" aria-hidden="true">*</span></span><input v-model.trim="form.task_name" maxlength="255" required :readonly="readonly" /></label>
      </div>
      <label class="task-editor__field task-editor__field--wide"><span class="task-editor__label">主要工作指引<span v-if="!readonly" class="required-mark" aria-hidden="true">*</span></span><textarea v-model.trim="form.work_content" rows="5" required :readonly="readonly" /></label>
      <label class="task-editor__field task-editor__field--wide"><span class="task-editor__label">输出成果<span v-if="!readonly" class="required-mark" aria-hidden="true">*</span></span><textarea v-model.trim="form.output_description" rows="5" required :readonly="readonly" /></label>
      <div class="task-editor__row"><label class="task-editor__field"><span class="task-editor__label">计划完成时间<span v-if="!readonly" class="required-mark" aria-hidden="true">*</span></span><input v-model="form.planned_completion_date" type="date" required :disabled="readonly" /></label><label class="task-editor__field">实际完成时间<input v-model="form.actual_completion_date" type="date" :disabled="readonly" /></label></div>
      <label class="task-editor__field task-editor__field--wide">工作进展（截至月日）<textarea v-model.trim="form.progress_text" rows="4" :readonly="readonly" /></label>
      <div class="task-editor__row"><label class="task-editor__field">完成进度（百分比）<input v-model.number="form.progress_percent" min="0" max="100" step="5" type="number" :readonly="readonly" @change="form.progress_percent = normalizePercent(form.progress_percent)" /></label><label class="task-editor__field">完成质量（百分比）<input v-model.number="form.quality_percent" min="0" max="100" step="5" type="number" :readonly="readonly" @change="form.quality_percent = normalizePercent(form.quality_percent)" /></label></div>
      <div class="task-editor__row"><label class="task-editor__field">月度工作完成率（完成进度*50%+完成质量*50%）<input :value="`${completionRate}%`" disabled /></label><label class="task-editor__field">是否在计划时间内完成<select v-model="form.on_time_status" :disabled="readonly"><option value="pending">待完成</option><option value="in_progress">进行中</option><option value="on_time">是，按计划完成</option><option value="late">否，已延期完成</option><option value="overdue">否，已逾期未完成</option><option value="completed">已完成</option><option value="not_applicable">不适用</option></select></label></div>
      <label class="task-editor__field task-editor__field--wide">进度缓慢原因说明<textarea v-model.trim="form.delay_reason" rows="4" :readonly="readonly" /></label>
      <div class="task-editor__row"><label class="task-editor__field">责任人<SearchableSelect v-model="ownerId" :options="userOptions" :disabled="readonly" aria-label="选择责任人" placeholder="输入文字筛选" /></label><label class="task-editor__field">协作人<SearchableSelect v-model="collaboratorIds" :options="userOptions" :multiple="true" :disabled="readonly" aria-label="选择协作人" placeholder="输入文字筛选" /></label></div>
      <div class="task-editor__field task-editor__field--wide task-editor__evidence">
        <label for="ito-task-links">相关文档链接或佐证材料</label>
        <textarea id="ito-task-links" v-model.trim="form.document_links" rows="3" :readonly="readonly" />
        <div v-if="!readonly" class="task-editor__attachment-toolbar"><button class="ghost-button" type="button" :disabled="attachmentBusy" @click="openFilePicker">{{ attachmentBusy ? "上传中" : "上传附件" }}</button><input ref="fileInputRef" class="task-editor__file-input" type="file" multiple @change="handleFiles" /></div>
        <div v-if="form.attachments.length" class="task-editor__attachment-list"><div v-for="(attachment, index) in form.attachments" :key="`${attachment.file_name}-${index}`" class="task-editor__attachment-item"><div class="task-editor__attachment-main"><AttachmentDownloadLink :attachment-id="attachment.id" :file-name="attachment.file_name" /><small>已上传</small></div><input v-model.trim="attachment.description" maxlength="500" placeholder="附件说明（可选）" :readonly="readonly" /><button v-if="!readonly" class="danger-action-button" type="button" @click="removeAttachment(index)">删除</button></div></div>
      </div>
      <NoticeBridge :warning-message="validationMessage" />
    </form>
    <template v-if="readonly" #actions><button class="primary-button" type="button" @click="emit('close')">关闭</button></template>
    <template v-else #actions><button class="ghost-button" type="button" @click="emit('close')">取消</button><button class="ghost-button" type="button" @click="submit('close')">保存&amp;关闭</button><button class="primary-button" type="button" @click="submit('next')">保存&amp;下一个</button></template>
  </BaseDialog>
</template>

<style scoped src="./TaskEditorDialog.css"></style>
