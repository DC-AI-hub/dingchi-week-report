<script setup lang="ts">
defineProps<{summary:string;month:string}>()
</script>
<template><section class="dashboard-card monthly-goal-display"><h2>月度目标 <small>{{month}}</small></h2><p class="user-content">{{summary || '暂无月度目标'}}</p></section></template>
<style scoped src="./MonthlyGoalDisplay.css"></style>
