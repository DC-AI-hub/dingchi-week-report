<script setup lang="ts">
export interface ExamplePreviewField {
  label: string
  value?: string
  rows?: ReadonlyArray<ExamplePreviewRow>
}

export interface ExamplePreviewRow {
  label: string
  value: string
}

withDefaults(
  defineProps<{
    content: string
    label?: string
    panelTitle?: string
    fields?: ReadonlyArray<ExamplePreviewField>
  }>(),
  {
    label: "填写样例",
    panelTitle: "填写样例",
  },
)
</script>

<template>
  <div class="example-preview">
    <button
      class="example-preview__trigger"
      type="button"
      :aria-label="`${label}（悬浮查看）`"
    >
      {{ label }}
    </button>
    <div class="example-preview__panel" role="tooltip">
      <div class="example-preview__panel-header">
        <strong>{{ panelTitle }}</strong>
      </div>
      <div v-if="fields?.length" class="example-preview__fields">
        <div v-for="field in fields" :key="field.label" class="example-preview__field">
          <span class="example-preview__field-label">{{ field.label }}</span>
          <div v-if="field.rows?.length" class="example-preview__field-rows">
            <div v-for="row in field.rows" :key="row.label" class="example-preview__field-row">
              <span class="example-preview__field-row-label">{{ row.label }}</span>
              <div class="example-preview__field-row-value">{{ row.value }}</div>
            </div>
          </div>
          <div v-else class="example-preview__field-value">{{ field.value }}</div>
        </div>
      </div>
      <pre v-else class="example-preview__content">{{ content }}</pre>
    </div>
  </div>
</template>

<style scoped src="./ExamplePreviewButton.css"></style>
