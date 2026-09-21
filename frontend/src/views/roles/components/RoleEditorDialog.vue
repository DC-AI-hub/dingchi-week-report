<script setup lang="ts">
import { computed, nextTick, reactive, ref, watch } from "vue"

import NoticeBridge from "@/components/feedback/NoticeBridge.vue"
import BaseDialog from "@/components/overlay/BaseDialog.vue"
import type { DictionaryItem } from "@/features/dictionary"
import GroupTreeSelect from "@/features/directory/components/GroupTreeSelect.vue"
import type { DirectoryGroup, DirectoryRole, RoleMutationPayload } from "@/features/directory/types"

const props = withDefaults(
  defineProps<{
    open: boolean
    role?: DirectoryRole | null
    isSaving?: boolean
    isDictionaryLoading?: boolean
    scopeOptions?: DictionaryItem[]
    templateOptions?: DictionaryItem[]
    groupOptions?: DirectoryGroup[]
  }>(),
  {
    role: null,
    isSaving: false,
    isDictionaryLoading: false,
    scopeOptions: () => [],
    templateOptions: () => [],
    groupOptions: () => [],
  },
)

const emit = defineEmits<{
  close: []
  submit: [payload: RoleMutationPayload]
}>()

const emptyForm = (): RoleMutationPayload => ({
  role_code: "",
  role_name: "",
  scope: props.scopeOptions[0]?.dict_code || "",
  report_template_code: props.templateOptions[0]?.dict_code || "",
  role_group_code: props.groupOptions[0]?.group_code || "",
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
    Object.assign(form, role ? toForm(role) : emptyForm())
    formError.value = ""
    void nextTick(() => (role ? roleNameInput.value : roleCodeInput.value)?.focus())
  },
  { immediate: true },
)

watch(
  () => [props.scopeOptions, props.templateOptions, props.groupOptions],
  () => {
    if (props.open && !props.role) {
      if (!form.scope) form.scope = props.scopeOptions[0]?.dict_code || ""
      if (!form.report_template_code) {
        form.report_template_code = props.templateOptions[0]?.dict_code || ""
      }
      if (!form.role_group_code) {
        form.role_group_code = props.groupOptions[0]?.group_code || ""
      }
    }
  },
  { deep: true },
)

function toForm(role: DirectoryRole): RoleMutationPayload {
  return {
    role_code: role.role_code,
    role_name: role.role_name,
    scope: role.scope,
    report_template_code: role.report_template_code,
    role_group_code: role.role_group_code,
    description: role.description,
  }
}

function submitForm() {
  const payload: RoleMutationPayload = {
    role_code: form.role_code.trim(),
    role_name: form.role_name.trim(),
    scope: form.scope,
    report_template_code: form.report_template_code.trim(),
    role_group_code: form.role_group_code,
    description: form.description.trim(),
  }

  if (!payload.role_code || !payload.role_name || !payload.scope || !payload.report_template_code) {
    formError.value = "请完整填写角色编码、角色名称、数据范围和周报模板。"
    return
  }
  if (!props.scopeOptions.some((item) => item.dict_code === payload.scope)) {
    formError.value = "请选择有效的数据范围。"
    return
  }
  if (!props.templateOptions.some((item) => item.dict_code === payload.report_template_code)) {
    formError.value = "请选择有效的周报模板。"
    return
  }
  if (!props.groupOptions.some((item) => item.group_code === payload.role_group_code)) {
    formError.value = "请选择有效的角色分组。"
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
    :open="open"
    :title="isEditing ? '编辑角色' : '新增角色'"
    width="920px"
    @close="$emit('close')"
  >
    <form id="role-editor-form" class="role-form" @submit.prevent="submitForm">
      <NoticeBridge :warning-message="formError" />

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
          <select
            v-model="form.scope"
            :disabled="isSaving || isDictionaryLoading || !scopeOptions.length"
          >
            <option value="" disabled>
              {{ isDictionaryLoading ? "正在加载静态配置…" : "请选择数据范围" }}
            </option>
            <option v-for="item in scopeOptions" :key="item.id" :value="item.dict_code">
              {{ item.dict_name }}
            </option>
          </select>
        </label>

        <label>
          <span>周报模板</span>
          <select
            v-model="form.report_template_code"
            :disabled="isSaving || isDictionaryLoading || !templateOptions.length"
          >
            <option value="" disabled>
              {{ isDictionaryLoading ? "正在加载静态配置…" : "请选择周报模板" }}
            </option>
            <option v-for="item in templateOptions" :key="item.id" :value="item.dict_code">
              {{ item.dict_name }}
            </option>
          </select>
        </label>

        <label>
          <span>角色分组</span>
          <GroupTreeSelect
            v-model="form.role_group_code"
            :allow-empty="false"
            :disabled="isSaving || !groupOptions.length"
            empty-label="请选择角色分组"
            :groups="groupOptions"
            value-field="group_code"
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
