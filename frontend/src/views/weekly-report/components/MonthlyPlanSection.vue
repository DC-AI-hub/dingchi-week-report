<script setup lang="ts">
import { computed, ref, watch } from "vue"

import ExamplePreviewButton from "@/components/feedback/ExamplePreviewButton.vue"
import BaseDialog from "@/components/overlay/BaseDialog.vue"

interface ExampleRow {
  label: string
  value: string
}

interface ExampleField {
  label: string
  value?: string
  rows?: ReadonlyArray<ExampleRow>
}

const props = withDefaults(
  defineProps<{
    editorOpen: boolean
    monthKey: string
    summary: string
    sampleContent: string
    sampleFields?: ReadonlyArray<ExampleField>
    locked?: boolean
    busy?: boolean
    errorMessage?: string
  }>(),
  {
    sampleFields: () => [],
    locked: false,
    busy: false,
    errorMessage: "",
  },
)

const emit = defineEmits<{
  open: []
  close: []
  save: [summary: string]
}>()

const draft = ref("")
const localValidationError = ref("")
const confirmOpen = ref(false)
const planLocked = computed(() => props.locked || Boolean(props.summary.trim()))

watch(
  () => [props.editorOpen, props.summary] as const,
  ([open, summary]) => {
    if (open) {
      draft.value = summary
      localValidationError.value = ""
    } else {
      confirmOpen.value = false
    }
  },
  { immediate: true },
)

function save() {
  if (planLocked.value) return
  const value = draft.value.trim()
  if (!value) {
    localValidationError.value = "月度计划不能为空。"
    return
  }
  confirmOpen.value = true
}

function confirmSave() {
  if (planLocked.value) return
  confirmOpen.value = false
  emit("save", draft.value.trim())
}
</script>

<template>
  <section class="dashboard-card monthly-plan-section" :class="{ 'is-locked': planLocked }">
    <div class="monthly-plan-section__heading">
      <h2>月度计划</h2>
      <div class="monthly-plan-section__actions">
        <ExamplePreviewButton
          :content="sampleContent"
          :fields="sampleFields"
          panel-title="月度计划填写样例"
        />
        <button v-if="!planLocked" class="ghost-button" type="button" @click="emit('open')">
          编辑月度计划
        </button>
      </div>
    </div>
    <textarea :value="summary" rows="4" readonly aria-label="月度计划内容" />
  </section>

  <BaseDialog
    :open="editorOpen"
    title="月度计划"
    width="720px"
    :busy="busy"
    @close="emit('close')"
  >
    <div class="monthly-plan-editor">
      <div class="monthly-plan-editor__month">{{ monthKey }}</div>
      <textarea v-model="draft" rows="12" :readonly="planLocked" aria-label="编辑月度计划内容" />
      <p v-if="localValidationError || errorMessage" class="monthly-plan-editor__error" role="alert">
        {{ localValidationError || errorMessage }}
      </p>
    </div>
    <template #actions>
      <button class="ghost-button" type="button" :disabled="busy" @click="emit('close')">
        取消
      </button>
      <button class="primary-button" type="button" :disabled="busy || planLocked" @click="save">
        {{ planLocked ? "已锁定" : busy ? "保存中" : "保存" }}
      </button>
    </template>
  </BaseDialog>

  <BaseDialog
    :open="confirmOpen"
    title="确认保存月度计划"
    width="520px"
    @close="confirmOpen = false"
  >
    <div class="monthly-plan-confirm">
      <div class="monthly-plan-confirm__warning" role="alert">
        请确认月度计划内容无误。保存后，该月度计划将锁定，后续不支持修改。
      </div>
    </div>
    <template #actions>
      <button class="ghost-button" type="button" @click="confirmOpen = false">取消</button>
      <button class="primary-button" type="button" @click="confirmSave">确认保存</button>
    </template>
  </BaseDialog>
</template>

<style scoped src="./MonthlyPlanSection.css"></style>
