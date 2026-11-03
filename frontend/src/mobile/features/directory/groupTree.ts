import type { DirectoryGroup } from "./types"

export interface DirectoryGroupTreeOption {
  group: DirectoryGroup
  depth: number
  label: string
}

function idOf(value: string | number | null | undefined): string | null {
  return value === null || value === undefined || value === "" ? null : String(value)
}

/** 将平铺分组整理为父级优先的下拉选项，并用缩进呈现层级。 */
export function buildGroupTreeOptions(groups: DirectoryGroup[]): DirectoryGroupTreeOption[] {
  const groupIds = new Set(groups.map((group) => idOf(group.id)).filter((id): id is string => Boolean(id)))
  const childrenMap = new Map<string | null, DirectoryGroup[]>()

  for (const group of groups) {
    const parentId = idOf(group.parent_group_id)
    const resolvedParentId = parentId && groupIds.has(parentId) ? parentId : null
    const siblings = childrenMap.get(resolvedParentId) ?? []
    siblings.push(group)
    childrenMap.set(resolvedParentId, siblings)
  }

  for (const siblings of childrenMap.values()) {
    siblings.sort((left, right) => left.group_name.localeCompare(right.group_name, "zh-CN"))
  }

  const options: DirectoryGroupTreeOption[] = []
  const visited = new Set<string>()
  const append = (parentId: string | null, depth: number) => {
    for (const group of childrenMap.get(parentId) ?? []) {
      const groupId = idOf(group.id)
      if (!groupId || visited.has(groupId)) continue
      visited.add(groupId)
      options.push({
        group,
        depth,
        label: `${depth ? `${"　".repeat(depth)}└─ ` : ""}${group.group_name}`,
      })
      append(groupId, depth + 1)
    }
  }

  append(null, 0)
  return options
}
