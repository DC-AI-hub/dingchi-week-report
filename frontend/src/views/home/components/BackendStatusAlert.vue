<script setup lang="ts">
import BaseAlert from "@/components/feedback/BaseAlert.vue"

defineProps<{
  message: string
}>()
</script>

<template>
  <BaseAlert v-if="message">{{ message }}。请确认后端已在 8000 端口启动。</BaseAlert>
</template>
