<script setup lang="ts">
import { ref } from "vue"

import BaseAlert from "@/components/feedback/BaseAlert.vue"
import { useChatStore } from "@/features/chat/store"

import ChatComposer from "./ChatComposer.vue"
import ChatMessageList from "./ChatMessageList.vue"
import ChatToolbar from "./ChatToolbar.vue"

const chatStore = useChatStore()
const prompt = ref("")

async function submit() {
  const content = prompt.value
  if (!content.trim()) return

  prompt.value = ""
  await chatStore.send(content)
}
</script>

<template>
  <section class="chat-panel surface-card" aria-label="AI 对话">
    <ChatToolbar
      :active-model="chatStore.activeModel"
      :has-messages="chatStore.hasMessages"
      :is-sending="chatStore.isSending"
      @clear="chatStore.clear"
    />

    <ChatMessageList :messages="chatStore.messages" :is-sending="chatStore.isSending" />

    <BaseAlert v-if="chatStore.error" :message="chatStore.error" />

    <ChatComposer v-model="prompt" :is-sending="chatStore.isSending" @submit="submit" />
  </section>
</template>

<style scoped src="./ChatPanel.css"></style>
