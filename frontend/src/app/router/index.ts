import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router"

import { useAuthStore } from "@/features/auth/store"

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    name: "dashboard",
    component: () => import("@/views/dashboard/IndexView.vue"),
    meta: { title: "周报总览", requiresAuth: true },
  },
  {
    path: "/login",
    name: "login",
    component: () => import("@/views/login/IndexView.vue"),
    meta: { title: "登录", public: true },
  },
  {
    path: "/weekly-reports",
    name: "weekly-reports",
    component: () => import("@/views/weekly-report/IndexView.vue"),
    meta: { title: "我的周报", requiresAuth: true },
  },
  {
    path: "/weekly-reports/new",
    name: "weekly-report-new",
    component: () => import("@/views/weekly-report/EditView.vue"),
    meta: { title: "填写周报", requiresAuth: true },
  },
  {
    path: "/weekly-reports/:reportId/edit",
    name: "weekly-report-edit",
    component: () => import("@/views/weekly-report/EditView.vue"),
    meta: { title: "编辑周报", requiresAuth: true },
  },
  {
    path: "/weekly-reports/review",
    name: "weekly-report-review",
    component: () => import("@/views/weekly-report/ReviewView.vue"),
    meta: { title: "待我审核", requiresAuth: true },
  },
  {
    path: "/weekly-reports/:reportId",
    name: "weekly-report-detail",
    component: () => import("@/views/weekly-report/DetailView.vue"),
    meta: { title: "周报详情", requiresAuth: true },
  },
  {
    path: "/users",
    name: "users",
    component: () => import("@/views/users/IndexView.vue"),
    meta: { title: "用户管理", requiresAuth: true },
  },
  {
    path: "/roles",
    name: "roles",
    component: () => import("@/views/roles/IndexView.vue"),
    meta: { title: "角色管理", requiresAuth: true },
  },
  {
    path: "/ai-chat",
    name: "ai-chat",
    component: () => import("@/views/chat/IndexView.vue"),
    meta: { title: "AI 助手", requiresAuth: true },
  },
  {
    path: "/:pathMatch(.*)*",
    name: "not-found",
    component: () => import("@/views/not-found/IndexView.vue"),
    meta: { title: "页面不存在" },
  },
]

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()
  if (to.meta.public) {
    if (to.name === "login" && authStore.isAuthenticated) return { name: "dashboard" }
    return true
  }
  await authStore.bootstrap()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { name: "login", query: { redirect: to.fullPath } }
  }
  return true
})

router.afterEach((to) => {
  const appTitle = import.meta.env.VITE_APP_TITLE || "鼎驰周报"
  document.title = to.meta.title ? String(to.meta.title) + " | " + appTitle : appTitle
})
