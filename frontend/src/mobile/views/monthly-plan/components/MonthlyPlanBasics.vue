<script setup lang="ts">
import { computed } from "vue"
import ExamplePreviewButton from "@/mobile/components/feedback/ExamplePreviewButton.vue"
import { monthlyGoalSamples } from "@/mobile/features/monthly-plan/goal-samples"
const month=defineModel<string>('month',{required:true})
const summary=defineModel<string>('summary',{required:true})
const props=defineProps<{existing:boolean;busy:boolean;templateCode:string}>()
const sampleFields=computed(()=>monthlyGoalSamples(props.templateCode))
</script>
<template>
  <section class="dashboard-card plan-basics">
    <div class="month-field">
      <label class="field-label" for="monthly-plan-month">所属月度<span class="required"> *</span></label>
      <input id="monthly-plan-month" v-model="month" type="month" required :disabled="existing || busy" />
    </div>
    <div class="goal-field">
      <div class="goal-heading">
        <label class="field-label" for="monthly-plan-goal">月度目标<span class="required"> *</span></label>
        <ExamplePreviewButton content="" :fields="sampleFields" panel-title="月度目标填写样例" />
      </div>
      <textarea id="monthly-plan-goal" v-model="summary" rows="7" maxlength="10000" required :disabled="busy" placeholder="请输入本月工作目标" />
    </div>
  </section>
</template>
<style scoped src="./MonthlyPlanBasics.css"></style>
