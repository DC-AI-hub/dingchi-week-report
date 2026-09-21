<script setup lang="ts">
import { computed, ref, watch } from "vue"

import BaseDialog from "@/components/overlay/BaseDialog.vue"
import {
  formatReportTaskField,
  normalizeReportTaskFields,
  reportTaskStatusLabel,
  reportTaskUpdatedAt,
} from "@/features/weekly-report/task-fields"
import type {
  ReportAttachment,
  ReportItem,
  ReportTemplateField,
} from "@/features/weekly-report/types"

import ReportPagination from "./ReportPagination.vue"
import ReportTaskDetailDialog from "./ReportTaskDetailDialog.vue"

const props = withDefaults(
  defineProps<{
    items: ReportItem[]
    fields?: ReportTemplateField[] | null
    attachments?: ReportAttachment[]
    showColumnsButton?: boolean
  }>(),
  { showColumnsButton: true },
)

const columnsOpen = ref(false)
const selectedCodes = ref<string[]>([])
const detailOpen = ref(false)
const detailItem = ref<ReportItem | null>(null)
const page = ref(1)
const pageSize = 10

const availableFields = computed(() => normalizeReportTaskFields(props.fields))
const primaryField = computed<ReportTemplateField | null>(() => {
  const source = props.fields || []
  const dimension = source.find((field) => field.field_code === "dimension")
  const customer = source.find((field) => field.field_code === "customer_name")

  // 模板字段配置是列表布局的唯一依据。职能组模板不配置客户/维度时，
  // 不再渲染一个空的主字段列；否则表格会留下与客户列同宽的空白区域。
  if (source.length) return dimension || customer || null

  // 兼容接口暂未返回字段配置的旧数据：招聘报告仍使用维度，其他报告
  // 根据任务数据判断是否存在客户主字段。
  const looksLikeRecruitment = !dimension
    && props.items.length > 0
    && props.items.every((item) => !item.customer_name_snapshot)
    && props.items.some((item) =>
      /recruitment|recruit|招聘/i.test(
        `${item.section_code || ""} ${item.section_name_snapshot || ""}`,
      ),
    )
  if (looksLikeRecruitment) {
    return { field_code: "dimension", label: "维度", sort_order: 1, default_visible: true }
  }
  if (props.items.some((item) => Boolean(item.customer_name_snapshot))) {
    return { field_code: "customer_name", label: "客户", sort_order: 1, default_visible: true }
  }
  return null
})
const displayItems = computed(() =>
  props.items
    .map((item, index) => ({ item, index }))
    .sort(
      (left, right) =>
        primaryValue(left.item).localeCompare(
          primaryValue(right.item),
          "zh-CN",
        ) ||
        left.item.sort_order - right.item.sort_order ||
        left.index - right.index,
    )
    .map(({ item }) => item),
)
const totalPages = computed(() => Math.max(1, Math.ceil(displayItems.value.length / pageSize)))
const pagedItems = computed(() => {
  const start = (page.value - 1) * pageSize
  return displayItems.value.slice(start, start + pageSize)
})
const selectedFields = computed(() => {
  const selected = new Set(selectedCodes.value)
  return availableFields.value.filter((field) => selected.has(field.field_code))
})

watch(
  availableFields,
  (fields) => {
    const available = new Set(fields.map((field) => field.field_code))
    selectedCodes.value = selectedCodes.value.filter((code) => available.has(code))
  },
  { immediate: true },
)

watch(totalPages, (value) => {
  if (page.value > value) page.value = value
}, { immediate: true })

function customerRowspan(index: number): number {
  if (!primaryField.value) return 1
  const current = primaryValue(pagedItems.value[index])
  if (index > 0 && primaryValue(pagedItems.value[index - 1]) === current) return 0

  let rowspan = 1
  while (
    index + rowspan < pagedItems.value.length
    && primaryValue(pagedItems.value[index + rowspan]) === current
  ) {
    rowspan += 1
  }
  return rowspan
}

function primaryValue(item: ReportItem | undefined): string {
  if (!item || !primaryField.value) return ""
  if (primaryField.value.field_code === "dimension") {
    return formatReportTaskField(item, "dimension")
  }
  return item.customer_name_snapshot || "—"
}

function statusClass(value: string | null | undefined): string {
  return value || "unknown"
}

function openTask(item: ReportItem) {
  detailItem.value = item
  detailOpen.value = true
}

function itemAttachments(item: ReportItem): ReportAttachment[] {
  return (props.attachments || []).filter((attachment) => attachment.relation_sub_id === item.id)
}

function openColumns() {
  columnsOpen.value = true
}

defineExpose({ openColumns })
</script>

<template>
  <div class="report-task-table">
    <div v-if="showColumnsButton" class="report-task-table__toolbar">
      <button class="ghost-button" type="button" @click="columnsOpen = true">选择展示字段</button>
    </div>

    <div class="report-task-table-wrap">
      <table class="report-task-table__grid">
        <thead>
          <tr>
            <th class="serial-col">序号</th>
            <th v-if="primaryField" class="customer-col">{{ primaryField.label }}</th>
            <th
              class="task-col"
              :class="{ 'task-col--without-primary': !primaryField }"
            >工作任务</th>
            <th v-for="field in selectedFields" :key="field.field_code" class="dynamic-col">
              {{ field.label }}
            </th>
            <th class="status-col">状态</th>
            <th class="updated-col">更新时间</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(item, index) in pagedItems" :key="item.id || `${item.task_code}-${index}`">
            <tr>
              <td class="serial-col">{{ (page - 1) * pageSize + index + 1 }}</td>
              <td
                v-if="primaryField && customerRowspan(index) > 0"
                class="customer-col customer-cell"
                :rowspan="customerRowspan(index)"
              >
                <span class="cell-text" :title="primaryValue(item)">
                  {{ primaryValue(item) }}
                </span>
              </td>
              <td
                class="task-col task-cell"
                :class="{ 'task-col--without-primary': !primaryField }"
              >
                <button
                  class="task-link"
                  type="button"
                  :title="item.task_name_snapshot || item.task_code"
                  @click="openTask(item)"
                >
                  {{ item.task_name_snapshot || item.task_code || "—" }}
                </button>
              </td>
              <td v-for="field in selectedFields" :key="field.field_code" class="dynamic-col">
                <span
                  class="cell-text"
                  :title="formatReportTaskField(item, field.field_code)"
                >
                  {{ formatReportTaskField(item, field.field_code) }}
                </span>
              </td>
              <td class="status-col">
                <span
                  class="status-pill"
                  :class="`status-pill--${statusClass(item.on_time_status)}`"
                >
                  {{ reportTaskStatusLabel(item.on_time_status) }}
                </span>
              </td>
              <td class="updated-col date-cell">
                {{ reportTaskUpdatedAt(item) }}
              </td>
            </tr>
          </template>
          <tr v-if="!pagedItems.length">
            <td :colspan="selectedFields.length + (primaryField ? 5 : 4)" class="empty-cell">暂无工作任务</td>
          </tr>
        </tbody>
      </table>
    </div>
    <ReportPagination
      :page="page"
      :page-size="pageSize"
      :total="displayItems.length"
      :total-pages="totalPages"
      @change="page = $event"
    />
  </div>

  <BaseDialog
    :open="columnsOpen"
    title="选择展示字段"
    width="640px"
    @close="columnsOpen = false"
  >
    <div class="column-options">
      <label v-for="field in availableFields" :key="field.field_code">
        <input v-model="selectedCodes" :value="field.field_code" type="checkbox" />
        <span>{{ field.label }}</span>
      </label>
      <p v-if="!availableFields.length" class="column-options__empty">暂无可选字段</p>
    </div>
    <template #actions>
      <button class="primary-button" type="button" @click="columnsOpen = false">确定</button>
    </template>
  </BaseDialog>

  <ReportTaskDetailDialog
    :open="detailOpen"
    :item="detailItem"
    :fields="props.fields"
    :attachments="detailItem ? itemAttachments(detailItem) : []"
    @close="detailOpen = false"
  />
</template>

<style scoped src="./ReportTaskTable.css"></style>
