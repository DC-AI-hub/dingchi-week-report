<script setup lang="ts">
interface Capability {
  index: string
  title: string
  description: string
}

const capabilities: Capability[] = [
  {
    index: "01",
    title: "前端分层",
    description: "路由、Pinia、功能模块与共享请求层彼此解耦。",
  },
  {
    index: "02",
    title: "业务 API",
    description: "所有 REST 风格接口统一收口到 /api 前缀。",
  },
  {
    index: "03",
    title: "MCP 服务",
    description: "Streamable HTTP 端点统一位于 /mcp/。",
  },
  {
    index: "04",
    title: "基础设施",
    description: "MySQL、Redis 和大模型参数均由环境变量注入。",
  },
]
</script>

<template>
  <section class="capability-grid" aria-label="项目能力">
    <article v-for="capability in capabilities" :key="capability.index" class="capability-card">
      <span>{{ capability.index }}</span>
      <h2>{{ capability.title }}</h2>
      <p>{{ capability.description }}</p>
    </article>
  </section>
</template>

<style scoped src="./CapabilityGrid.css"></style>
