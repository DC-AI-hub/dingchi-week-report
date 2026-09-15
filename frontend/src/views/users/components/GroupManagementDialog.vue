<script setup lang="ts">
import { computed, ref, watch } from "vue"

import BaseDialog from "@/components/overlay/BaseDialog.vue"
import type { DirectoryGroup } from "@/features/directory/types"

import GroupTree from "./GroupTree.vue"

const props = withDefaults(
  defineProps<{
    open: boolean
    groups?: DirectoryGroup[]
    isSaving?: boolean
  }>(),
  { groups: () => [], isSaving: false },
)

const emit = defineEmits<{
  close: []
  create: [parentGroupId: string | null]
  edit: [group: DirectoryGroup]
  delete: [group: DirectoryGroup]
}>()

const selectedId = ref<string | null>(null)
const selectedGroup = computed(() => props.groups.find((group) => group.id === selectedId.value) || null)

watch(
  () => ({ open: props.open, groups: props.groups }),
  ({ open, groups }) => {
    if (!open) return
    if (selectedId.value && groups.some((group) => group.id === selectedId.value)) return
    selectedId.value = groups[0]?.id || null
  },
  { immediate: true, deep: true },
)

function selectGroup(group: DirectoryGroup) {
  selectedId.value = group.id
}
</script>

<template>
  <BaseDialog :busy="isSaving" :open="open" title="分组管理" width="980px" @close="emit('close')">
    <div class="group-management">
      <section class="group-tree-card">
        <div class="panel-heading">
          <div>
            <span class="section-caption">HIERARCHY</span>
            <h3>组织分组</h3>
          </div>
          <button class="ghost-button" type="button" :disabled="isSaving" @click="emit('create', null)">
            新增根分组
          </button>
        </div>
        <GroupTree
          :groups="groups"
          :selected-id="selectedId"
          @create="emit('create', $event.id)"
          @delete="emit('delete', $event)"
          @edit="emit('edit', $event)"
          @select="selectGroup"
        />
      </section>

      <section class="group-detail-card">
        <template v-if="selectedGroup">
          <div class="panel-heading">
            <div>
              <span class="section-caption">GROUP DETAIL</span>
              <h3>{{ selectedGroup.group_name }}</h3>
            </div>
            <span class="group-state">{{ selectedGroup.status === "active" ? "启用" : "停用" }}</span>
          </div>
          <dl class="group-detail-list">
            <div>
              <dt>分组编码</dt>
              <dd>{{ selectedGroup.group_code }}</dd>
            </div>
            <div>
              <dt>上级分组</dt>
              <dd>
                {{ groups.find((group) => group.id === selectedGroup?.parent_group_id)?.group_name || "顶级分组" }}
              </dd>
            </div>
            <div>
              <dt>分组说明</dt>
              <dd>{{ selectedGroup.description || "暂无说明" }}</dd>
            </div>
          </dl>
        </template>
        <div v-else class="group-detail-empty">
          <h3>还没有分组</h3>
          <p>创建根分组后，可以继续添加多层级下级分组。</p>
          <button class="primary-button" type="button" :disabled="isSaving" @click="emit('create', null)">新增根分组</button>
        </div>
      </section>
    </div>
    <template #actions>
      <button class="secondary-button" type="button" :disabled="isSaving" @click="emit('close')">关闭</button>
    </template>
  </BaseDialog>
</template>

<style scoped src="./GroupManagementDialog.css"></style>
