<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue"

import { encryptPassword } from "@/shared/security/password"
import { createGroup, createUser, listGroups, listRoles, listUsers } from "@/features/directory/api"
import type { DirectoryGroup, DirectoryRole, DirectoryUser } from "@/features/directory/types"

const users = ref<DirectoryUser[]>([])
const groups = ref<DirectoryGroup[]>([])
const roles = ref<DirectoryRole[]>([])
const isLoading = ref(true)
const isSaving = ref(false)
const showUserForm = ref(false)
const showGroupForm = ref(false)
const errorMessage = ref("")
const successMessage = ref("")
const filters = reactive({ role_code: "", group_id: "" })
const userForm = reactive({ username: "", employee_no: "", display_name: "", email: "", password: "", group_id: "", manager_id: "", role_codes: ["delivery_specialist"] })
const groupForm = reactive({ group_code: "", group_name: "", description: "", parent_group_id: "" })

const managerName = computed(() => new Map(users.value.map((user) => [user.id, user.display_name])))
const roleName = (code: string) => roles.value.find((role) => role.role_code === code)?.role_name || code

async function load() {
  isLoading.value = true
  errorMessage.value = ""
  try {
    const [userData, groupData, roleData] = await Promise.all([listUsers(filters), listGroups(), listRoles()])
    users.value = userData.items; groups.value = groupData.items; roles.value = roleData.items
  } catch (error) { errorMessage.value = error instanceof Error ? error.message : "组织数据加载失败。" } finally { isLoading.value = false }
}

async function saveUser() {
  if (!userForm.username || !userForm.employee_no || !userForm.display_name || !userForm.password || !userForm.role_codes.length) { errorMessage.value = "请完整填写账号、工号、姓名、密码和角色。"; return }
  isSaving.value = true
  try {
    await createUser({ ...userForm, password: await encryptPassword(userForm.password), group_id: userForm.group_id || null, manager_id: userForm.manager_id || null })
    successMessage.value = "用户已创建。"; showUserForm.value = false; Object.assign(userForm, { username: "", employee_no: "", display_name: "", email: "", password: "", group_id: "", manager_id: "", role_codes: ["delivery_specialist"] }); await load()
  } catch (error) { errorMessage.value = error instanceof Error ? error.message : "用户创建失败。" } finally { isSaving.value = false }
}

async function saveGroup() {
  if (!groupForm.group_code || !groupForm.group_name) { errorMessage.value = "分组编码和名称不能为空。"; return }
  isSaving.value = true
  try { await createGroup({ ...groupForm, parent_group_id: groupForm.parent_group_id || null }); successMessage.value = "分组已创建。"; showGroupForm.value = false; Object.assign(groupForm, { group_code: "", group_name: "", description: "", parent_group_id: "" }); await load() } catch (error) { errorMessage.value = error instanceof Error ? error.message : "分组创建失败。" } finally { isSaving.value = false }
}

function toggleRole(code: string) { userForm.role_codes = userForm.role_codes.includes(code) ? userForm.role_codes.filter((item) => item !== code) : [...userForm.role_codes, code] }

onMounted(() => void load())
</script>

<template>
  <div class="users-page">
    <section class="directory-hero"><div><span class="section-caption">ORGANIZATION</span><h1>用户与组织</h1><p>维护人员、角色、分组和上下级关系，周报权限会随组织关系自动计算。</p></div><div class="hero-actions"><button class="ghost-button" type="button" @click="showGroupForm = !showGroupForm">{{ showGroupForm ? "收起分组表单" : "新增分组" }}</button><button class="primary-button" type="button" @click="showUserForm = !showUserForm">{{ showUserForm ? "收起用户表单" : "新增用户" }}</button></div></section>
    <p v-if="errorMessage" class="page-alert" role="alert">{{ errorMessage }}</p><p v-if="successMessage" class="page-success" role="status">{{ successMessage }}</p>
    <section v-if="showGroupForm" class="dashboard-card inline-form"><div class="section-heading"><div><span class="section-caption">NEW GROUP</span><h2>新增分组</h2></div></div><div class="form-grid"><label>分组编码<input v-model="groupForm.group_code" placeholder="delivery" /></label><label>分组名称<input v-model="groupForm.group_name" placeholder="交付中心" /></label><label>上级分组<select v-model="groupForm.parent_group_id"><option value="">无</option><option v-for="group in groups" :key="group.id" :value="group.id">{{ group.group_name }}</option></select></label><label>说明<input v-model="groupForm.description" placeholder="分组职责说明" /></label></div><div class="form-actions"><button class="primary-button" type="button" :disabled="isSaving" @click="saveGroup">保存分组</button></div></section>
    <section v-if="showUserForm" class="dashboard-card inline-form"><div class="section-heading"><div><span class="section-caption">NEW USER</span><h2>新增用户</h2></div></div><div class="form-grid"><label>登录账号<input v-model="userForm.username" placeholder="zhangsan" /></label><label>工号<input v-model="userForm.employee_no" placeholder="E1008" /></label><label>姓名<input v-model="userForm.display_name" placeholder="张三" /></label><label>邮箱<input v-model="userForm.email" type="email" placeholder="name@example.com" /></label><label>初始密码<input v-model="userForm.password" type="password" placeholder="至少 8 位" /></label><label>所属分组<select v-model="userForm.group_id"><option value="">未分组</option><option v-for="group in groups" :key="group.id" :value="group.id">{{ group.group_name }}</option></select></label><label>直属上级<select v-model="userForm.manager_id"><option value="">无</option><option v-for="user in users" :key="user.id" :value="user.id">{{ user.display_name }}（{{ user.employee_no }}）</option></select></label><fieldset><legend>角色（可多选）</legend><label v-for="role in roles" :key="role.id" class="checkbox-label"><input :checked="userForm.role_codes.includes(role.role_code)" type="checkbox" @change="toggleRole(role.role_code)" />{{ role.role_name }}</label></fieldset></div><div class="form-actions"><button class="primary-button" type="button" :disabled="isSaving" @click="saveUser">{{ isSaving ? "保存中…" : "保存用户" }}</button></div></section>

    <section class="dashboard-card directory-card"><div class="section-heading section-heading--wide"><div><span class="section-caption">DIRECTORY</span><h2>人员目录</h2></div><div class="filter-row"><select v-model="filters.role_code" @change="load"><option value="">全部角色</option><option v-for="role in roles" :key="role.id" :value="role.role_code">{{ role.role_name }}</option></select><select v-model="filters.group_id" @change="load"><option value="">全部分组</option><option v-for="group in groups" :key="group.id" :value="group.id">{{ group.group_name }}</option></select><button class="ghost-button" type="button" :disabled="isLoading" @click="load">刷新</button></div></div><div class="table-wrap"><table class="directory-table"><thead><tr><th>人员</th><th>角色</th><th>分组</th><th>直属上级</th><th>账号</th><th>状态</th></tr></thead><tbody><tr v-for="user in users" :key="user.id"><td><div class="person-cell"><span class="person-avatar" :style="{ background: user.avatar_color || '#2f80ed' }">{{ user.display_name.slice(0, 1) }}</span><div><strong>{{ user.display_name }}</strong><small>{{ user.employee_no }}</small></div></div></td><td><div class="role-tags"><span v-for="code in user.role_codes" :key="code">{{ roleName(code) }}</span></div></td><td>{{ user.group_name || "未分组" }}</td><td>{{ user.manager_id ? managerName.get(user.manager_id) || user.manager_id : "无" }}</td><td>{{ user.username }}</td><td><span class="active-status">{{ user.status === "active" ? "在职" : user.status }}</span></td></tr><tr v-if="!users.length && !isLoading"><td colspan="6" class="empty-row">暂无人员数据。</td></tr><tr v-if="isLoading"><td colspan="6" class="empty-row">正在加载…</td></tr></tbody></table></div></section>
  </div>
</template>

<style scoped src="./IndexView.css"></style>
