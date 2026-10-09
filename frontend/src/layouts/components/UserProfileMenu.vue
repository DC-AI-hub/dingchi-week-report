<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue"
import { useRouter } from "vue-router"

import { useAppStore } from "@/app/stores/app"
import NoticeBridge from "@/components/feedback/NoticeBridge.vue"
import { useAuthStore } from "@/features/auth/store"
import ChangePasswordDialog from "./ChangePasswordDialog.vue"

const appStore = useAppStore()
const authStore = useAuthStore()
const router = useRouter()
const menuElement = ref<HTMLElement | null>(null)
const isOpen = ref(false)
const isChangingRole = ref(false)
const isChangePasswordOpen = ref(false)
const displayName = computed(() => {
  const rawName = authStore.user?.display_name?.trim() || "未登录"
  const nameParts = rawName.split(/[·•]/).map((part) => part.trim()).filter(Boolean)
  return nameParts[nameParts.length - 1] || rawName
})

function scopeLabel(scope: string) {
  return scope === "all" ? "全员数据" : scope === "team" ? "团队数据" : "个人数据"
}

function handleDocumentPointerDown(event: PointerEvent) {
  if (!isOpen.value || menuElement.value?.contains(event.target as Node)) return
  isOpen.value = false
}

function handleDocumentKeyDown(event: KeyboardEvent) {
  if (event.key === "Escape") isOpen.value = false
}

async function handleRoleSelect(roleCode: string) {
  if (isChangingRole.value) return
  if (roleCode === authStore.activeRole?.role_code) {
    isOpen.value = false
    return
  }

  isChangingRole.value = true
  try {
    await authStore.changeRole(roleCode)
    isOpen.value = false
    router.go(0)
  } finally {
    isChangingRole.value = false
  }
}

function openChangePassword() {
  isOpen.value = false
  isChangePasswordOpen.value = true
}

async function handleSignOut() {
  await authStore.signOut()
  isOpen.value = false
  await router.push("/login")
}

onMounted(() => {
  document.addEventListener("pointerdown", handleDocumentPointerDown)
  document.addEventListener("keydown", handleDocumentKeyDown)
})

onBeforeUnmount(() => {
  document.removeEventListener("pointerdown", handleDocumentPointerDown)
  document.removeEventListener("keydown", handleDocumentKeyDown)
})
</script>

<template>
  <div ref="menuElement" class="sidebar-profile">
    <button
      class="profile-trigger"
      :class="{ 'profile-trigger--open': isOpen }"
      type="button"
      :aria-expanded="isOpen"
      aria-haspopup="dialog"
      @click="isOpen = !isOpen"
    >
      <span class="profile-copy">
        <strong>{{ displayName }}</strong>
        <small>{{ authStore.activeRole?.role_name || "暂无职位" }}</small>
      </span>
      <span class="profile-caret" aria-hidden="true">›</span>
    </button>

    <Transition name="profile-popover">
      <section v-if="isOpen" class="profile-panel" role="dialog" aria-label="用户信息与职位切换">
        <div class="profile-panel-head">
          <span class="profile-panel-avatar" :style="{ background: authStore.user?.avatar_color || '#16a6d8' }">
            {{ authStore.user?.display_name?.slice(-1) || "我" }}
          </span>
          <div>
            <strong>{{ displayName }}</strong>
            <span>{{ authStore.activeRole?.role_name || "暂无职位" }}</span>
            <small>{{ authStore.user?.employee_no || authStore.user?.username || "本地账号" }}</small>
          </div>
        </div>

        <div class="profile-role-section">
          <span class="profile-section-label">切换职位</span>
          <div class="profile-role-list">
            <button
              v-for="role in authStore.roles"
              :key="role.role_code"
              class="profile-role-option"
              :class="{ 'profile-role-option--active': role.role_code === authStore.activeRole?.role_code }"
              type="button"
              :disabled="isChangingRole"
              @click="handleRoleSelect(role.role_code)"
            >
              <span>{{ role.role_name }}</span>
              <small>{{ scopeLabel(role.scope) }}</small>
              <i aria-hidden="true" />
            </button>
          </div>
        </div>

        <NoticeBridge :warning-message="authStore.errorMessage" />

        <div class="profile-panel-actions">
          <button type="button" @click="appStore.toggleTheme">
            {{ appStore.theme === "light" ? "切换深色" : "切换浅色" }}
          </button>
          <button type="button" @click="openChangePassword">修改密码</button>
          <button class="profile-signout" type="button" @click="handleSignOut">退出登录</button>
        </div>
      </section>
    </Transition>

    <ChangePasswordDialog :open="isChangePasswordOpen" @close="isChangePasswordOpen = false" />
  </div>
</template>

<style scoped src="./UserProfileMenu.css"></style>
