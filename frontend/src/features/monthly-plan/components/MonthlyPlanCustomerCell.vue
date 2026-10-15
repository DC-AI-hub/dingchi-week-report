<script setup lang="ts">
import DeliveryCustomerSelect from "@/features/weekly-report/components/DeliveryCustomerSelect.vue"

defineProps<{ value: string }>()
const emit = defineEmits<{ change: [value: string] }>()
</script>
<template>
  <div class="monthly-customer-cell" tabindex="0" :aria-label="`客户：${value || '未选择'}`">
    <span class="customer-text">{{ value || "选择客户" }}</span>
    <div class="customer-editor"><DeliveryCustomerSelect :model-value="value" required teleport-menu @update:model-value="emit('change', $event)" /></div>
  </div>
</template>
<style scoped src="./MonthlyPlanCustomerCell.css"></style>
