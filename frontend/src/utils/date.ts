/** 统一页面日期显示为 yyyy-mm-dd HH:mi:ss。 */
export function formatDateTime(
  value: string | Date | null | undefined,
  empty = "—",
): string {
  if (value === null || value === undefined || value === "") return empty
  const source = value instanceof Date ? value.toISOString() : String(value)
  const match = source.match(/^(\d{4}-\d{2}-\d{2})(?:[T ](\d{2}:\d{2}:\d{2}))?/)
  if (!match) return source.replace("T", " ").replace(/Z$/, "")
  return match[1] + " " + (match[2] || "00:00:00")
}

/** 显示周报周期的日期范围，不带时区和 ISO 分隔符。 */
export function formatPeriod(
  periodStart: string | null | undefined,
  periodEnd: string | null | undefined,
): string {
  const start = formatDateTime(periodStart, "")
  const end = formatDateTime(periodEnd, "")
  if (!start && !end) return "未设置周期"
  if (!end) return start.slice(0, 10)
  return start.slice(0, 10) + " 至 " + end.slice(0, 10)
}
