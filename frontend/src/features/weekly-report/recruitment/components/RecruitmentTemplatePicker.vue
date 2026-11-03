<script setup lang="ts">
import { ref } from "vue"
import TaskTemplatePopover from "@/features/weekly-report/components/TaskTemplatePopover.vue"
import { recruitmentTaskTemplates } from "../task-templates"
const emit = defineEmits<{ select: [index: number] }>()
const open = ref(false)
const trigger = ref<HTMLButtonElement | null>(null)
const anchor = ref<HTMLElement | null>(null)
const selected = ref("")
function toggle() {
  anchor.value = trigger.value?.closest<HTMLElement>('[role="dialog"]') || null
  open.value = !open.value
}
function select(index: number) {
  selected.value = String(index)
  open.value = false
  emit("select", index)
  trigger.value?.focus()
}
</script>
<template>
  <button ref="trigger" class="template-picker" type="button" :aria-expanded="open" aria-haspopup="dialog" @click.prevent="toggle">选择模板</button>
  <TaskTemplatePopover :open="open" :anchor="anchor" :trigger="trigger" :selected="selected" :templates="recruitmentTaskTemplates" @close="open = false" @select="select" />
</template>
<style scoped src="./RecruitmentTemplatePicker.css"></style>
