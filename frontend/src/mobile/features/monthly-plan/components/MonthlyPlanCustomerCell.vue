<script setup lang="ts">
import DeliveryCustomerSelect from "@/mobile/features/weekly-report/components/DeliveryCustomerSelect.vue"

defineProps<{ value: string; textInput?: boolean }>()
const emit = defineEmits<{ change: [value: string] }>()
</script>
<template>
  <div class="monthly-customer-cell" tabindex="0" :aria-label="`${textInput ? '维度' : '客户'}：${value || '未填写'}`">
    <span class="customer-text">{{ value || (textInput ? "填写维度" : "选择客户") }}</span>
    <div class="customer-editor"><input v-if="textInput" :value="value" aria-label="维度" maxlength="255" placeholder="请输入维度" @change="emit('change', ($event.target as HTMLInputElement).value.trim())" /><DeliveryCustomerSelect v-else :model-value="value" required teleport-menu @update:model-value="emit('change', $event)" /></div>
  </div>
</template>
<style scoped src="./MonthlyPlanCustomerCell.css"></style>
