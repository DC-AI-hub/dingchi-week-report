<script setup lang="ts">
import { computed } from "vue"
import type { ApprovedPlanVersion } from "@/features/monthly-plan/types"
import MonthlyPlanTaskPanel from "@/features/monthly-plan/components/MonthlyPlanTaskPanel.vue"
import { formatDateTime } from "@/utils/date"
const props=defineProps<{history:ApprovedPlanVersion[]}>()
const entries=computed(()=>[...props.history].sort((a,b)=>Date.parse(b.created_at)-Date.parse(a.created_at) || b.id.localeCompare(a.id,'en',{numeric:true})))
</script>
<template>
<section v-if="history.length" class="dashboard-card change-history"><h2>变更历史</h2>
 <details v-for="entry in entries" :key="entry.id"><summary><strong>{{entry.process_type==='initial'?'申请':'变更'}}</strong><time :datetime="entry.created_at">{{formatDateTime(entry.created_at)}}</time></summary>
 <div class="version-content"><h3>月度目标</h3><p>{{entry.snapshot.summary}}</p><MonthlyPlanTaskPanel :tasks="entry.snapshot.tasks" :month-key="entry.snapshot.month_key" :template-code="entry.snapshot.template_code" readonly /></div>
 </details>
</section>
</template>
<style scoped src="./PlanChangeHistory.css"></style>
