import { mobileStorage as localStorage } from "@/mobile/shared/storage"
import { computed, ref } from "vue"

const storageKey = "dingchi-week-report:customer-history:v1"
const maxHistoryItems = 10

interface CustomerHistoryRecord { name: string; used_at: number }

function readRecords(): CustomerHistoryRecord[] {
  if (typeof window === "undefined") return []
  try {
    const parsed: unknown = JSON.parse(localStorage.getItem(storageKey) || "[]")
    if (!Array.isArray(parsed)) return []
    const records = parsed.filter((item): item is CustomerHistoryRecord => {
      return Boolean(item && typeof item === "object" && typeof (item as CustomerHistoryRecord).name === "string" &&
        (item as CustomerHistoryRecord).name.trim() && Number.isFinite((item as CustomerHistoryRecord).used_at))
    })
    return records
      .map((item) => ({ name: item.name.trim(), used_at: item.used_at }))
      .sort((left, right) => right.used_at - left.used_at)
      .filter((item, index, all) => all.findIndex((candidate) => candidate.name === item.name) === index)
      .slice(0, maxHistoryItems)
  } catch { return [] }
}

function writeRecords(records: CustomerHistoryRecord[]) {
  if (typeof window === "undefined") return
  try { localStorage.setItem(storageKey, JSON.stringify(records)) } catch { /* 本地存储不可用时不阻断填写 */ }
}

export function useDeliveryAssistantCustomerHistory() {
  const records = ref<CustomerHistoryRecord[]>([])
  const customerHistory = computed(() => records.value.map((item) => item.name))
  function refresh() { records.value = readRecords() }
  function remember(name: string) {
    const normalized = name.trim()
    if (!normalized) return
    const next = [{ name: normalized, used_at: Date.now() }, ...records.value.filter((item) => item.name !== normalized)].slice(0, maxHistoryItems)
    records.value = next
    writeRecords(next)
  }
  return { customerHistory, refresh, remember }
}
