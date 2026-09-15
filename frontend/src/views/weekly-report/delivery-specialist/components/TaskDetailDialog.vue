<script setup lang="ts">
import { computed } from "vue"

import BaseDialog from "@/components/overlay/BaseDialog.vue"
import { formatDateTime } from "@/utils/date"
import {
  deliveryTaskFieldDefinitions,
  type DeliveryTaskColumn,
  type DeliveryTaskDraft,
} from "@/features/weekly-report/delivery-specialist/types"

const props = defineProps<{
  open: boolean
  task: DeliveryTaskDraft | null
  mode: "monthly" | "weekly"
}>()

const emit = defineEmits<{ close: [] }>()

const monthlyColumns = new Set<DeliveryTaskColumn>([
  "customer_name",
  "task_name",
  "work_content",
  "planned_completion_date",
  "owner_name",
])

const fields = computed(() =>
  deliveryTaskFieldDefinitions.filter((field) =>
    props.mode === "weekly" || monthlyColumns.has(field.code),
  ),
)

const wideFields = new Set<DeliveryTaskColumn>([
  "work_content",
  "output_description",
  "progress_text",
  "delay_reason",
  "document_links",
])

function displayValue(task: DeliveryTaskDraft, column: DeliveryTaskColumn) {
  if (column === "customer_name") return task.customer_name || "未填写"
  if (column === "progress_percent") return `${Math.round(Number(task.progress_percent ?? 0))}%`
  if (column === "on_time_status") {
    return ({
      in_progress: "进行中",
      on_time: "是，按计划完成",
      late: "否，已延期完成",
      overdue: "否，已逾期未完成",
      not_applicable: "不适用",
    } as Record<string, string>)[task[column]] || "—"
  }
  return task[column] || "—"
}
</script>

<template>
  <BaseDialog :open="open" title="任务详情" width="900px" @close="emit('close')">
    <div v-if="task" class="task-detail">
      <div class="task-detail__grid">
        <div
          v-for="field in fields"
          :key="field.code"
          class="task-detail__item"
          :class="{ 'task-detail__item--wide': wideFields.has(field.code) }"
        >
          <span class="task-detail__label">{{ field.label }}</span>
          <p class="task-detail__value">{{ displayValue(task, field.code) }}</p>
        </div>
        <div class="task-detail__item">
          <span class="task-detail__label">更新时间</span>
          <p class="task-detail__value">{{ formatDateTime(task.updated_at) }}</p>
        </div>
      </div>

      <div v-if="task.attachments.length" class="task-detail__attachments">
        <span class="task-detail__label">附件</span>
        <ul>
          <li v-for="(attachment, index) in task.attachments" :key="`${attachment.file_name}-${index}`">
            <a v-if="attachment.file_url" :href="attachment.file_url" target="_blank" rel="noreferrer">{{ attachment.file_name }}</a>
            <span v-else>{{ attachment.file_name }}</span>
            <small>{{ attachment.description || (attachment.file ? "待保存后上传" : "已上传") }}</small>
          </li>
        </ul>
      </div>
    </div>
    <template #actions>
      <button class="primary-button" type="button" @click="emit('close')">关闭</button>
    </template>
  </BaseDialog>
</template>

<style scoped src="./TaskDetailDialog.css"></style>
