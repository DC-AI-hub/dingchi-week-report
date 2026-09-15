<script setup lang="ts">
import type { DirectoryRole } from "@/features/directory/types"
import type { DictionaryItem } from "@/features/dictionary"

const props = withDefaults(
  defineProps<{
    roles: DirectoryRole[]
    isLoading?: boolean
    activeRoleCode?: string
    scopeOptions?: DictionaryItem[]
    templateOptions?: DictionaryItem[]
  }>(),
  {
    isLoading: false,
    activeRoleCode: "",
    scopeOptions: () => [],
    templateOptions: () => [],
  },
)

defineEmits<{
  edit: [role: DirectoryRole]
  delete: [role: DirectoryRole]
}>()

function dictionaryLabel(options: DictionaryItem[], code: string): string {
  return options.find((item) => item.dict_code === code)?.dict_name || code
}

function scopeLabel(scope: string): string {
  return dictionaryLabel(props.scopeOptions, scope)
}

function templateLabel(templateCode: string): string {
  return dictionaryLabel(props.templateOptions, templateCode)
}

function deleteDisabledReason(role: DirectoryRole): string {
  if (role.role_code === "system_admin") return "系统管理员角色受保护，不能删除"
  if (role.role_code === props.activeRoleCode) return "当前正在使用的角色不能删除"
  return ""
}
</script>

<template>
  <section aria-label="角色列表" class="role-grid">
    <article v-for="role in roles" :key="role.id" class="dashboard-card role-card">
      <div class="role-card__heading">
        <div class="role-identity">
          <span class="role-mark" aria-hidden="true">{{ role.role_name.slice(0, 1) }}</span>
          <div class="role-title">
            <h2>{{ role.role_name }}</h2>
            <span>{{ role.role_code }}</span>
          </div>
        </div>
        <span class="scope-badge">{{ scopeLabel(role.scope) }}</span>
      </div>

      <p class="role-description">{{ role.description || "暂无角色说明" }}</p>

      <dl class="role-details">
        <div>
          <dt>周报模板</dt>
          <dd :title="role.report_template_code">{{ templateLabel(role.report_template_code) }}</dd>
        </div>
        <div>
          <dt>可见范围</dt>
          <dd>{{ scopeLabel(role.scope) }}</dd>
        </div>
        <div>
          <dt>状态</dt>
          <dd :class="{ 'status-active': role.status === 'active' }">
            {{ role.status === "active" ? "启用" : "停用" }}
          </dd>
        </div>
      </dl>

      <div class="role-actions">
        <button class="edit-button" type="button" @click="$emit('edit', role)">编辑</button>
        <button
          class="delete-button"
          type="button"
          :disabled="Boolean(deleteDisabledReason(role))"
          :title="deleteDisabledReason(role)"
          @click="$emit('delete', role)"
        >
          删除
        </button>
      </div>
    </article>

    <article v-if="isLoading" class="dashboard-card empty-card" aria-live="polite">
      正在加载角色数据…
    </article>
    <article v-else-if="!roles.length" class="dashboard-card empty-card">
      暂无角色数据，可以通过“新增角色”创建第一条角色配置。
    </article>
  </section>
</template>

<style scoped src="./RoleCatalog.css"></style>
