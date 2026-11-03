<script setup lang="ts">
const prompt = defineModel<string>({ required: true })

defineProps<{
  isSending: boolean
}>()

const emit = defineEmits<{
  submit: []
}>()

function handleKeydown(event: KeyboardEvent) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault()
    emit("submit")
  }
}
</script>

<template>
  <form class="composer" @submit.prevent="emit('submit')">
    <textarea
      v-model="prompt"
      rows="3"
      maxlength="20000"
      placeholder="输入消息，Enter 发送，Shift + Enter 换行"
      :disabled="isSending"
      @keydown="handleKeydown"
    />
    <button class="primary-button" type="submit" :disabled="!prompt.trim() || isSending">
      {{ isSending ? "发送中" : "发送" }}
    </button>
  </form>
</template>

<style scoped src="./ChatComposer.css"></style>
