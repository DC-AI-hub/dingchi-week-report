import { ref } from "vue"

import { listDictionaryItems } from "@/features/dictionary"
import type { DictionaryItem } from "@/features/dictionary"
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
  const scopeOptions = ref<DictionaryItem[]>([])
  const templateOptions = ref<DictionaryItem[]>([])
  const isDictionaryLoading = ref(false)
  const dictionaryErrorMessage = ref("")

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

  async function loadDictionaries() {
    isDictionaryLoading.value = true
    dictionaryErrorMessage.value = ""
    try {
      const [scopes, templates] = await Promise.all([
        listDictionaryItems("role_scope"),
        listDictionaryItems("report_template"),
      ])
      scopeOptions.value = scopes.items
      templateOptions.value = templates.items
    } catch (error: unknown) {
      dictionaryErrorMessage.value = getErrorMessage(error, "静态配置加载失败，请联系管理员。")
    } finally {
      isDictionaryLoading.value = false
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
    scopeOptions,
    templateOptions,
    isDictionaryLoading,
    dictionaryErrorMessage,
    loadRoles,
    loadDictionaries,
    saveRole,
    removeRole,
  }
}
