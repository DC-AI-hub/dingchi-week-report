<script setup lang="ts">
import FullscreenPanel from "@/components/layout/FullscreenPanel.vue"
import { formatDateTime } from "@/utils/date"
import ExamplePreviewButton from "@/components/feedback/ExamplePreviewButton.vue"
import BaseDialog from "@/components/overlay/BaseDialog.vue"
import { deliveryWeeklyTaskSample, deliveryWeeklyTaskSampleFields } from "@/features/weekly-report/delivery-specialist/samples"
import type { DeliveryTaskDraft } from "@/features/weekly-report/delivery-specialist/types"
import ReportPagination from "@/views/weekly-report/components/ReportPagination.vue"
import { useTaskCollection, type DeliveryTaskCollectionProps } from "@/features/weekly-report/composables/useDeliveryTaskCollection"
import TaskEditorDialog from "./TaskEditorDialog.vue"
import { useFunctionalTaskEditor } from "../composables/useFunctionalTaskEditor"
const props = withDefaults(defineProps<DeliveryTaskCollectionProps>(), {
  includeCustomer: true,
  sampleContent: deliveryWeeklyTaskSample,
  sampleFields: () => deliveryWeeklyTaskSampleFields,
  columnPreferenceKey: "delivery_specialist_v1",
})
const emit = defineEmits<{ "update:tasks": [tasks: DeliveryTaskDraft[]] }>()
const { filteredTaskEntries, columnsOpen, users, customerFilter, plannedDateFilter, taskPage, taskPageSize, showCustomer, editableDelivery, customerOptions, selectedColumns, availableFields, selectedFields, totalTaskPages, pagedTaskEntries, removeTask, customerRowspan, displayValue } = useTaskCollection(props, emit)
const { editorOpen, editorKey, editingTask, detailOpen, detailTask, addTask, editTask, saveTask, openTaskDetail } = useFunctionalTaskEditor(props, emit)
</script>

<template>
  <FullscreenPanel :title="title" class="dashboard-card task-section">
    <template #actions>
        <ExamplePreviewButton
          :content="sampleContent"
          :fields="sampleFields"
          panel-title="本周工作任务填写样例"
        />
        <button class="ghost-button" type="button" @click="columnsOpen = true">选择展示字段</button>
        <button class="primary-button" type="button" @click="addTask">新增任务</button>
    </template>
    <div class="task-section__filters">
      <select v-if="showCustomer && !editableDelivery" v-model="customerFilter" aria-label="按客户筛选">
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
  </FullscreenPanel>

  <TaskEditorDialog :key="editorKey" :open="editorOpen" :task="editingTask" :mode="mode" :default-owner-id="defaultOwnerId" :owner-name="ownerName" :users="users" :include-customer="showCustomer" :report-id="reportId" @close="editorOpen = false" @save="saveTask" />
  <TaskEditorDialog
    :open="detailOpen"
    :task="detailTask"
    :mode="mode"
    :default-owner-id="defaultOwnerId" :owner-name="ownerName"
    :users="users"
    :include-customer="showCustomer"
    :readonly="true"
    :report-id="reportId"
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
