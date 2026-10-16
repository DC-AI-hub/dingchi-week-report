import { ref } from "vue"
import { emptyDeliveryTask, type DeliveryTaskDraft } from "@/features/weekly-report/delivery-specialist/types"
import type { DeliveryTaskCollectionProps } from "@/features/weekly-report/composables/useDeliveryTaskCollection"

export function useFunctionalTaskEditor(props: DeliveryTaskCollectionProps, emit: (event: "update:tasks", tasks: DeliveryTaskDraft[]) => void) {
  const editorOpen = ref(false)
  const editorKey = ref(0)
  const editingIndex = ref(-1)
  const editingTask = ref<DeliveryTaskDraft | null>(null)
  const detailOpen = ref(false)
  const detailTask = ref<DeliveryTaskDraft | null>(null)
  function addTask() {
    editingIndex.value = -1
    editingTask.value = null
    editorOpen.value = true
  }
  function editTask(index: number) {
    editingIndex.value = index
    editingTask.value = { ...props.tasks[index] }
    editorOpen.value = true
  }

  function currentLocalTimestamp() {
    const value = new Date()
    const pad = (part: number) => String(part).padStart(2, "0")
    return `${value.getFullYear()}-${pad(value.getMonth() + 1)}-${pad(value.getDate())}T${pad(value.getHours())}:${pad(value.getMinutes())}:${pad(value.getSeconds())}`
  }

  function saveTask(task: DeliveryTaskDraft, action: "close" | "next") {
    const normalizedTask: DeliveryTaskDraft = {
      ...emptyDeliveryTask(props.ownerName),
      ...task,
      customer_name: task.customer_name.trim(),
      task_name: task.task_name.trim(),
      owner_name: task.owner_name || props.ownerName || "",
      updated_at: currentLocalTimestamp(),
    }
    const next = [...props.tasks]
    if (editingIndex.value < 0) {
      next.push(normalizedTask)
    }
    else next.splice(editingIndex.value, 1, normalizedTask)
    emit("update:tasks", next)
    if (action === "close") {
      editorOpen.value = false
      return
    }

    // 继续填写时重新创建编辑器，清空上一条任务的表单并保留弹窗打开状态。
    editingIndex.value = -1
    editingTask.value = null
    editorKey.value += 1
  }

  function openTaskDetail(task: DeliveryTaskDraft) {
    detailTask.value = task
    detailOpen.value = true
  }

  return { editorOpen, editorKey, editingTask, detailOpen, detailTask, addTask, editTask, saveTask, openTaskDetail }
}
