<script setup lang="ts">
import NoticeBridge from "@/components/feedback/NoticeBridge.vue"
import { computed, reactive, ref, watch } from "vue"

import SearchableSelect from "@/components/form/SearchableSelect.vue"
import BaseDialog from "@/components/overlay/BaseDialog.vue"
import type { DirectoryUserOption } from "@/features/directory/types"
import {
  emptyDeliveryTask,
  type DeliveryTaskAttachment,
  type DeliveryTaskDraft,
} from "@/features/weekly-report/delivery-specialist/types"
import { useCustomerHistory } from "@/features/weekly-report/delivery-specialist/useCustomerHistory"

const props = withDefaults(
  defineProps<{
    open: boolean
    task: DeliveryTaskDraft | null
    mode: "monthly" | "weekly"
    ownerName?: string
    users?: DirectoryUserOption[]
    includeCustomer?: boolean
    readonly?: boolean
  }>(),
  {
    ownerName: "",
    users: () => [],
    includeCustomer: true,
    readonly: false,
  },
)
const emit = defineEmits<{
  close: []
  save: [task: DeliveryTaskDraft, action: "close" | "next"]
}>()

const form = reactive<DeliveryTaskDraft>(emptyDeliveryTask())
const ownerId = ref("")
const collaboratorIds = ref<string[]>([])
const unknownCollaboratorNames = ref<string[]>([])
const fileInputRef = ref<HTMLInputElement | null>(null)
const customerHistoryOpen = ref(false)
const validationMessage = ref("")
const { customerHistory, refresh: refreshCustomerHistory, remember: rememberCustomer } = useCustomerHistory()

const userOptions = computed(() =>
  props.users.map((user) => ({
    value: user.id,
    label: user.display_name,
    description: [user.employee_no, user.username].filter(Boolean).join(" · "),
  })),
)

const filteredCustomerHistory = computed(() => {
  const keyword = form.customer_name.trim().toLocaleLowerCase()
  return customerHistory.value
    .filter((name) => !keyword || name.toLocaleLowerCase().includes(keyword))
    .slice(0, 10)
})

function cloneTask(task: DeliveryTaskDraft | null) {
  const next = emptyDeliveryTask(props.ownerName)
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
  () => [props.open, props.task, props.ownerName] as const,
  () => {
    Object.assign(form, cloneTask(props.task))
    validationMessage.value = ""
    syncAssignmentFields()
  },
  { immediate: true },
)

watch(() => props.users, syncAssignmentFields, { deep: true })

watch(
  () => [form.customer_name, form.task_name, form.work_content, form.output_description, form.planned_completion_date],
  () => {
    validationMessage.value = ""
  },
)

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

function openCustomerHistory() {
  refreshCustomerHistory()
  customerHistoryOpen.value = true
}

function scheduleCustomerHistoryClose() {
  globalThis.setTimeout(() => {
    customerHistoryOpen.value = false
  }, 120)
}

function selectCustomer(name: string) {
  form.customer_name = name
  customerHistoryOpen.value = false
}

function normalizeProgress(value: number | null) {
  const number = Number(value)
  if (!Number.isFinite(number)) return 0
  return Math.min(100, Math.max(0, Math.round(number / 5) * 5))
}

function submit(action: "close" | "next") {
  const customerName = props.includeCustomer ? form.customer_name.trim() : ""
  const taskName = form.task_name.trim()
  const workContent = form.work_content.trim()
  const outputDescription = form.output_description.trim()
  const plannedCompletionDate = String(form.planned_completion_date || "").trim()
  const missingFields = [
    props.includeCustomer && !customerName && "客户",
    !taskName && "工作任务",
    !workContent && "主要工作内容",
    !outputDescription && "输出成果",
    !plannedCompletionDate && "计划完成时间",
  ].filter(Boolean)
  if (missingFields.length) {
    validationMessage.value = `${missingFields.join("、")}不能为空。`
    return
  }
  Object.assign(form, {
    customer_name: customerName,
    task_name: taskName,
    work_content: workContent,
    output_description: outputDescription,
    planned_completion_date: plannedCompletionDate,
    progress_percent: normalizeProgress(form.progress_percent),
  })
  if (props.includeCustomer) rememberCustomer(customerName)
  customerHistoryOpen.value = false
  emit("save", {
    ...form,
    attachments: form.attachments.map((attachment) => ({ ...attachment })),
  }, action)
}

function openFilePicker() {
  fileInputRef.value?.click()
}

function handleFiles(event: Event) {
  const input = event.target as HTMLInputElement
  const files = Array.from(input.files || [])
  for (const file of files) {
    const duplicate = form.attachments.some(
      (attachment) => attachment.file_name === file.name && attachment.file?.size === file.size,
    )
    if (!duplicate) {
      const attachment: DeliveryTaskAttachment = {
        file,
        attachment_type: "weekly_report",
        file_name: file.name,
        description: "",
      }
      form.attachments.push(attachment)
    }
  }
  input.value = ""
}

function removeAttachment(index: number) {
  form.attachments.splice(index, 1)
}
</script>

<template>
  <BaseDialog :open="open" :title="readonly ? '任务详情' : (task ? '编辑任务' : '新增任务')" width="980px" height="88vh" @close="emit('close')">
    <form class="task-editor" @submit.prevent="submit('close')">
      <div class="task-editor__row">
        <div v-if="includeCustomer" class="task-editor__field task-editor__customer-field">
          <label for="task-customer-name"><span class="task-editor__label">客户<span v-if="!readonly" class="required-mark" aria-hidden="true">*</span></span></label>
          <div class="customer-input-wrap">
            <input
              id="task-customer-name"
              v-model.trim="form.customer_name"
              maxlength="255"
              required
              :readonly="readonly"
              autocomplete="off"
              aria-autocomplete="list"
              aria-controls="customer-history-list"
              :aria-expanded="customerHistoryOpen"
              @focus="!readonly && openCustomerHistory()"
              @click="!readonly && openCustomerHistory()"
              @blur="scheduleCustomerHistoryClose"
            />
            <div
              v-if="customerHistoryOpen && filteredCustomerHistory.length"
              id="customer-history-list"
              class="customer-history"
              role="listbox"
            >
              <button
                v-for="customer in filteredCustomerHistory"
                :key="customer"
                class="customer-history__option"
                type="button"
                role="option"
                @mousedown.prevent="selectCustomer(customer)"
              >
                {{ customer }}
              </button>
            </div>
          </div>
        </div>
        <label
          class="task-editor__field"
          :class="{ 'task-editor__field--full': !includeCustomer }"
        >
          <span class="task-editor__label">工作任务<span v-if="!readonly" class="required-mark" aria-hidden="true">*</span></span>
          <input v-model.trim="form.task_name" maxlength="255" required :readonly="readonly" />
        </label>
      </div>

      <label class="task-editor__field task-editor__field--wide">
        <span class="task-editor__label">主要工作内容<span v-if="!readonly" class="required-mark" aria-hidden="true">*</span></span>
        <textarea v-model.trim="form.work_content" rows="4" required :readonly="readonly" />
      </label>
      <label class="task-editor__field task-editor__field--wide">
        <span class="task-editor__label">输出成果<span v-if="!readonly" class="required-mark" aria-hidden="true">*</span></span>
        <textarea v-model.trim="form.output_description" rows="4" required :readonly="readonly" />
      </label>

      <div class="task-editor__row">
        <label class="task-editor__field"><span class="task-editor__label">计划完成时间<span v-if="!readonly" class="required-mark" aria-hidden="true">*</span></span><input v-model="form.planned_completion_date" type="date" required :disabled="readonly" /></label>
        <label v-if="mode === 'weekly'" class="task-editor__field">实际完成时间<input v-model="form.actual_completion_date" type="date" :disabled="readonly" /></label>
      </div>

      <div v-if="mode === 'weekly'" class="task-editor__row">
        <label class="task-editor__field">
          完成进度（百分比）
          <input v-model.number="form.progress_percent" min="0" max="100" step="5" type="number" :readonly="readonly" @change="form.progress_percent = normalizeProgress(form.progress_percent)" />
        </label>
        <label class="task-editor__field">
          是否在计划时间内完成
          <select v-model="form.on_time_status" :disabled="readonly">
            <option value="in_progress">进行中</option>
            <option value="on_time">是，按计划完成</option>
            <option value="late">否，已延期完成</option>
            <option value="overdue">否，已逾期未完成</option>
            <option value="not_applicable">不适用</option>
          </select>
        </label>
      </div>

      <div class="task-editor__row">
        <label class="task-editor__field">
          责任人
          <SearchableSelect v-model="ownerId" :options="userOptions" :disabled="readonly" aria-label="选择责任人" placeholder="输入文字筛选" />
        </label>
        <label class="task-editor__field">
          协作人
          <SearchableSelect
            v-model="collaboratorIds"
            :options="userOptions"
            :multiple="true"
            :disabled="readonly"
            aria-label="选择协作人"
            placeholder="输入文字筛选"
          />
        </label>
      </div>

      <div class="task-editor__field task-editor__field--wide task-editor__evidence">
        <label for="task-document-links">相关文档链接或佐证材料</label>
        <textarea id="task-document-links" v-model.trim="form.document_links" rows="3" :readonly="readonly" />
        <div v-if="!readonly" class="task-editor__attachment-toolbar">
          <button class="ghost-button" type="button" @click="openFilePicker">上传附件</button>
          <input ref="fileInputRef" class="task-editor__file-input" type="file" multiple @change="handleFiles" />
          <span>可选择多个文件</span>
        </div>
        <div v-if="form.attachments.length" class="task-editor__attachment-list">
          <div v-for="(attachment, index) in form.attachments" :key="`${attachment.file_name}-${index}`" class="task-editor__attachment-item">
            <div class="task-editor__attachment-main">
              <a v-if="attachment.file_url" :href="attachment.file_url" target="_blank" rel="noreferrer">{{ attachment.file_name }}</a>
              <span v-else>{{ attachment.file_name }}</span>
              <small>{{ attachment.file ? "待保存后上传" : "已上传" }}</small>
            </div>
            <input v-model.trim="attachment.description" maxlength="500" placeholder="附件说明（可选）" :readonly="readonly" />
            <button v-if="!readonly" class="link-button danger" type="button" @click="removeAttachment(index)">移除</button>
          </div>
        </div>
      </div>

      <template v-if="mode === 'weekly'">
        <label class="task-editor__field task-editor__field--wide">工作进展（截至月日）<textarea v-model.trim="form.progress_text" rows="4" :readonly="readonly" /></label>
        <label class="task-editor__field task-editor__field--wide">进度缓慢原因说明<textarea v-model.trim="form.delay_reason" rows="3" :readonly="readonly" /></label>
      </template>
      <NoticeBridge :warning-message="validationMessage" />
    </form>
    <template v-if="readonly" #actions>
      <button class="primary-button" type="button" @click="emit('close')">关闭</button>
    </template>
    <template v-else #actions>
      <button class="ghost-button" type="button" @click="emit('close')">取消</button>
      <button class="ghost-button" type="button" @click="submit('close')">保存&amp;关闭</button>
      <button class="primary-button" type="button" @click="submit('next')">保存&amp;下一个</button>
    </template>
  </BaseDialog>
</template>

<style scoped src="./TaskEditorDialog.css"></style>
