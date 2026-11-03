import { mobileStorage as localStorage } from "@/mobile/shared/storage"
import { computed, ref } from "vue"

const STORAGE_KEY = "dingchi-week-report:customer-history:v1"
const MAX_HISTORY_ITEMS = 10

interface CustomerHistoryRecord {
  name: string
  used_at: number
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null
}

function parseRecord(value: unknown): CustomerHistoryRecord | null {
  if (
    !isRecord(value) ||
    typeof value.name !== "string" ||
    !value.name.trim() ||
    typeof value.used_at !== "number" ||
    !Number.isFinite(value.used_at)
  ) {
    return null
  }
  return { name: value.name.trim(), used_at: value.used_at }
}

function readRecords(): CustomerHistoryRecord[] {
  if (typeof window === "undefined") return []

  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed: unknown = JSON.parse(raw)
    if (!Array.isArray(parsed)) return []

    return parsed
      .map(parseRecord)
      .filter((item): item is CustomerHistoryRecord => Boolean(item))
      .sort((left, right) => right.used_at - left.used_at)
      .filter((item, index, records) => records.findIndex((candidate) => candidate.name === item.name) === index)
      .slice(0, MAX_HISTORY_ITEMS)
  } catch {
    return []
  }
}

function writeRecords(records: CustomerHistoryRecord[]) {
  if (typeof window === "undefined") return

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(records))
  } catch {
    // 浏览器禁用本地存储时不阻断周报填写。
  }
}

export function useCustomerHistory() {
  const records = ref<CustomerHistoryRecord[]>([])
  const customerHistory = computed(() => records.value.map((item) => item.name))

  function refresh() {
    records.value = readRecords()
  }

  function remember(name: string) {
    const normalized = name.trim()
    if (!normalized) return

    const nextRecords: CustomerHistoryRecord[] = [
      { name: normalized, used_at: Date.now() },
      ...records.value.filter((item) => item.name !== normalized),
    ].slice(0, MAX_HISTORY_ITEMS)
    records.value = nextRecords
    writeRecords(nextRecords)
  }

  return { customerHistory, refresh, remember }
}
