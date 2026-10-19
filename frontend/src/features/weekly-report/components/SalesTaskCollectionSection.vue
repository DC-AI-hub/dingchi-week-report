<script setup lang="ts">
import FullscreenPanel from "@/components/layout/FullscreenPanel.vue"
import ExamplePreviewButton from "@/components/feedback/ExamplePreviewButton.vue"
import BaseDialog from "@/components/overlay/BaseDialog.vue"
import PaginationBar from "@/components/navigation/PaginationBar.vue"
import EditableTaskTable from "@/features/weekly-report/components/EditableTaskTable.vue"
import TaskQuickFillDialog from "@/features/weekly-report/components/TaskQuickFillDialog.vue"
import { computed } from "vue"
import { itoSalesWeeklyTaskSample, itoSalesWeeklyTaskSampleFields } from "@/features/weekly-report/ito-sales/samples"
import { innovationSalesWeeklyTaskSample, innovationSalesWeeklyTaskSampleFields } from "@/features/weekly-report/innovation-sales/samples"
import type { ItoSalesTaskDraft } from "@/features/weekly-report/ito-sales/types"
import { useSalesTaskCollection, type SalesCollectionProps } from "@/features/weekly-report/sales/useSalesTaskCollection"
const props = defineProps<SalesCollectionProps>()
const emit = defineEmits<{ "update:tasks": [tasks: ItoSalesTaskDraft[]] }>()
const { templates, quickFillOpen, columnsOpen, users, customerFilter, plannedDateFilter, taskPage, pageSize, selectedColumns, customerOptions, filteredTaskEntries, totalPages, pagedTaskEntries, availableFields, selectedFields, addTemplates, insertTask, patchTask, removeTask } = useSalesTaskCollection(props, emit)
const sampleContent = computed(() => props.templateCode === "innovation_sales_v1" ? innovationSalesWeeklyTaskSample : itoSalesWeeklyTaskSample)
const sampleFields = computed(() => props.templateCode === "innovation_sales_v1" ? innovationSalesWeeklyTaskSampleFields : itoSalesWeeklyTaskSampleFields)
</script>
<template>
  <FullscreenPanel :title="title" class="dashboard-card task-section">
    <template #actions>
      <ExamplePreviewButton :content="sampleContent" :fields="sampleFields" panel-title="本周工作任务填写样例" />
      <button class="ghost-button" type="button" @click="columnsOpen = true">选择展示字段</button>
      <button class="primary-button" type="button" @click="quickFillOpen = true">新增任务</button>
    </template>
    <div class="task-section__filters">
      <select v-model="customerFilter" aria-label="按客户筛选"><option value="">全部客户</option><option v-for="dimension in customerOptions" :key="dimension" :value="dimension">{{ dimension }}</option></select>
      <label><span>计划完成时间</span><input v-model="plannedDateFilter" type="date" aria-label="按计划完成时间筛选" /></label>
    </div>
    <EditableTaskTable sales-mode scope-field="customer_name" :total-tasks="tasks.length" @add-blank="insertTask(-1)" :entries="pagedTaskEntries" :fields="selectedFields" :users="users" :offset="(taskPage - 1) * pageSize" :templates="templates" @patch="patchTask" @remove="removeTask" @insert="insertTask" />
    <PaginationBar :page="taskPage" :page-size="pageSize" :total="filteredTaskEntries.length" :total-pages="totalPages" @change="taskPage = $event" />
  </FullscreenPanel>
  <TaskQuickFillDialog :open="quickFillOpen" sales :templates="templates" @close="quickFillOpen = false" @confirm="addTemplates" />
  <BaseDialog :open="columnsOpen" title="选择展示字段" width="640px" @close="columnsOpen = false">
    <div class="column-options"><label v-for="field in availableFields" :key="field.code"><input v-model="selectedColumns" :value="field.code" type="checkbox" />{{ field.label }}</label></div>
    <template #actions><button class="primary-button" type="button" @click="columnsOpen = false">确定</button></template>
  </BaseDialog>
</template>
<style scoped src="./SalesTaskCollectionSection.css"></style>
