<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue"

import SearchableSelect from "@/components/form/SearchableSelect.vue"
import type { DirectoryUserOption } from "../types"

const props = defineProps<{
  modelValue: string | string[] | null
  users: DirectoryUserOption[]
  multiple?: boolean
  disabled?: boolean
  ariaLabel?: string
  placeholder?: string
  ordered?: boolean
}>()
const select = ref<{ $el: HTMLElement } | null>(null)
const panelStyle = ref<Record<string,string>>({})
let observer: MutationObserver | undefined
async function updatePanel() {
  await nextTick()
  const root=select.value?.$el
  const rect=root?.getBoundingClientRect()
  const menu=root?.querySelector<HTMLElement>(".searchable-select__menu")
  if(!rect || !menu)return
  const width=menu.getBoundingClientRect().width
  const left=Math.max(12,Math.min(rect.left,window.innerWidth-width-12))
  panelStyle.value={"--person-menu-offset":`${left-rect.left}px`}
}
onMounted(()=>{
  window.addEventListener("resize",updatePanel)
  observer=new MutationObserver(()=>void updatePanel())
  if(select.value?.$el)observer.observe(select.value.$el,{childList:true,subtree:true,characterData:true})
})
onBeforeUnmount(()=>{observer?.disconnect();window.removeEventListener("resize",updatePanel)})
const emit = defineEmits<{ "update:modelValue": [value: string | string[]] }>()
const options = computed(() => props.users.map((user) => ({
  value: user.id, label: user.display_name,
  description: [user.employee_no, user.username].filter(Boolean).join(" · "),
  group: user.group_name || "未分组",
})).sort((a, b) => a.group.localeCompare(b.group, "zh-CN") || a.label.localeCompare(b.label, "zh-CN")))
</script>

<template>
  <SearchableSelect
    ref="select"
    :style="panelStyle"
    @pointerdown.capture="updatePanel"
    @focusin.capture="updatePanel"
    :model-value="modelValue || (multiple ? [] : '')"
    :options="options"
    :multiple="multiple"
    :disabled="disabled"
    :show-selection-order="ordered"
    :aria-label="ariaLabel || '选择人员'"
    :placeholder="placeholder || '按姓名、账号、工号或分组搜索'"
    @update:model-value="emit('update:modelValue', $event)"
  />
</template>

<style scoped src="./PersonSelect.css"></style>
