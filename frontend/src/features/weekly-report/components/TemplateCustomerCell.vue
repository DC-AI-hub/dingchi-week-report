<script setup lang="ts">
import TemplateTaskCell from "./TemplateTaskCell.vue"
import type { TaskTextMetadata } from "../task-texts"
import type { EditableTask } from "../task-editing"
defineProps<{ task: TaskTextMetadata & { customer_name?: string } }>()
const emit = defineEmits<{ patch: [value: Partial<EditableTask>] }>()
</script>
<template>
  <TemplateTaskCell label="客户" :task="{ task_name: task.customer_name || '', task_template: task.customer_template, task_values: task.customer_values }"
    @patch="emit('patch', { customer_name: $event.task_name, customer_values: $event.task_values })" />
</template>
