<script setup lang="ts">
import { computed, nextTick, reactive, ref, watch } from "vue"

import BaseDialog from "@/components/overlay/BaseDialog.vue"
import type { DirectoryRole, RoleMutationPayload } from "@/features/directory/types"

const props = withDefaults(
  defineProps<{
    open: boolean
    role?: DirectoryRole | null
    isSaving?: boolean
  }>(),
  {
    role: null,
    isSaving: false,
  },
)

const emit = defineEmits<{
  close: []
  submit: [payload: RoleMutationPayload]
}>()

const emptyForm = (): RoleMutationPayload => ({
  role_code: "",
  role_name: "",
  scope: "self",
  report_template_code: "general_v1",
  description: "",
})

const form = reactive<RoleMutationPayload>(emptyForm())
const formError = ref("")
const roleCodeInput = ref<HTMLInputElement | null>(null)
const roleNameInput = ref<HTMLInputElement | null>(null)
const isEditing = computed(() => Boolean(props.role))

watch(
  () => ({ open: props.open, role: props.role }),
  ({ open, role }) => {
    if (!open) return
    Object.assign(
      form,
      role
        ? {
            role_code: role.role_code,
            role_name: role.role_name,
            scope: normalizeScope(role.scope),
            report_template_code: role.report_template_code,
            description: role.description,
          }
        : emptyForm(),
    )
    formError.value = ""
    void nextTick(() => (role ? roleNameInput.value : roleCodeInput.value)?.focus())
  },
  { immediate: true },
)

function normalizeScope(scope: string): RoleMutationPayload["scope"] {
  return scope === "team" || scope === "all" ? scope : "self"
}

function submitForm() {
  const payload: RoleMutationPayload = {
    role_code: form.role_code.trim(),
    role_name: form.role_name.trim(),
    scope: form.scope,
    report_template_code: form.report_template_code.trim(),
    description: form.description.trim(),
  }

  if (!payload.role_code || !payload.role_name || !payload.report_template_code) {
    formError.value = "请完整填写角色编码、角色名称和模板编码。"
    return
  }
  if (!/^[a-z][a-z0-9_]*$/.test(payload.role_code)) {
    formError.value = "角色编码必须以小写字母开头，只能包含小写字母、数字和下划线。"
    return
  }
  formError.value = ""
  emit("submit", payload)
}
</script>

<template>
  <BaseDialog
    :busy="isSaving"
    :description="isEditing ? '角色编码不可修改，其余配置保存后立即生效。' : '配置角色名称、数据可见范围和周报模板。'"
    :open="open"
    :title="isEditing ? '编辑角色' : '新增角色'"
    width="680px"
    @close="$emit('close')"
  >
    <form id="role-editor-form" class="role-form" @submit.prevent="submitForm">
      <p v-if="formError" class="form-error" role="alert">{{ formError }}</p>

      <div class="form-grid">
        <label>
          <span>角色编码</span>
          <input
            ref="roleCodeInput"
            v-model="form.role_code"
            autocomplete="off"
            maxlength="64"
            placeholder="project_specialist"
            :disabled="isEditing || isSaving"
          />
          <small>{{ isEditing ? "角色编码创建后不可修改" : "小写字母开头，使用下划线分隔" }}</small>
        </label>

        <label>
          <span>角色名称</span>
          <input
            ref="roleNameInput"
            v-model="form.role_name"
            autocomplete="off"
            maxlength="128"
            placeholder="项目专员"
            :disabled="isSaving"
          />
        </label>

        <label>
          <span>数据范围</span>
          <select v-model="form.scope" :disabled="isSaving">
            <option value="self">仅本人数据</option>
            <option value="team">本人及下属团队</option>
            <option value="all">全部数据</option>
          </select>
        </label>

        <label>
          <span>周报模板编码</span>
          <input
            v-model="form.report_template_code"
            autocomplete="off"
            maxlength="64"
            placeholder="project_specialist_v1"
            :disabled="isSaving"
          />
        </label>

        <label class="description-field">
          <span>角色说明</span>
          <textarea
            v-model="form.description"
            maxlength="255"
            placeholder="说明角色职责与数据边界"
            rows="4"
            :disabled="isSaving"
          ></textarea>
          <small>{{ form.description.length }}/255</small>
        </label>
      </div>
    </form>

    <template #actions>
      <button class="secondary-button" type="button" :disabled="isSaving" @click="$emit('close')">
        取消
      </button>
      <button class="primary-button" form="role-editor-form" type="submit" :disabled="isSaving">
        {{ isSaving ? "保存中…" : isEditing ? "保存修改" : "创建角色" }}
      </button>
    </template>
  </BaseDialog>
</template>

<style scoped src="./RoleEditorDialog.css"></style>
