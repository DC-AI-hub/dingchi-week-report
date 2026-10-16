<script setup lang="ts">
import { clearFieldValidity } from "@/utils/form-validation"
import AttachmentDownloadLink from "@/components/file/AttachmentDownloadLink.vue"
import PersonSelect from "@/features/directory/components/PersonSelect.vue"
import DeliveryCustomerSelect from "@/features/weekly-report/components/DeliveryCustomerSelect.vue"
import BaseDialog from "@/components/overlay/BaseDialog.vue"
import type { DirectoryUserOption } from "@/features/directory/types"
import type { DeliveryTaskDraft } from "@/features/weekly-report/delivery-specialist/types"
import { useFunctionalTaskForm } from "../composables/useFunctionalTaskForm"
const props = withDefaults(
  defineProps<{
    open: boolean
    task: DeliveryTaskDraft | null
    mode: "monthly" | "weekly"
    defaultOwnerId?: string; ownerName?: string
    users?: DirectoryUserOption[]
    includeCustomer?: boolean
    readonly?: boolean
    reportId?: string
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

const { form, ownerId, collaboratorIds, fileInputRef, attachmentBusy, formElement, customerSelect, normalizeProgress, submit, openFilePicker, handleFiles, removeAttachment } = useFunctionalTaskForm(props, emit)
</script>

<template>
  <BaseDialog :open="open" :title="readonly ? '任务详情' : (task ? '编辑任务' : '新增任务')" width="980px" height="88vh" @close="emit('close')">
    <form ref="formElement" novalidate @input.capture="clearFieldValidity" @change.capture="clearFieldValidity" class="task-editor" @submit.prevent="submit('close')">
      <div class="task-editor__row">
        <div v-if="includeCustomer" class="task-editor__field task-editor__customer-field">
          <label for="task-customer-name"><span class="task-editor__label">客户<span v-if="!readonly" class="required-mark" aria-hidden="true">*</span></span></label>
          <DeliveryCustomerSelect ref="customerSelect" v-model="form.customer_name" :readonly="readonly" required />
        </div>
        <label
          class="task-editor__field task-editor__field--full"
        >
          <span class="task-editor__label">工作任务<span v-if="!readonly" class="required-mark" aria-hidden="true">*</span></span>
          <textarea v-if="includeCustomer" v-model.trim="form.task_name" rows="4" required :readonly="readonly" />
          <input v-else v-model.trim="form.task_name" required :readonly="readonly" />
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
            <option value="pending">待完成</option>
            <option value="in_progress">进行中</option>
            <option value="on_time">是，按计划完成</option>
            <option value="late">否，已延期完成</option>
            <option value="overdue">否，已逾期未完成</option>
            <option value="completed">已完成</option>
            <option value="not_applicable">不适用</option>
          </select>
        </label>
      </div>

      <div class="task-editor__row">
        <label class="task-editor__field">
          责任人
          <PersonSelect v-model="ownerId" :users="users || []" :disabled="readonly" aria-label="选择责任人" placeholder="输入文字筛选" />
        </label>
        <label class="task-editor__field">
          协作人
          <PersonSelect
            v-model="collaboratorIds"
            :users="users || []"
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
          <button class="ghost-button" type="button" :disabled="attachmentBusy" @click="openFilePicker">{{ attachmentBusy ? "上传中" : "上传附件" }}</button>
          <input ref="fileInputRef" class="task-editor__file-input" type="file" multiple @change="handleFiles" />
          <span>可选择多个文件</span>
        </div>
        <div v-if="form.attachments.length" class="task-editor__attachment-list">
          <div v-for="(attachment, index) in form.attachments" :key="`${attachment.file_name}-${index}`" class="task-editor__attachment-item">
            <div class="task-editor__attachment-main">
              <AttachmentDownloadLink :attachment-id="attachment.id" :file-name="attachment.file_name" />
              <small>已上传</small>
            </div>
            <input v-model.trim="attachment.description" maxlength="500" placeholder="附件说明（可选）" :readonly="readonly" />
            <button v-if="!readonly" class="danger-action-button" type="button" @click="removeAttachment(index)">删除</button>
          </div>
        </div>
      </div>

      <template v-if="mode === 'weekly'">
        <label class="task-editor__field task-editor__field--wide">工作进展（截至月日）<textarea v-model.trim="form.progress_text" rows="4" :readonly="readonly" /></label>
        <label class="task-editor__field task-editor__field--wide">进度缓慢原因说明<textarea v-model.trim="form.delay_reason" rows="3" :readonly="readonly" /></label>
      </template>
    </form>
    <template v-if="readonly" #actions>
      <button class="primary-button" type="button" @click="emit('close')">关闭</button>
    </template>
    <template v-else #actions>
      <button class="ghost-button" type="button" @click="emit('close')">取消</button>
      <button class="ghost-button" type="button" @click="submit('close')">确定</button>
      <button class="ghost-button" type="button" @click="submit('next')">确定并继续添加</button>
    </template>
  </BaseDialog>
</template>

<style scoped src="./TaskEditorDialog.css"></style>
