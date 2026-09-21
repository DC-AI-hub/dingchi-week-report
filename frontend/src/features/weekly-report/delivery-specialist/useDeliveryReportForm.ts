import { computed, reactive, ref, watch } from "vue"

import { useAuthStore } from "@/features/auth/store"
import {
  createReport,
  getMonthlyPlan,
  getReportDetail,
  getReportTemplate,
  saveMonthlyPlan,
  uploadReportAttachment,
  updateReport,
} from "../api"
import type {
  DailyWorkTask,
  ReportAttachment,
  ReportItem,
  ReportPayload,
  ReportTemplateField,
  WeeklyReportDetail,
} from "../types"
import {
  deliveryTaskFieldDefinitions,
  emptyDeliveryTask,
  type DeliveryTaskDraft,
  type DeliveryTaskFieldDefinition,
} from "./types"

function isoDate(value: Date) {
  const month = String(value.getMonth() + 1).padStart(2, "0")
  const day = String(value.getDate()).padStart(2, "0")
  return `${value.getFullYear()}-${month}-${day}`
}

function currentMonday() {
  const value = new Date()
  const day = value.getDay() || 7
  value.setDate(value.getDate() - day + 1)
  return isoDate(value)
}

function endOfWeek(start: string) {
  const value = new Date(`${start}T00:00:00`)
  value.setDate(value.getDate() + 6)
  return isoDate(value)
}

function taskCode(task: Pick<DeliveryTaskDraft, "client_key">, prefix = "delivery") {
  return `${prefix}_${task.client_key}`.slice(0, 64)
}

function fromReportItem(
  item: ReportItem,
  attachments: ReportAttachment[] = [],
): DeliveryTaskDraft {
  return {
    ...emptyDeliveryTask(item.owner_name_snapshot),
    client_key: item.id || item.task_code,
    updated_at: item.updated_at,
    customer_name: item.customer_name_snapshot,
    task_name: item.task_name_snapshot,
    work_content: item.work_content,
    output_description: item.output_description,
    planned_completion_date: item.planned_completion_date || "",
    progress_text: item.progress_text,
    progress_percent: item.progress_percent ?? 0,
    delay_reason: item.delay_reason,
    on_time_status: item.on_time_status,
    actual_completion_date: item.actual_completion_date || "",
    owner_id: item.owner_id,
    owner_name: item.owner_name_snapshot,
    collaborator_names: item.collaborator_names,
    document_links: item.document_links,
    attachments: attachments.map((attachment) => ({
      id: attachment.id,
      attachment_type: "attachment_type" in attachment ? attachment.attachment_type : "weekly_report",
      storage_key: "storage_key" in attachment ? attachment.storage_key : undefined,
      file_url: attachment.file_url,
      file_name: attachment.file_name,
      mime_type: "mime_type" in attachment ? attachment.mime_type : undefined,
      file_size: "file_size" in attachment ? attachment.file_size : undefined,
      description: attachment.description || "",
    })),
  }
}

function normalizeTaskFields(
  fields: ReportTemplateField[] | undefined,
  fallbackFields: DeliveryTaskFieldDefinition[],
): DeliveryTaskFieldDefinition[] {
  const known = new Set(fallbackFields.map((field) => field.code))
  const normalized = (fields || [])
    .filter((field) => known.has(field.field_code as DeliveryTaskFieldDefinition["code"]))
    .map((field) => ({
      code: field.field_code as DeliveryTaskFieldDefinition["code"],
      label: field.label,
      sort_order: Number(field.sort_order),
      default_visible: field.default_visible,
    }))
    .filter((field) => field.label && Number.isFinite(field.sort_order))
  return normalized.length ? normalized : fallbackFields
}

export interface DeliveryReportFormOptions {
  templateCode?: string
  includeCustomer?: boolean
  fallbackFields?: DeliveryTaskFieldDefinition[]
  taskCodePrefix?: string
}

export function useDeliveryReportForm(
  reportId: () => string,
  options: DeliveryReportFormOptions = {},
) {
  const templateCode = options.templateCode || "delivery_specialist_v1"
  const includeCustomer = options.includeCustomer ?? true
  const fallbackFields = options.fallbackFields || deliveryTaskFieldDefinitions
  const taskCodePrefix = options.taskCodePrefix || "delivery"
  const authStore = useAuthStore()
  const start = currentMonday()
  const report = reactive({
    id: reportId(),
    period_start: start,
    period_end: endOfWeek(start),
    summary: "",
  })
  const monthlySummary = ref("")
  const monthlyPlanLocked = ref(false)
  const isMonthlyPlanSaving = ref(false)
  const monthlyPlanErrorMessage = ref("")
  const weeklyTasks = ref<DeliveryTaskDraft[]>([])
  const dailyTasks = ref<DailyWorkTask[]>([])
  const taskFields = ref<DeliveryTaskFieldDefinition[]>(fallbackFields)
  const isLoading = ref(true)
  const isSaving = ref(false)
  const errorMessage = ref("")
  const monthKey = computed(() => report.period_start.slice(0, 7))
  const isNew = computed(() => !reportId())
  let initialized = false

  function setPeriodStart(value: string) {
    report.period_start = value
    report.period_end = endOfWeek(value)
  }

  async function loadMonthlyPlan() {
    monthlyPlanErrorMessage.value = ""
    try {
      const plan = await getMonthlyPlan(monthKey.value)
      monthlySummary.value = plan?.summary || ""
      monthlyPlanLocked.value = Boolean(plan?.id)
    } catch {
      // 月度计划表尚未初始化或本月尚未建立记录时，周报仍可先填写。
      monthlySummary.value = ""
      monthlyPlanLocked.value = false
    }
  }

  async function saveMonthlyPlanSummary(summary: string) {
    isMonthlyPlanSaving.value = true
    monthlyPlanErrorMessage.value = ""
    try {
      const plan = await saveMonthlyPlan(monthKey.value, summary)
      monthlySummary.value = plan.summary || ""
      monthlyPlanLocked.value = true
      return true
    } catch (error) {
      monthlyPlanErrorMessage.value = error instanceof Error ? error.message : "月度计划保存失败。"
      return false
    } finally {
      isMonthlyPlanSaving.value = false
    }
  }

  async function loadTaskFields() {
    try {
      const template = await getReportTemplate(templateCode)
      taskFields.value = normalizeTaskFields(template.fields, fallbackFields)
    } catch {
      // 字段字典尚未初始化时使用内置 Excel 顺序，不影响周报填写。
      taskFields.value = fallbackFields
    }
  }

  async function load() {
    isLoading.value = true
    errorMessage.value = ""
    try {
      await loadTaskFields()
      if (reportId()) {
        const detail = await getReportDetail(reportId())
        Object.assign(report, {
          id: detail.report.id,
          period_start: detail.report.period_start,
          period_end: detail.report.period_end,
          summary: detail.report.summary || "",
        })
        monthlySummary.value = detail.monthly_plan?.summary || ""
        monthlyPlanLocked.value = Boolean(detail.monthly_plan?.id)
        const attachments = detail.attachments || []
        weeklyTasks.value = detail.items.map((item) =>
          fromReportItem(
            item,
            attachments.filter((attachment) => attachment.relation_sub_id === item.id),
          ),
        )
        dailyTasks.value = detail.daily_tasks || []
      } else {
        report.id = ""
        dailyTasks.value = []
        await loadMonthlyPlan()
      }
      initialized = true
    } catch (error) {
      errorMessage.value = error instanceof Error ? error.message : "周报加载失败。"
    } finally {
      isLoading.value = false
    }
  }

  function buildPayload(): ReportPayload {
    return {
      period_start: report.period_start,
      period_end: report.period_end,
      summary: report.summary,
      risk_level: "none",
      risk_blocked: false,
      risk_reason: "",
      next_action: "",
      support_needed: "",
      expected_resolve_date: null,
      items: weeklyTasks.value.map((item, index) => ({
        task_code: taskCode(item, taskCodePrefix),
        section_code: "weekly_tasks",
        scope_type: includeCustomer ? "customer" : "overall",
        customer_name_snapshot: includeCustomer ? item.customer_name.trim() : "",
        task_name_snapshot: item.task_name.trim(),
        work_content: item.work_content,
        output_description: item.output_description,
        planned_completion_date: item.planned_completion_date || null,
        progress_text: item.progress_text,
        progress_percent: item.progress_percent,
        delay_reason: item.delay_reason,
        on_time_status: item.on_time_status,
        actual_completion_date: item.actual_completion_date || null,
        owner_id: item.owner_id,
        owner_name_snapshot: item.owner_name,
        collaborator_names: item.collaborator_names,
        document_links: item.document_links,
        sort_order: index,
      })),
      metrics: [],
      daily_tasks: dailyTasks.value.map((task) => ({
        id: task.id.startsWith("draft-") ? undefined : task.id,
        work_date: task.work_date,
        work_content: task.work_content,
      })),
      attachments: weeklyTasks.value.flatMap((item) =>
        item.attachments
          .filter((attachment) => Boolean(attachment.id) && !attachment.file)
          .map((attachment) => ({
            id: attachment.id as string,
            task_code: taskCode(item, taskCodePrefix),
          })),
      ),
    }
  }

  async function uploadPendingAttachments(detail: WeeklyReportDetail) {
    for (const task of weeklyTasks.value) {
      const item = detail.items.find((candidate) => candidate.task_code === taskCode(task, taskCodePrefix))
      for (const attachment of task.attachments) {
        const file = attachment.file
        if (!file) continue
        const uploaded = await uploadReportAttachment(
          detail.report.id,
          file,
          item?.id,
          attachment.description,
          attachment.attachment_type || "weekly_report",
        )
        Object.assign(attachment, {
          id: uploaded.id,
          attachment_type: uploaded.attachment_type,
          storage_key: uploaded.storage_key,
          file_url: uploaded.file_url,
          file_name: uploaded.file_name || attachment.file_name,
          mime_type: uploaded.mime_type,
          file_size: uploaded.file_size,
          description: uploaded.description || attachment.description,
          file: undefined,
        })
      }
    }
  }

  async function save() {
    isSaving.value = true
    errorMessage.value = ""
    try {
      const detail = reportId()
        ? await updateReport(reportId(), buildPayload())
        : await createReport(buildPayload())
      report.id = detail.report.id
      try {
        await uploadPendingAttachments(detail)
      } catch (error) {
        errorMessage.value = error instanceof Error ? error.message : "附件上传失败，请重试。"
        return ""
      }
      return detail.report.id
    } catch (error) {
      errorMessage.value = error instanceof Error ? error.message : "保存周报失败。"
      return ""
    } finally {
      isSaving.value = false
    }
  }

  watch(monthKey, async () => {
    if (initialized && isNew.value) await loadMonthlyPlan()
  })

  return {
    report, monthlySummary, monthlyPlanLocked, weeklyTasks, dailyTasks, taskFields, monthKey, isNew,
    isLoading, isSaving, errorMessage, isMonthlyPlanSaving, monthlyPlanErrorMessage,
    authStore, setPeriodStart, load, save, saveMonthlyPlanSummary,
  }
}
