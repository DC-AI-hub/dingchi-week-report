<script setup lang="ts">
import { ArrowUpRight, Check, Trophy } from "lucide-vue-next"
import { RouterLink } from "vue-router"

import type { DashboardItem, DashboardReport } from "@/features/dashboard/types"

const props = defineProps<{ tasks: DashboardItem[]; reports: DashboardReport[] }>()
const completedTasks = () => props.tasks.filter((task) => (task.progress_percent || 0) >= 100).slice(0, 3)
</script>

<template>
  <article class="personal-content-panel personal-results-panel">
    <div class="content-panel-heading">
      <div class="content-panel-title">
        <span class="content-panel-icon content-panel-icon--purple" aria-hidden="true"><Trophy :size="17" /></span>
        <div>
          <span class="content-kicker">成果沉淀</span>
          <h2>本周工作成果</h2>
        </div>
      </div>
      <RouterLink class="panel-link panel-link--icon" to="/weekly-reports" aria-label="查看周报"><ArrowUpRight :size="15" /></RouterLink>
    </div>

    <div v-if="!completedTasks().length && !props.reports.length" class="content-empty">暂无已完成成果</div>
    <div v-else class="result-list">
      <div v-for="task in completedTasks()" :key="task.id" class="result-item">
        <span class="result-marker" aria-hidden="true"><Check :size="14" :stroke-width="2.8" /></span>
        <div>
          <strong :title="task.task_name_snapshot">{{ task.task_name_snapshot }}</strong>
          <span :title="task.output_description || task.progress_text">{{ task.output_description || task.progress_text || "已完成本周任务" }}</span>
        </div>
      </div>
      <div v-for="report in props.reports.slice(0, Math.max(0, 3 - completedTasks().length))" :key="`report-${report.id}`" class="result-item">
        <span class="result-marker result-marker--blue" aria-hidden="true"><ArrowUpRight :size="14" :stroke-width="2.8" /></span>
        <div>
          <strong :title="report.summary || report.employee_name">{{ report.summary || `${report.employee_name}的周报` }}</strong>
          <span>{{ report.group_name || "本周周报" }}</span>
        </div>
      </div>
    </div>
  </article>
</template>

<style scoped src="./PersonalResultsPanel.css"></style>
