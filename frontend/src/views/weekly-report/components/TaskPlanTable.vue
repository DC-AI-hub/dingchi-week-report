<script setup lang="ts">
import type { ReportItem, TemplateItem } from "@/features/weekly-report/types"
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
    <table class="task-table">
      <thead>
        <tr>
          <th>工作任务</th>
          <th>客户 / 项目</th>
          <th>输出成果与进展</th>
          <th>完成进度</th>
          <th>完成质量</th>
          <th>计划完成时间</th>
          <th>状态</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(item, index) in items" :key="item.task_code || index">
          <td class="task-name">
            <strong>{{ item.task_name_snapshot || templateTasks.find((task) => task.task_code === item.task_code)?.label || item.task_code }}</strong>
            <small>{{ item.guidance_snapshot || templateTasks.find((task) => task.task_code === item.task_code)?.guidance }}</small>
          </td>
          <td>
            <input v-if="!readonly" v-model="item.customer_name_snapshot" type="text" placeholder="客户 / 项目" />
            <span v-else>{{ item.customer_name_snapshot || "—" }}</span>
          </td>
          <td class="output-cell">
            <textarea v-if="!readonly" v-model="item.output_description" rows="2" placeholder="本周产出、关键进展、结果说明" />
            <span v-else>{{ item.output_description || item.progress_text || "—" }}</span>
            <textarea v-if="!readonly" v-model="item.progress_text" rows="2" placeholder="补充进展描述" />
          </td>
          <td>
            <div v-if="!readonly" class="percent-control"><input v-model.number="item.progress_percent" type="number" min="0" max="100" step="1" /><span>%</span></div>
            <strong v-else>{{ item.progress_percent ?? 0 }}%</strong>
          </td>
          <td>
            <div v-if="!readonly" class="percent-control"><input v-model.number="item.quality_percent" type="number" min="0" max="100" step="1" /><span>%</span></div>
            <strong v-else>{{ item.quality_percent ?? 0 }}%</strong>
          </td>
          <td>
            <input v-if="!readonly" v-model="item.planned_completion_date" type="date" />
            <span v-else>{{ formatDateTime(item.planned_completion_date) }}</span>
          </td>
          <td>
            <span :class="{ 'status-pill': true, [`status-pill--${item.on_time_status || 'in_progress'}`]: true }">{{ statusLabels[item.on_time_status || 'in_progress'] || '进行中' }}</span>
          </td>
        </tr>
        <tr v-if="!items.length"><td colspan="7" class="empty-cell">模板暂无任务，请联系系统管理员配置。</td></tr>
      </tbody>
    </table>
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
