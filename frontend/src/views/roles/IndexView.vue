<script setup lang="ts">
import { onMounted, ref } from "vue"

import { useAuthStore } from "@/features/auth/store"
import type { DirectoryRole, RoleMutationPayload } from "@/features/directory/types"

import RoleCatalog from "./components/RoleCatalog.vue"
import RoleDeleteDialog from "./components/RoleDeleteDialog.vue"
import RoleEditorDialog from "./components/RoleEditorDialog.vue"
import RolePageHeader from "./components/RolePageHeader.vue"
import { useRoleManagement } from "./composables/useRoleManagement"

const authStore = useAuthStore()
const roleManagement = useRoleManagement()
const isEditorOpen = ref(false)
const editingRole = ref<DirectoryRole | null>(null)
const deletingRole = ref<DirectoryRole | null>(null)

function openCreateDialog() {
  editingRole.value = null
  isEditorOpen.value = true
}

function openEditDialog(role: DirectoryRole) {
  editingRole.value = role
  isEditorOpen.value = true
}

function closeEditorDialog() {
  if (!roleManagement.isSaving.value) isEditorOpen.value = false
}

async function submitRole(payload: RoleMutationPayload) {
  const isSaved = await roleManagement.saveRole(editingRole.value, payload)
  if (isSaved) isEditorOpen.value = false
}

async function confirmDelete() {
  if (!deletingRole.value) return
  const isDeleted = await roleManagement.removeRole(deletingRole.value)
  if (isDeleted) deletingRole.value = null
}

onMounted(() => {
  void roleManagement.loadRoles()
  void roleManagement.loadDictionaries()
})
</script>

<template>
  <div class="roles-page">
    <RolePageHeader @create="openCreateDialog" />

    <p v-if="roleManagement.errorMessage.value" class="page-alert" role="alert">
      {{ roleManagement.errorMessage.value }}
    </p>
    <p v-if="roleManagement.successMessage.value" class="page-success" role="status">
      {{ roleManagement.successMessage.value }}
    </p>
    <p v-if="roleManagement.dictionaryErrorMessage.value" class="page-alert" role="alert">
      {{ roleManagement.dictionaryErrorMessage.value }}
    </p>

    <RoleCatalog
      :active-role-code="authStore.activeRole?.role_code"
      :is-loading="roleManagement.isLoading.value"
      :roles="roleManagement.roles.value"
      :scope-options="roleManagement.scopeOptions.value"
      :template-options="roleManagement.templateOptions.value"
      @delete="deletingRole = $event"
      @edit="openEditDialog"
    />

    <RoleEditorDialog
      :is-dictionary-loading="roleManagement.isDictionaryLoading.value"
      :is-saving="roleManagement.isSaving.value"
      :open="isEditorOpen"
      :role="editingRole"
      :scope-options="roleManagement.scopeOptions.value"
      :template-options="roleManagement.templateOptions.value"
      @close="closeEditorDialog"
      @submit="submitRole"
    />
    <RoleDeleteDialog
      :is-deleting="roleManagement.isDeleting.value"
      :open="Boolean(deletingRole)"
      :role="deletingRole"
      @close="deletingRole = null"
      @confirm="confirmDelete"
    />
  </div>
</template>

<style scoped src="./IndexView.css"></style>
