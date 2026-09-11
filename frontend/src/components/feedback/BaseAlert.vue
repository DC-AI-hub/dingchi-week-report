<script setup lang="ts">
withDefaults(
  defineProps<{
    message?: string
  }>(),
  {
    message: "",
  },
)
</script>

<template>
  <p class="base-alert" role="alert">
    <slot>{{ message }}</slot>
  </p>
</template>

<style scoped src="./BaseAlert.css"></style>
