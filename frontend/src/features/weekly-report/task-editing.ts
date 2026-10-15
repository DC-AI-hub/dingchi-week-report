import type { DeliveryTaskDraft, DeliveryTaskColumn } from "./delivery-specialist/types"

export interface TaskTemplateOption { task: string; work: string; dimension?: string }
export type EditableTask = Omit<DeliveryTaskDraft, "customer_name"> & {
  customer_name?: string
  dimension?: string
  quality_percent?: number | null
  completion_rate?: number | null
}
export type EditableTaskColumn = DeliveryTaskColumn | "dimension" | "quality_percent" | "completion_rate"
export interface EditableTaskField { code: EditableTaskColumn; label: string }
