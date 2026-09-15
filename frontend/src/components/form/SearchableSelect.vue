<script setup lang="ts">
import { computed, nextTick, ref } from "vue"

type SearchableOption = {
  value: string
  label: string
  description?: string
}

const props = withDefaults(
  defineProps<{
    modelValue: string | string[]
    options: SearchableOption[]
    multiple?: boolean
    placeholder?: string
    disabled?: boolean
    ariaLabel?: string
  }>(),
  {
    multiple: false,
    placeholder: "请选择",
    disabled: false,
    ariaLabel: "选择",
  },
)

const emit = defineEmits<{
  "update:modelValue": [value: string | string[]]
}>()

const rootRef = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)
const isOpen = ref(false)
const query = ref("")

const selectedValues = computed<string[]>(() => {
  if (props.multiple) {
    return Array.isArray(props.modelValue) ? props.modelValue : []
  }
  return typeof props.modelValue === "string" && props.modelValue ? [props.modelValue] : []
})

const selectedOptions = computed(() =>
  selectedValues.value
    .map((value) => props.options.find((option) => option.value === value))
    .filter((option): option is SearchableOption => Boolean(option)),
)

const filteredOptions = computed(() => {
  const keyword = query.value.trim().toLocaleLowerCase()
  if (!keyword) return props.options
  return props.options.filter((option) =>
    [option.label, option.description || ""].some((value) =>
      value.toLocaleLowerCase().includes(keyword),
    ),
  )
})

function openList() {
  if (props.disabled) return
  isOpen.value = true
  nextTick(() => inputRef.value?.focus())
}

function handleControlMouseDown() {
  if (!props.disabled) openList()
}

function isSelected(value: string) {
  return selectedValues.value.includes(value)
}

function selectOption(option: SearchableOption) {
  if (props.multiple) {
    const values = selectedValues.value
    const next = isSelected(option.value)
      ? values.filter((value) => value !== option.value)
      : [...values, option.value]
    emit("update:modelValue", next)
    query.value = ""
    openList()
    return
  }
  emit("update:modelValue", option.value)
  query.value = ""
  isOpen.value = false
}

function removeOption(value: string) {
  if (!props.multiple) {
    emit("update:modelValue", "")
    return
  }
  emit("update:modelValue", selectedValues.value.filter((item) => item !== value))
}

function clearSingle(event: MouseEvent) {
  event.preventDefault()
  event.stopPropagation()
  emit("update:modelValue", "")
  query.value = ""
  openList()
}

function handleFocusOut() {
  window.setTimeout(() => {
    if (!rootRef.value?.contains(document.activeElement)) isOpen.value = false
  }, 0)
}
</script>

<template>
  <div
    ref="rootRef"
    class="searchable-select"
    :class="{ 'searchable-select--disabled': disabled }"
    @focusout="handleFocusOut"
  >
    <div class="searchable-select__control" @mousedown="handleControlMouseDown">
      <div v-if="multiple" class="searchable-select__chips">
        <span v-for="option in selectedOptions" :key="option.value" class="searchable-select__chip">
          {{ option.label }}
          <button
            type="button"
            aria-label="移除已选项"
            @mousedown.stop.prevent
            @click.stop="removeOption(option.value)"
          >
            移除
          </button>
        </span>
      </div>
      <span v-if="!multiple && selectedOptions[0] && !query" class="searchable-select__selected">
        {{ selectedOptions[0].label }}
      </span>
      <input
        ref="inputRef"
        v-model="query"
        class="searchable-select__input"
        :aria-label="ariaLabel"
        :disabled="disabled"
        :placeholder="selectedOptions.length ? '' : placeholder"
        autocomplete="off"
        @focus="openList"
        @keydown.esc="isOpen = false"
      />
      <button
        v-if="!multiple && selectedValues.length"
        class="searchable-select__clear"
        type="button"
        @mousedown.stop.prevent
        @click="clearSingle"
      >
        清除
      </button>
    </div>
    <div v-if="isOpen" class="searchable-select__menu" role="listbox">
      <button
        v-for="option in filteredOptions"
        :key="option.value"
        class="searchable-select__option"
        :class="{ 'searchable-select__option--selected': isSelected(option.value) }"
        type="button"
        role="option"
        :aria-selected="isSelected(option.value)"
        @mousedown.prevent
        @click="selectOption(option)"
      >
        <span>
          <strong>{{ option.label }}</strong>
          <small v-if="option.description">{{ option.description }}</small>
        </span>
        <em v-if="isSelected(option.value)">已选</em>
      </button>
      <p v-if="!filteredOptions.length" class="searchable-select__empty">暂无匹配项</p>
    </div>
  </div>
</template>

<style scoped src="./SearchableSelect.css"></style>
