<script setup lang="ts">
import { computed } from "vue"
import { useRoute, useRouter } from "vue-router"
import ScrollableTabs from "@/components/navigation/ScrollableTabs.vue"
import SharedReportsSection from "./components/SharedReportsSection.vue"

import { useAuthStore } from "@/features/auth/store"

import AllReportsView from "./all/IndexView.vue"
import SelfReportsView from "./self/IndexView.vue"
import TeamReportsView from "./team/IndexView.vue"

const authStore = useAuthStore()
const route = useRoute(), router = useRouter()
const sharedTab = computed({
 get: () => route.query.tab === "shared" ? "shared" : "reports",
 set: (tab: string) => { void router.replace({query:{...route.query,tab:tab === "shared" ? "shared" : undefined}}) },
})
const tabs = [{id:"reports",name:"周报"},{id:"shared",name:"共享周报"}]


const reportPage = computed(() => {
  const scope = authStore.effectiveRole?.scope
  if (scope === "all") return authStore.reportingRoles.length ? TeamReportsView : AllReportsView
  if (scope === "team") return TeamReportsView
  return SelfReportsView
})
</script>

<template>
  <div v-if="authStore.isAuthenticated" class="weekly-workspace">
    <div class="dashboard-card weekly-workspace-tabs"><ScrollableTabs v-model="sharedTab" :items="tabs" /></div>
    <SharedReportsSection v-if="sharedTab==='shared'" :key="authStore.user?.id" />
    <component v-else :is="reportPage" />
  </div>
</template>

<style scoped src="./IndexView.css"></style>
