<script setup lang="ts">
import PlanStatusTag from "./PlanStatusTag.vue"
import { type ApprovalRecord } from "@/features/monthly-plan/types"
import { formatDateTime } from "@/utils/date"
defineProps<{ records: ApprovalRecord[]; busy: boolean }>()
defineEmits<{ view:[record:ApprovalRecord] }>()
</script>

<template>
  <div class="approval-table-wrap">
    <table class="approval-table"><colgroup><col class="col-month" /><col class="col-person" /><col class="col-group" /><col /><col class="col-kind" /><col class="col-version" /><col class="col-status" /><col class="col-time" /><col class="col-time" /><col class="col-actions" /></colgroup>
      <thead><tr><th>所属月度</th><th>提交人</th><th>分组</th><th>月度目标</th><th>申请类型</th><th>版本</th><th>流程状态</th><th>提交时间</th><th>处理时间</th><th>操作</th></tr></thead>
      <tbody>
        <tr v-for="record in records" :key="record.id">
          <td>{{record.month_key}}</td><td>{{record.employee_name}}</td><td>{{record.group_name}}</td><td class="summary">{{record.snapshot.summary}}</td><td>{{record.process_type==='change'?'变更申请':'首次申请'}}</td><td>{{record.revision}}</td>
          <td><PlanStatusTag :status="record.status" /></td>
          <td class="date">{{formatDateTime(record.created_at)}}</td><td class="date">{{formatDateTime(record.my_acted_at)}}</td>
          <td class="actions"><button type="button" @click="$emit('view',record)">查看</button></td>
        </tr>
        <tr v-if="!records.length"><td class="empty" colspan="10">{{busy?'正在加载审批任务…':'暂无符合条件的审批任务'}}</td></tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped src="./MonthlyApprovalTable.css"></style>
