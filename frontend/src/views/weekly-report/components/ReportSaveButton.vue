<script setup lang="ts">
defineProps<{ busy: boolean; disabled?: boolean }>()
defineEmits<{ save: [] }>()
</script>

<template>
  <Teleport defer to="#weekly-report-header-actions">
    <button
      class="primary-button"
      type="button"
      :disabled="busy || disabled"
      @click="$emit('save')"
    >
      {{ busy ? "保存中…" : "保存周报" }}
    </button>
  </Teleport>
</template>
