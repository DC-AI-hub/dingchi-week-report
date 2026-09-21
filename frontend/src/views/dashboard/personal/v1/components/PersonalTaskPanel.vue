<script setup lang="ts">
import { ClipboardCheck, ArrowUpRight } from "lucide-vue-next"
import { RouterLink } from "vue-router"

import type { DashboardItem } from "@/features/dashboard/types"

defineProps<{ tasks: DashboardItem[] }>()

function percent(value: number | null) {
  return value === null ? "—" : `${Math.round(value)}%`
}

function statusLabel(status: string) {
  return status === "overdue" || status === "late" ? "延期" : status === "on_time" ? "已完成" : "进行中"
}
</script>

<template>
  <article class="personal-content-panel personal-task-panel">
    <div class="content-panel-heading">
      <div class="content-panel-title">
        <span class="content-panel-icon" aria-hidden="true"><ClipboardCheck :size="17" /></span>
        <div>
          <span class="content-kicker">重点行动</span>
          <h2>我的本周条目</h2>
        </div>
      </div>
      <RouterLink class="panel-link" to="/weekly-reports">查看全部 <ArrowUpRight :size="14" aria-hidden="true" /></RouterLink>
    </div>

    <div v-if="!tasks.length" class="content-empty">暂无任务数据</div>
    <div v-else class="personal-task-table">
      <div class="personal-task-table-head" aria-hidden="true">
        <span>客户</span><span>工作任务</span><span>进展</span><span>进度</span><span>完成率</span><span>状态</span>
      </div>
      <div v-for="task in tasks.slice(0, 5)" :key="task.id" class="personal-task-row">
        <span class="task-customer" :title="task.customer_name_snapshot || '内部事项'">{{ task.customer_name_snapshot || "内部事项" }}</span>
        <div class="task-name" :title="task.task_name_snapshot">
          <strong>{{ task.task_name_snapshot }}</strong>
          <small>{{ task.progress_text || "暂无进展" }}</small>
        </div>
        <div class="task-progress-track" aria-hidden="true"><span :style="{ width: `${task.progress_percent || 0}%` }" /></div>
        <span class="task-number">{{ percent(task.progress_percent) }}</span>
        <span class="task-number task-number--green">{{ percent(task.completion_rate) }}</span>
        <span class="task-status" :class="`task-status--${task.on_time_status}`">{{ statusLabel(task.on_time_status) }}</span>
      </div>
    </div>
  </article>
</template>

<style scoped src="./PersonalTaskPanel.css"></style>
