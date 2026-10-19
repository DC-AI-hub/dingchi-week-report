<script setup lang="ts">
import SalesTaskCollectionSection from "@/features/weekly-report/components/SalesTaskCollectionSection.vue"
import { itoSalesTaskFieldDefinitions, type ItoSalesTaskDraft, type ItoSalesTaskFieldDefinition } from "@/features/weekly-report/ito-sales/types"
defineProps<{ title: string; tasks: ItoSalesTaskDraft[]; defaultOwnerId?: string; ownerName?: string; fieldDefinitions?: ItoSalesTaskFieldDefinition[] }>()
const emit = defineEmits<{ "update:tasks": [tasks: ItoSalesTaskDraft[]] }>()
</script>
<template>
  <SalesTaskCollectionSection template-code="ito_sales_v1" :title="title" :tasks="tasks" :default-owner-id="defaultOwnerId" :owner-name="ownerName" :field-definitions="fieldDefinitions?.length ? fieldDefinitions : itoSalesTaskFieldDefinitions" @update:tasks="emit('update:tasks', $event)" />
</template>
