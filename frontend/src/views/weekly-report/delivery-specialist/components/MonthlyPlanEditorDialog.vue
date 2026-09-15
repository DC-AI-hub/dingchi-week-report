<script setup lang="ts">
import { ref, watch } from "vue"

import BaseDialog from "@/components/overlay/BaseDialog.vue"

const props = withDefaults(
  defineProps<{
    open: boolean
    monthKey: string
    summary: string
    busy?: boolean
    errorMessage?: string
  }>(),
  { busy: false, errorMessage: "" },
)
const emit = defineEmits<{
  close: []
  save: [summary: string]
}>()
const draft = ref("")

watch(
  () => [props.open, props.summary] as const,
  ([open, summary]) => {
    if (open) draft.value = summary
  },
  { immediate: true },
)

function save() {
  emit("save", draft.value.trim())
}
</script>

<template>
  <BaseDialog :open="open" title="月度计划" width="720px" :busy="busy" @close="emit('close')">
    <div class="monthly-plan-editor">
      <div class="monthly-plan-editor__month">{{ monthKey }}</div>
      <textarea v-model="draft" rows="12" aria-label="月度计划内容" />
      <p v-if="errorMessage" class="monthly-plan-editor__error" role="alert">{{ errorMessage }}</p>
    </div>
    <template #actions>
      <button class="ghost-button" type="button" :disabled="busy" @click="emit('close')">取消</button>
      <button class="primary-button" type="button" :disabled="busy" @click="save">{{ busy ? "保存中" : "保存" }}</button>
    </template>
  </BaseDialog>
</template>

<style scoped src="./MonthlyPlanEditorDialog.css"></style>
