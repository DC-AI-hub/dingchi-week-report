<script setup lang="ts">
import { RouterLink } from "vue-router"

defineProps<{
  backendAvailable: boolean
  isCheckingBackend: boolean
}>()

const emit = defineEmits<{
  checkBackend: []
}>()
</script>

<template>
  <section class="hero-card surface-card">
    <div>
      <span class="eyebrow">LOCAL WORKSPACE</span>
      <h1>周报系统开发底座已就绪</h1>
      <p>
        Vue 负责交互，Django 提供业务 API，MCP 暴露 AI 工具；MySQL 与 Redis
        承载持久化和缓存能力。
      </p>
      <div class="hero-actions">
        <RouterLink class="primary-button" to="/ai-chat">打开 AI 助手</RouterLink>
        <button class="secondary-button" type="button" @click="emit('checkBackend')">
          {{ isCheckingBackend ? "检测中..." : "检测后端" }}
        </button>
      </div>
    </div>

    <div class="status-orbit" :class="{ online: backendAvailable }">
      <span class="status-dot" />
      <strong>{{ backendAvailable ? "API ONLINE" : "API OFFLINE" }}</strong>
      <small>/api/v1/health/live/</small>
    </div>
  </section>
</template>

<style scoped src="./HomeHero.css"></style>
