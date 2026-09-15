<script setup lang="ts">
import { computed, ref, watch } from "vue"

import type { DirectoryGroup } from "@/features/directory/types"

interface TreeRow {
  group: DirectoryGroup
  depth: number
  hasChildren: boolean
}

const props = withDefaults(
  defineProps<{
    groups: DirectoryGroup[]
    selectedId?: string | null
  }>(),
  { selectedId: null },
)

const emit = defineEmits<{
  select: [group: DirectoryGroup]
  create: [parentGroup: DirectoryGroup]
  edit: [group: DirectoryGroup]
  delete: [group: DirectoryGroup]
}>()

const expandedIds = ref(new Set<string>())

const childrenMap = computed(() => {
  const map = new Map<string | null, DirectoryGroup[]>()
  for (const group of props.groups) {
    const parentId = group.parent_group_id && props.groups.some((item) => item.id === group.parent_group_id)
      ? group.parent_group_id
      : null
    const children = map.get(parentId) || []
    children.push(group)
    map.set(parentId, children)
  }
  for (const children of map.values()) children.sort((left, right) => left.group_name.localeCompare(right.group_name, "zh-CN"))
  return map
})

const treeRows = computed<TreeRow[]>(() => {
  const rows: TreeRow[] = []
  const visited = new Set<string>()

  function walk(parentId: string | null, depth: number) {
    for (const group of childrenMap.value.get(parentId) || []) {
      if (visited.has(group.id)) continue
      visited.add(group.id)
      const children = childrenMap.value.get(group.id) || []
      rows.push({ group, depth, hasChildren: children.length > 0 })
      if (children.length && expandedIds.value.has(group.id)) walk(group.id, depth + 1)
    }
  }

  walk(null, 0)
  for (const group of props.groups) {
    if (!visited.has(group.id)) rows.push({ group, depth: 0, hasChildren: false })
  }
  return rows
})

watch(
  () => props.groups,
  (groups) => {
    const ids = new Set(groups.map((group) => group.id))
    for (const group of groups) expandedIds.value.add(group.id)
    for (const id of expandedIds.value) if (!ids.has(id)) expandedIds.value.delete(id)
  },
  { immediate: true, deep: true },
)

function toggle(group: DirectoryGroup) {
  if (!treeRows.value.some((row) => row.group.id === group.id && row.hasChildren)) return
  const next = new Set(expandedIds.value)
  if (next.has(group.id)) next.delete(group.id)
  else next.add(group.id)
  expandedIds.value = next
}
</script>

<template>
  <div v-if="treeRows.length" class="group-tree" role="tree" aria-label="组织分组树">
    <div
      v-for="row in treeRows"
      :key="row.group.id"
      class="tree-row"
      :class="{ 'tree-row--selected': selectedId === row.group.id }"
      role="treeitem"
      :aria-level="row.depth + 1"
      :aria-selected="selectedId === row.group.id"
      :style="{ paddingLeft: `${0.6 + row.depth * 1.25}rem` }"
      @click="emit('select', row.group)"
    >
      <button
        class="tree-toggle"
        type="button"
        :aria-label="row.hasChildren ? (expandedIds.has(row.group.id) ? '收起下级分组' : '展开下级分组') : '无下级分组'"
        :disabled="!row.hasChildren"
        @click.stop="toggle(row.group)"
      >
        {{ row.hasChildren ? (expandedIds.has(row.group.id) ? '−' : '+') : '·' }}
      </button>
      <span class="tree-name">{{ row.group.group_name }}</span>
      <span class="tree-actions">
        <button class="tree-action" type="button" @click.stop="emit('create', row.group)">新增下级</button>
        <button class="tree-action" type="button" @click.stop="emit('edit', row.group)">编辑</button>
        <button class="tree-action tree-action--danger" type="button" @click.stop="emit('delete', row.group)">删除</button>
      </span>
    </div>
  </div>
  <p v-else class="tree-empty">暂无分组，先创建一个根分组。</p>
</template>

<style scoped src="./GroupTree.css"></style>
