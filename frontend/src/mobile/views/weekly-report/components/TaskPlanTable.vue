<script setup lang="ts">
import type { ReportItem, TemplateItem } from "@/mobile/features/weekly-report/types"
import { formatDateTime } from "@/utils/date"

type TaskDraft = Partial<ReportItem> & { task_code: string }

defineProps<{
  items: TaskDraft[]
  templateTasks: TemplateItem[]
  readonly?: boolean
}>()

const statusLabels: Record<string, string> = {
  pending: "待完成",
  in_progress: "进行中",
  overdue: "延期",
  late: "延期完成",
  on_time: "按时完成",
  completed: "已完成",
  not_applicable: "不适用",
}

function isDelayed(item: TaskDraft) {
  return item.on_time_status === "overdue" || item.on_time_status === "late"
}
</script>

<template>
  <div class="task-table-wrap">
    <div class="mobile-task-cards">
      
      
        <article data-mobile-task-card v-for="(item, index) in items" :key="item.task_code || index">
          <div data-card-field data-label="工作任务" class="task-name">
            <strong>{{ item.task_name_snapshot || templateTasks.find((task) => task.task_code === item.task_code)?.label || item.task_code }}</strong>
            <small>{{ item.guidance_snapshot || templateTasks.find((task) => task.task_code === item.task_code)?.guidance }}</small>
          </div>
          <div data-card-field data-label="客户 / 项目">
            <input v-if="!readonly" v-model="item.customer_name_snapshot" type="text" placeholder="客户 / 项目" />
            <span v-else>{{ item.customer_name_snapshot || "—" }}</span>
          </div>
          <div data-card-field data-label="输出成果与进展" class="output-cell">
            <textarea v-if="!readonly" v-model="item.output_description" rows="2" placeholder="本周产出、关键进展、结果说明" />
            <span v-else>{{ item.output_description || item.progress_text || "—" }}</span>
            <textarea v-if="!readonly" v-model="item.progress_text" rows="2" placeholder="补充进展描述" />
          </div>
          <div data-card-field data-label="完成进度">
            <div v-if="!readonly" class="percent-control"><input v-model.number="item.progress_percent" type="number" min="0" max="100" step="1" /><span>%</span></div>
            <strong v-else>{{ item.progress_percent ?? 0 }}%</strong>
          </div>
          <div data-card-field data-label="完成质量">
            <div v-if="!readonly" class="percent-control"><input v-model.number="item.quality_percent" type="number" min="0" max="100" step="1" /><span>%</span></div>
            <strong v-else>{{ item.quality_percent ?? 0 }}%</strong>
          </div>
          <div data-card-field data-label="计划完成时间">
            <input v-if="!readonly" v-model="item.planned_completion_date" type="date" />
            <span v-else>{{ formatDateTime(item.planned_completion_date) }}</span>
          </div>
          <div data-card-field data-label="状态">
            <span :class="{ 'status-pill': true, [`status-pill--${item.on_time_status || 'in_progress'}`]: true }">{{ statusLabels[item.on_time_status || 'in_progress'] || '进行中' }}</span>
          </div>
        </article>
        <article data-mobile-task-card v-if="!items.length"><div data-card-field data-label="" colspan="7" class="empty-cell">模板暂无任务，请联系系统管理员配置。</div></article>
      
    </div>
  </div>
  <div v-if="!readonly" class="delay-fields">
    <div v-for="item in items.filter(isDelayed)" :key="`delay-${item.task_code}`" class="delay-card">
      <strong>{{ item.task_name_snapshot || item.task_code }} 的延期说明</strong>
      <div class="delay-grid">
        <input v-model="item.delay_reason" type="text" placeholder="延期原因（必填）" />
        <input v-model="item.next_action" type="text" placeholder="下一步行动（必填）" />
        <input v-model="item.expected_completion_date" type="date" aria-label="预计完成日期" />
      </div>
    </div>
  </div>
</template>

<style scoped src="./TaskPlanTable.css"></style>

<style scoped src="@/mobile/components/data-display/TaskCards.css"></style>
