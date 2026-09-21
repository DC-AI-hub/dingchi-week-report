import { ref } from "vue"

const storageKey = "dingchi-week-report:ito-sales:customers"
const customerHistory = ref<string[]>([])
let loaded = false

function load() {
  if (loaded) return
  loaded = true
  try {
    const value = JSON.parse(localStorage.getItem(storageKey) || "[]")
    if (Array.isArray(value)) customerHistory.value = value.filter((item): item is string => typeof item === "string").slice(0, 10)
  } catch { customerHistory.value = [] }
}

function remember(name: string) {
  load()
  const normalized = name.trim()
  if (!normalized) return
  customerHistory.value = [normalized, ...customerHistory.value.filter((item) => item !== normalized)].slice(0, 10)
  localStorage.setItem(storageKey, JSON.stringify(customerHistory.value))
}

export function useItoSalesCustomerHistory() {
  load()
  return {
    customerHistory,
    refresh: load,
    remember,
  }
}
