<script setup lang="ts">
import { RouterLink } from "vue-router"
import type { PlanContext } from "@/features/monthly-plan/types"
defineProps<{ context: PlanContext | null; personal: boolean }>()
</script>
<template>
  <header class="monthly-list-header">
    <div class="monthly-list-tabs"><slot /></div>
    <RouterLink v-if="personal && context?.can_create" class="primary-button" :to="{name:'monthly-plan-new',query:{tab:'mine'}}">新增月度计划</RouterLink>
  </header>
  <p v-if="personal && context?.warning" class="monthly-list-warning" role="alert">{{ context.warning }}</p>
</template>
<style scoped src="./MonthlyPlanListHeader.css"></style>
