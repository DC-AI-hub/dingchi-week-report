<script setup lang="ts">
import { computed, onMounted } from "vue"
import { RouterLink, useRoute } from "vue-router"

import dingchiLogo from "@/assets/brand/dingchi-logo.png"
import sidebarDataColumns from "@/assets/dashboard/hero-data-columns.png"
import NoticeCenter from "@/components/feedback/NoticeCenter.vue"
import BackButton from "@/components/navigation/BackButton.vue"
import GlobalWatermark from "@/components/security/GlobalWatermark.vue"
import { useAuthStore } from "@/features/auth/store"
import { formatDateTime } from "@/utils/date"

import NavIcon from "./components/NavIcon.vue"
import UserProfileMenu from "./components/UserProfileMenu.vue"

const authStore = useAuthStore()
const route = useRoute()
const isPublic = computed(() => Boolean(route.meta.public))
const isDashboard = computed(() => route.path === "/")
const isSecondaryPage = computed(() => [
  "weekly-report-new",
  "weekly-report-edit",
  "weekly-report-detail",
].includes(String(route.name)))
const isSystemAdmin = computed(() => authStore.activeRole?.role_code === "system_admin")
const watermarkText = computed(() => {
  const user = authStore.user
  if (!user) return ""
  return `${user.username} · ${user.display_name}`
})
const headerDate = formatDateTime(new Date())
// 不同数据范围仍由当前角色和路由权限控制，导航统一使用“周报”作为用户可见名称。
const weeklyReportLabel = "周报"

const navItems = computed(() => [
  { label: "总览", to: "/", icon: "home" as const, visible: true },
  { label: weeklyReportLabel, to: "/weekly-reports", icon: "report" as const, visible: true },
  {
    label: "用户管理",
    to: "/users",
    icon: "users" as const,
    visible: isSystemAdmin.value,
  },
  {
    label: "职位管理",
    to: "/roles",
    icon: "roles" as const,
    visible: isSystemAdmin.value,
  },
  { label: "AI 助手", to: "/ai-chat", icon: "sparkles" as const, visible: true },
])

onMounted(() => {
  if (!isPublic.value) {
    void authStore.bootstrap()
  }
})

</script>

<template>
  <template v-if="isPublic">
    <slot />
  </template>
  <div v-else class="app-shell">
    <aside class="app-sidebar">
      <RouterLink class="brand" to="/" aria-label="返回总览">
        <span class="brand-mark">
          <img :src="dingchiLogo" alt="鼎驰" />
        </span>
        <span class="brand-name">鼎驰周报</span>
      </RouterLink>
      <nav class="side-nav" aria-label="主导航">
        <RouterLink v-for="item in navItems.filter((item) => item.visible)" :key="item.to" :to="item.to">
          <NavIcon :name="item.icon" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>
      <div class="sidebar-lower">
        <img class="sidebar-data-art" :src="sidebarDataColumns" alt="" aria-hidden="true" />
        <UserProfileMenu />
      </div>
    </aside>

    <section class="app-content">
      <header v-if="!isDashboard" class="app-header">
        <div v-if="isSecondaryPage" class="header-back">
          <BackButton :to="{ name: 'weekly-reports' }" />
        </div>
        <div class="header-context">
          <span class="header-kicker">智能周报驾驶舱</span>
          <span class="header-date">本周 {{ headerDate }}</span>
        </div>
      </header>
      <main class="app-main" :class="{ 'app-main--dashboard': isDashboard }">
        <slot />
      </main>
    </section>
    <NoticeCenter />
    <GlobalWatermark :text="watermarkText" />
  </div>
</template>

<style scoped src="./DefaultLayout.css"></style>
