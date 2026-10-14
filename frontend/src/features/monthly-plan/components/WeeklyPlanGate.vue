<script setup lang="ts">
import { RouterLink } from "vue-router"
defineProps<{month:string;loading:boolean;message:string}>()
defineEmits<{retry:[]}>()
</script>
<template>
  <section class="dashboard-card plan-gate" role="alert">
    <h2>{{loading?'正在检查月度计划审批状态':'请先完成月度计划审批'}}</h2>
    <p>{{loading?`${month} 月度计划加载中…`:message || `${month} 尚无审批通过的月度计划，暂不能填写周报。`}}</p>
    <div v-if="!loading"><RouterLink class="ghost-button" :to="{name:'monthly-plans',query:{month_key:month}}">前往月度计划</RouterLink><button class="ghost-button" type="button" @click="$emit('retry')">重新检查</button></div>
  </section>
</template>
<style scoped src="./WeeklyPlanGate.css"></style>
