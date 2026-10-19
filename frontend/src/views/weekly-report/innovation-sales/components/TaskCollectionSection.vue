<script setup lang="ts">
import SalesTaskCollectionSection from "@/features/weekly-report/components/SalesTaskCollectionSection.vue"
import { innovationSalesTaskFieldDefinitions, type InnovationSalesTaskDraft, type InnovationSalesTaskFieldDefinition } from "@/features/weekly-report/innovation-sales/types"
defineProps<{ title: string; tasks: InnovationSalesTaskDraft[]; defaultOwnerId?: string; ownerName?: string; fieldDefinitions?: InnovationSalesTaskFieldDefinition[] }>()
const emit = defineEmits<{ "update:tasks": [tasks: InnovationSalesTaskDraft[]] }>()
</script>
<template>
  <SalesTaskCollectionSection template-code="innovation_sales_v1" :title="title" :tasks="tasks" :default-owner-id="defaultOwnerId" :owner-name="ownerName" :field-definitions="fieldDefinitions?.length ? fieldDefinitions : innovationSalesTaskFieldDefinitions" @update:tasks="emit('update:tasks', $event)" />
</template>
