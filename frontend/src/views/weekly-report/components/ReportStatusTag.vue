<script setup lang="ts">
import type { ReportStatus } from "@/features/weekly-report/types"

defineProps<{ status: ReportStatus }>()

const labels: Record<string, string> = {
  active: "激活状态",
  pending_activation: "待激活状态",
  archived: "归档状态",
}
</script>

<template>
  <span :class="['report-status-tag', 'report-status-tag--' + status]">
    {{ labels[status] || status }}
  </span>
</template>

<style scoped src="./ReportStatusTag.css"></style>
