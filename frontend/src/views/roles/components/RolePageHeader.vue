<script setup lang="ts">
defineEmits<{
  create: []
}>()
</script>

<template>
  <section class="roles-hero">
    <div>
      <h1>角色管理</h1>
      <p>配置角色的数据范围和周报模板，用户与组织关系请在用户管理中维护。</p>
    </div>
    <button class="primary-button" type="button" @click="$emit('create')">新增角色</button>
  </section>
</template>

<style scoped src="./RolePageHeader.css"></style>
