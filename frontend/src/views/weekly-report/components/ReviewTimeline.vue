<script setup lang="ts">
import type { ReportReview } from "@/features/weekly-report/types"

defineProps<{ history: ReportReview[] }>()

const labels: Record<string, string> = { submit: "提交周报", approve: "审核通过", return: "退回修改" }
</script>

<template>
  <div class="review-timeline">
    <div v-for="item in history" :key="item.id" class="review-entry">
      <span class="review-dot" />
      <div><strong>{{ labels[item.action] || item.action }}</strong><span>{{ item.reviewer_name || "系统" }} · {{ item.created_at }}</span><p v-if="item.comment">{{ item.comment }}</p></div>
    </div>
    <p v-if="!history.length" class="review-empty">暂无提交或审核记录。</p>
  </div>
</template>

<style scoped>
.review-timeline { display: grid; gap: 0.85rem; }
.review-entry { display: grid; grid-template-columns: 14px 1fr; gap: 0.65rem; position: relative; }
.review-entry:not(:last-child)::after { content: ""; position: absolute; left: 6px; top: 14px; bottom: -14px; width: 1px; background: #dce8f7; }
.review-dot { z-index: 1; width: 12px; height: 12px; margin-top: 3px; border: 3px solid #dcecff; border-radius: 50%; background: var(--accent); box-sizing: border-box; }
.review-entry strong, .review-entry span, .review-entry p { display: block; }
.review-entry strong { color: var(--text-strong); font-size: 0.8rem; }
.review-entry span { margin-top: 0.18rem; color: var(--muted); font-size: 0.7rem; }
.review-entry p { margin: 0.35rem 0 0; color: var(--text); font-size: 0.76rem; white-space: pre-wrap; }
.review-empty { margin: 0; color: var(--muted); font-size: 0.78rem; }
</style>
