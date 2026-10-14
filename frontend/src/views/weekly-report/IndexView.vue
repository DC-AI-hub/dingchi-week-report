<script setup lang="ts">
import { computed } from "vue"

import { useAuthStore } from "@/features/auth/store"

import AllReportsView from "./all/IndexView.vue"
import SelfReportsView from "./self/IndexView.vue"
import TeamReportsView from "./team/IndexView.vue"

const authStore = useAuthStore()

const reportPage = computed(() => {
  const scope = authStore.activeRole?.scope
  if (scope === "all") return AllReportsView
  if (scope === "team") return TeamReportsView
  return SelfReportsView
})
</script>

<template>
  <component v-if="authStore.isAuthenticated" :is="reportPage" />
</template>
