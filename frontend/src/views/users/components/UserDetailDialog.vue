<script setup lang="ts">
import { computed } from "vue"

import BaseDialog from "@/components/overlay/BaseDialog.vue"
import type { DirectoryUser } from "@/features/directory/types"

const props = withDefaults(
  defineProps<{
    open: boolean
    user?: DirectoryUser | null
    users?: DirectoryUser[]
  }>(),
  { user: null, users: () => [] },
)

const managerDisplayName = computed(() => {
  const ids = props.user?.manager_ids || (props.user?.manager_id ? [props.user.manager_id] : [])
  return ids.map((id, index) => `${index + 1}. ${props.users?.find((item) => item.id === id)?.display_name || "未知"}`).join(" → ") || "无"
})

const emit = defineEmits<{
  close: []
}>()
</script>

<template>
  <BaseDialog :open="open" title="查看用户" width="620px" @close="emit('close')">
    <div v-if="user" class="user-detail">
      <div class="detail-profile">
        <span class="detail-avatar" :style="{ background: user.avatar_color || '#2f80ed' }">{{ user.display_name.slice(0, 1) }}</span>
        <div>
          <h3>{{ user.display_name }}</h3>
          <p>{{ user.employee_no }} · {{ user.status === "active" ? "在职" : "停用" }}</p>
        </div>
      </div>
      <dl class="detail-grid">
        <div><dt>登录账号</dt><dd>{{ user.username }}</dd></div>
        <div><dt>邮箱</dt><dd>{{ user.email || "未填写" }}</dd></div>
        <div><dt>手机号</dt><dd>{{ user.phone || "未填写" }}</dd></div>
        <div><dt>所属分组</dt><dd>{{ user.group_name || "未分组" }}</dd></div>
        <div><dt>直属上级</dt><dd>{{ managerDisplayName }}</dd></div>
        <div class="detail-grid__wide"><dt>职位</dt><dd class="detail-roles">{{ user.role_names.length ? user.role_names.join("、") : "未分配" }}</dd></div>
      </dl>
    </div>
    <template #actions>
      <button class="secondary-button" type="button" @click="emit('close')">关闭</button>
    </template>
  </BaseDialog>
</template>

<style scoped src="./UserDetailDialog.css"></style>
