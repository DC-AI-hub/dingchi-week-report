<script setup lang="ts">
import { RouterLink } from "vue-router"
import { planStatusLabels, type ApprovalRecord } from "@/mobile/features/monthly-plan/types"
import { formatDateTime } from "@/utils/date"
defineProps<{records:ApprovalRecord[]}>()
</script>
<template>
  <section class="dashboard-card approval-history">
    <h2>审批记录</h2>
    <div v-for="record in records" :key="record.id" class="approval-record">
      <header><RouterLink v-if="record.plan_id" :to="{name:'mobile-monthly-plan-detail',params:{planId:record.plan_id}}">{{record.employee_name}} · {{record.month_key}}</RouterLink><strong>第 {{record.revision}} 版 · {{planStatusLabels[record.status]}}</strong><span>{{formatDateTime(record.created_at)}}</span></header>
      <ol><li v-for="step in record.steps" :key="step.sort_order">{{step.approver_name}}：{{planStatusLabels[step.status]}}<span v-if="step.reason"> · {{step.reason}}</span></li></ol>
      <details><summary>查看此次提交的计划快照</summary><p class="snapshot">{{record.snapshot.summary}}</p><ul><li v-for="(task,index) in record.snapshot.tasks" :key="index">{{task.scope_name ? task.scope_name+'：' : ''}}{{task.work_task}}</li></ul></details>
    </div>
  </section>
</template>
<style scoped src="./ApprovalHistoryPanel.css"></style>
