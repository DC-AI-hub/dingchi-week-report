import { defineStore } from "pinia"
import { computed, ref } from "vue"

import { getLiveness, type Liveness } from "@/features/system/api"
import { getErrorMessage } from "@/shared/api/errors"

export const useAppStore = defineStore("app", () => {
  const backend = ref<Liveness | null>(null)
  const backendError = ref("")
  const isCheckingBackend = ref(false)
  const theme = ref<"light" | "dark">(
    localStorage.getItem("theme") === "dark" ? "dark" : "light",
  )

  const backendAvailable = computed(() => backend.value?.status === "ok")

  function applyTheme() {
    document.documentElement.dataset.theme = theme.value
    localStorage.setItem("theme", theme.value)
  }

  function toggleTheme() {
    theme.value = theme.value === "light" ? "dark" : "light"
    applyTheme()
  }

  async function checkBackend() {
    isCheckingBackend.value = true
    backendError.value = ""
    try {
      backend.value = await getLiveness()
    } catch (error) {
      backend.value = null
      backendError.value = getErrorMessage(error)
    } finally {
      isCheckingBackend.value = false
    }
  }

  applyTheme()

  return {
    backend,
    backendAvailable,
    backendError,
    isCheckingBackend,
    theme,
    checkBackend,
    toggleTheme,
  }
})

