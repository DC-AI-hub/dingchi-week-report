<script setup lang="ts">
import BaseDialog from "@/components/overlay/BaseDialog.vue"
import type { DirectoryRole } from "@/features/directory/types"

withDefaults(
  defineProps<{
    open: boolean
    role?: DirectoryRole | null
    isDeleting?: boolean
  }>(),
  {
    role: null,
    isDeleting: false,
  },
)

defineEmits<{
  close: []
  confirm: []
}>()
</script>

<template>
  <BaseDialog
    :busy="isDeleting"
    description="删除后该角色不再出现在角色列表和用户可选角色中。"
    :open="open"
    title="删除角色"
    width="480px"
    @close="$emit('close')"
  >
    <div v-if="role" class="delete-content">
      <p>
        确认删除角色“<strong>{{ role.role_name }}</strong>”吗？
      </p>
      <div class="role-summary">
        <span>角色编码</span>
        <strong>{{ role.role_code }}</strong>
      </div>
      <p class="delete-note">历史周报数据会保留，已分配此角色的用户将无法再切换到该角色。</p>
    </div>

    <template #actions>
      <button class="secondary-button" type="button" :disabled="isDeleting" @click="$emit('close')">
        取消
      </button>
      <button class="danger-button" type="button" :disabled="isDeleting" @click="$emit('confirm')">
        {{ isDeleting ? "删除中…" : "确认删除" }}
      </button>
    </template>
  </BaseDialog>
</template>

<style scoped src="./RoleDeleteDialog.css"></style>
