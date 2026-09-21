import {
  deliveryTaskFieldDefinitions,
  emptyDeliveryTask,
  type DeliveryTaskDraft,
  type DeliveryTaskFieldDefinition,
} from "@/features/weekly-report/delivery-specialist/types"

/**
 * 职能组沿用交付模板的任务字段和顺序，但工作事项不按客户归组，故移除客户字段。
 * 字段定义独立于交付专员，便于后端字典未初始化时仍能按本模板渲染。
 */
export const functionalTaskFieldDefinitions: DeliveryTaskFieldDefinition[] =
  deliveryTaskFieldDefinitions
    .filter((field) => field.code !== "customer_name")
    .map((field) => ({ ...field }))

export type FunctionalTaskDraft = DeliveryTaskDraft

export function emptyFunctionalTask(ownerName = ""): FunctionalTaskDraft {
  return emptyDeliveryTask(ownerName)
}
