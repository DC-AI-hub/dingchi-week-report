<script setup lang="ts">
import { onMounted } from "vue"

import { useAppStore } from "@/app/stores/app"

import BackendStatusAlert from "./components/BackendStatusAlert.vue"
import CapabilityGrid from "./components/CapabilityGrid.vue"
import HomeHero from "./components/HomeHero.vue"

const appStore = useAppStore()

onMounted(() => {
  void appStore.checkBackend()
})
</script>

<template>
  <div class="page-stack">
    <HomeHero
      :backend-available="appStore.backendAvailable"
      :is-checking-backend="appStore.isCheckingBackend"
      @check-backend="appStore.checkBackend"
    />
    <BackendStatusAlert :message="appStore.backendError" />
    <CapabilityGrid />
  </div>
</template>

