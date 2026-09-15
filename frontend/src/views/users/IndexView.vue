<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue"

import {
  createGroup,
  createUser,
  deleteGroup,
  deleteUser,
  listGroups,
  listRoles,
  listUsers,
  updateGroup,
  updateUser,
} from "@/features/directory/api"
import type {
  DirectoryGroup,
  DirectoryRole,
  DirectoryUser,
  GroupMutationPayload,
  UserMutationPayload,
} from "@/features/directory/types"
import { encryptPassword } from "@/shared/security/password"

import ConfirmDeleteDialog from "./components/ConfirmDeleteDialog.vue"
import GroupEditorDialog from "./components/GroupEditorDialog.vue"
import GroupManagementDialog from "./components/GroupManagementDialog.vue"
import UserDetailDialog from "./components/UserDetailDialog.vue"
import UserEditorDialog from "./components/UserEditorDialog.vue"

const users = ref<DirectoryUser[]>([])
const groups = ref<DirectoryGroup[]>([])
const roles = ref<DirectoryRole[]>([])
const isLoading = ref(true)
const isSaving = ref(false)
const isDeleting = ref(false)
const isGroupManagementOpen = ref(false)
const isGroupEditorOpen = ref(false)
const editingGroup = ref<DirectoryGroup | null>(null)
const newGroupParentId = ref<string | null>(null)
const isUserEditorOpen = ref(false)
const editingUser = ref<DirectoryUser | null>(null)
const viewingUser = ref<DirectoryUser | null>(null)
const deletingTarget = ref<
  | { kind: "group"; item: DirectoryGroup }
  | { kind: "user"; item: DirectoryUser }
  | null
>(null)
const errorMessage = ref("")
const successMessage = ref("")
const filters = reactive({ role_code: "", group_id: "" })

const managerName = computed(() => new Map(users.value.map((user) => [user.id, user.display_name])))
const roleName = (code: string) => roles.value.find((role) => role.role_code === code)?.role_name || code

const deleteTitle = computed(() => (deletingTarget.value?.kind === "group" ? "删除分组" : "删除用户"))
const deleteMessage = computed(() => {
  const target = deletingTarget.value
  if (!target) return ""
  if (target.kind === "group") return `确认删除分组“${target.item.group_name}”吗？有下级分组或在职成员时无法删除。`
  return `确认删除用户“${target.item.display_name}”吗？删除后该用户将无法登录，历史周报会保留；仍有直属下属时无法删除。`
})

function messageFromError(error: unknown, fallback: string) {
  return error instanceof Error ? error.message : fallback
}

async function load() {
  isLoading.value = true
  errorMessage.value = ""
  try {
    const [userData, groupData, roleData] = await Promise.all([
      listUsers(filters),
      listGroups(),
      listRoles(),
    ])
    users.value = userData.items
    groups.value = groupData.items
    roles.value = roleData.items
  } catch (error) {
    errorMessage.value = messageFromError(error, "组织数据加载失败。")
  } finally {
    isLoading.value = false
  }
}

function openCreateGroup(parentGroupId: string | null = null) {
  editingGroup.value = null
  newGroupParentId.value = parentGroupId
  isGroupEditorOpen.value = true
}

function openEditGroup(group: DirectoryGroup) {
  editingGroup.value = group
  newGroupParentId.value = null
  isGroupEditorOpen.value = true
}

function closeGroupEditor() {
  if (!isSaving.value) isGroupEditorOpen.value = false
}

async function submitGroup(payload: GroupMutationPayload) {
  isSaving.value = true
  errorMessage.value = ""
  try {
    if (editingGroup.value) await updateGroup(editingGroup.value.id, payload)
    else await createGroup(payload)
    successMessage.value = editingGroup.value ? "分组已更新。" : "分组已创建。"
    isGroupEditorOpen.value = false
    await load()
  } catch (error) {
    errorMessage.value = messageFromError(error, "分组保存失败。")
  } finally {
    isSaving.value = false
  }
}

function openCreateUser() {
  editingUser.value = null
  isUserEditorOpen.value = true
}

function openEditUser(user: DirectoryUser) {
  editingUser.value = user
  isUserEditorOpen.value = true
}

function closeUserEditor() {
  if (!isSaving.value) isUserEditorOpen.value = false
}

async function submitUser(payload: UserMutationPayload) {
  isSaving.value = true
  errorMessage.value = ""
  try {
    const commonPayload = {
      username: payload.username,
      employee_no: payload.employee_no,
      display_name: payload.display_name,
      email: payload.email,
      group_id: payload.group_id || null,
      manager_id: payload.manager_id || null,
      role_codes: payload.role_codes,
      status: payload.status || "active",
    }
    const encryptedPassword = payload.password ? await encryptPassword(payload.password) : ""
    if (editingUser.value) {
      await updateUser(editingUser.value.id, {
        ...commonPayload,
        ...(encryptedPassword ? { password: encryptedPassword } : {}),
      })
    } else {
      if (!encryptedPassword) throw new Error("请设置初始密码。")
      await createUser({ ...commonPayload, password: encryptedPassword })
    }
    successMessage.value = editingUser.value ? "用户已更新。" : "用户已创建。"
    isUserEditorOpen.value = false
    await load()
  } catch (error) {
    errorMessage.value = messageFromError(error, "用户保存失败。")
  } finally {
    isSaving.value = false
  }
}

function requestDeleteGroup(group: DirectoryGroup) {
  deletingTarget.value = { kind: "group", item: group }
}

function requestDeleteUser(user: DirectoryUser) {
  deletingTarget.value = { kind: "user", item: user }
}

async function confirmDelete() {
  const target = deletingTarget.value
  if (!target) return
  isDeleting.value = true
  errorMessage.value = ""
  try {
    if (target.kind === "group") await deleteGroup(target.item.id)
    else await deleteUser(target.item.id)
    successMessage.value = target.kind === "group" ? "分组已删除。" : "用户已删除。"
    deletingTarget.value = null
    await load()
  } catch (error) {
    errorMessage.value = messageFromError(error, "删除失败。")
  } finally {
    isDeleting.value = false
  }
}

onMounted(() => void load())
</script>

<template>
  <div class="users-page">
    <section class="directory-hero">
      <div>
        <span class="section-caption">ORGANIZATION</span>
        <h1>用户与组织</h1>
        <p>维护人员、角色、分组和上下级关系，周报权限会随组织关系自动计算。</p>
      </div>
      <div class="hero-actions">
        <button class="ghost-button" type="button" @click="isGroupManagementOpen = true">分组管理</button>
        <button class="primary-button" type="button" @click="openCreateUser">新增用户</button>
      </div>
    </section>

    <p v-if="errorMessage" class="page-alert" role="alert">{{ errorMessage }}</p>
    <p v-if="successMessage" class="page-success" role="status">{{ successMessage }}</p>

    <section class="dashboard-card directory-card">
      <div class="directory-heading">
        <div>
          <span class="section-caption">DIRECTORY</span>
          <h2>人员目录</h2>
        </div>
        <div class="filter-row">
          <select v-model="filters.role_code" aria-label="按角色筛选" @change="load">
            <option value="">全部角色</option>
            <option v-for="role in roles" :key="role.id" :value="role.role_code">{{ role.role_name }}</option>
          </select>
          <select v-model="filters.group_id" aria-label="按分组筛选" @change="load">
            <option value="">全部分组</option>
            <option v-for="group in groups" :key="group.id" :value="group.id">{{ group.group_name }}</option>
          </select>
          <button class="ghost-button" type="button" :disabled="isLoading" @click="load">刷新</button>
        </div>
      </div>

      <div class="table-wrap">
        <table class="directory-table">
          <thead>
            <tr>
              <th>人员</th>
              <th>角色</th>
              <th>分组</th>
              <th>直属上级</th>
              <th>账号</th>
              <th>状态</th>
              <th class="actions-column">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>
                <div class="person-cell">
                  <span class="person-avatar" :style="{ background: user.avatar_color || '#2f80ed' }">{{ user.display_name.slice(0, 1) }}</span>
                  <div>
                    <strong>{{ user.display_name }}</strong>
                    <small>{{ user.employee_no }}</small>
                  </div>
                </div>
              </td>
              <td>
                <div class="role-tags">
                  <span v-for="code in user.role_codes" :key="code">{{ roleName(code) }}</span>
                </div>
              </td>
              <td>{{ user.group_name || "未分组" }}</td>
              <td>{{ user.manager_id ? managerName.get(user.manager_id) || "未知" : "无" }}</td>
              <td>{{ user.username }}</td>
              <td><span class="active-status">{{ user.status === "active" ? "在职" : "停用" }}</span></td>
              <td>
                <div class="row-actions">
                  <button class="row-action" type="button" @click="viewingUser = user">查看</button>
                  <button class="row-action" type="button" @click="openEditUser(user)">编辑</button>
                  <button class="row-action row-action--danger" type="button" @click="requestDeleteUser(user)">删除</button>
                </div>
              </td>
            </tr>
            <tr v-if="!users.length && !isLoading"><td colspan="7" class="empty-row">暂无人员数据。</td></tr>
            <tr v-if="isLoading"><td colspan="7" class="empty-row">正在加载…</td></tr>
          </tbody>
        </table>
      </div>
    </section>

    <GroupManagementDialog
      :groups="groups"
      :is-saving="isSaving"
      :open="isGroupManagementOpen"
      @close="isGroupManagementOpen = false"
      @create="openCreateGroup"
      @delete="requestDeleteGroup"
      @edit="openEditGroup"
    />
    <GroupEditorDialog
      :group="editingGroup"
      :groups="groups"
      :initial-parent-group-id="newGroupParentId"
      :is-saving="isSaving"
      :open="isGroupEditorOpen"
      @close="closeGroupEditor"
      @submit="submitGroup"
    />
    <UserEditorDialog
      :groups="groups"
      :is-saving="isSaving"
      :open="isUserEditorOpen"
      :roles="roles"
      :user="editingUser"
      :users="users"
      @close="closeUserEditor"
      @submit="submitUser"
    />
    <UserDetailDialog :open="Boolean(viewingUser)" :user="viewingUser" :users="users" @close="viewingUser = null" />
    <ConfirmDeleteDialog
      :is-deleting="isDeleting"
      :message="deleteMessage"
      :open="Boolean(deletingTarget)"
      :title="deleteTitle"
      @close="deletingTarget = null"
      @confirm="confirmDelete"
    />
  </div>
</template>

<style scoped src="./IndexView.css"></style>
