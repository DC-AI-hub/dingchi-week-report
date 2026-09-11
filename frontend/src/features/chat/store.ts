import { defineStore } from "pinia"
import { computed, ref } from "vue"

import { getErrorMessage } from "@/shared/api/errors"
import { createId } from "@/utils/id"

import { createChatCompletion } from "./api"
import type { ChatEntry, ChatMessage } from "./types"

export const useChatStore = defineStore("chat", () => {
  const messages = ref<ChatEntry[]>([])
  const isSending = ref(false)
  const error = ref("")
  const activeModel = ref("")

  const hasMessages = computed(() => messages.value.length > 0)

  async function send(content: string) {
    const prompt = content.trim()
    if (!prompt || isSending.value) return

    messages.value.push({ id: createId(), role: "user", content: prompt })
    isSending.value = true
    error.value = ""

    try {
      const history: ChatMessage[] = messages.value.map(({ role, content: text }) => ({
        role,
        content: text,
      }))
      const result = await createChatCompletion(history)
      activeModel.value = result.model
      messages.value.push({
        id: createId(),
        role: "assistant",
        content: result.content,
      })
    } catch (requestError) {
      error.value = getErrorMessage(requestError)
    } finally {
      isSending.value = false
    }
  }

  function clear() {
    messages.value = []
    activeModel.value = ""
    error.value = ""
  }

  return { messages, isSending, error, activeModel, hasMessages, send, clear }
})
