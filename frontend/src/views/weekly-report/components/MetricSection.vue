<script setup lang="ts">
import type { ReportMetric, TemplateItem } from "@/features/weekly-report/types"

type MetricDraft = Partial<ReportMetric> & { metric_code: string }

defineProps<{
  metrics: MetricDraft[]
  templateMetrics: TemplateItem[]
  readonly?: boolean
}>()
</script>

<template>
  <div class="metric-grid">
    <article v-for="metric in metrics" :key="metric.metric_code" class="metric-card">
      <div class="metric-title">
        <strong>{{ metric.metric_name_snapshot || templateMetrics.find((item) => item.task_code === metric.metric_code)?.label || metric.metric_code }}</strong>
        <span>{{ metric.unit || templateMetrics.find((item) => item.task_code === metric.metric_code)?.unit }}</span>
      </div>
      <p v-if="templateMetrics.find((item) => item.task_code === metric.metric_code)?.guidance" class="metric-guidance">
        {{ templateMetrics.find((item) => item.task_code === metric.metric_code)?.guidance }}
      </p>
      <div class="metric-values">
        <label>目标<input v-if="!readonly" v-model.number="metric.target_value_decimal" type="number" step="0.01" /><span v-else>{{ metric.target_value_decimal ?? '—' }}</span></label>
        <label>实际<input v-if="!readonly" v-model.number="metric.actual_value_decimal" type="number" step="0.01" /><span v-else>{{ metric.actual_value_decimal ?? (metric.value_text || '—') }}</span></label>
      </div>
      <textarea v-if="!readonly" v-model="metric.note" rows="2" placeholder="补充口径或结果说明" />
      <p v-else class="metric-note">{{ metric.note || '暂无补充说明' }}</p>
    </article>
    <p v-if="!metrics.length" class="metric-empty">该职位暂无量化指标。</p>
  </div>
</template>

<style scoped src="./MetricSection.css"></style>
