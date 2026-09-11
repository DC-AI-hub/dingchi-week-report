import { ref } from "vue"

import { createRole, deleteRole, listRoles, updateRole } from "@/features/directory/api"
import type { DirectoryRole, RoleMutationPayload } from "@/features/directory/types"

function getErrorMessage(error: unknown, fallback: string): string {
  return error instanceof Error ? error.message : fallback
}

export function useRoleManagement() {
  const roles = ref<DirectoryRole[]>([])
  const isLoading = ref(false)
  const isSaving = ref(false)
  const isDeleting = ref(false)
  const errorMessage = ref("")
  const successMessage = ref("")

  async function loadRoles() {
    isLoading.value = true
    errorMessage.value = ""
    try {
      roles.value = (await listRoles()).items
    } catch (error: unknown) {
      errorMessage.value = getErrorMessage(error, "角色数据加载失败。")
    } finally {
      isLoading.value = false
    }
  }

  async function saveRole(role: DirectoryRole | null, payload: RoleMutationPayload) {
    isSaving.value = true
    errorMessage.value = ""
    successMessage.value = ""
    try {
      if (role) await updateRole(role.id, payload)
      else await createRole(payload)
      successMessage.value = role ? "角色配置已更新。" : "角色已创建。"
      await loadRoles()
      return true
    } catch (error: unknown) {
      errorMessage.value = getErrorMessage(error, role ? "角色更新失败。" : "角色创建失败。")
      return false
    } finally {
      isSaving.value = false
    }
  }

  async function removeRole(role: DirectoryRole) {
    isDeleting.value = true
    errorMessage.value = ""
    successMessage.value = ""
    try {
      await deleteRole(role.id)
      successMessage.value = `角色“${role.role_name}”已删除。`
      await loadRoles()
      return true
    } catch (error: unknown) {
      errorMessage.value = getErrorMessage(error, "角色删除失败。")
      return false
    } finally {
      isDeleting.value = false
    }
  }

  return {
    roles,
    isLoading,
    isSaving,
    isDeleting,
    errorMessage,
    successMessage,
    loadRoles,
    saveRole,
    removeRole,
  }
}
