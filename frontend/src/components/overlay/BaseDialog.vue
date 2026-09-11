<script setup lang="ts">
import { onBeforeUnmount, watch } from "vue"

const props = withDefaults(
  defineProps<{
    open: boolean
    title: string
    description?: string
    busy?: boolean
    width?: string
  }>(),
  {
    description: "",
    busy: false,
    width: "640px",
  },
)

const emit = defineEmits<{
  close: []
}>()

function requestClose() {
  if (!props.busy) emit("close")
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === "Escape" && props.open) requestClose()
}

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) window.addEventListener("keydown", handleKeydown)
    else window.removeEventListener("keydown", handleKeydown)
  },
  { immediate: true },
)

onBeforeUnmount(() => window.removeEventListener("keydown", handleKeydown))
</script>

<template>
  <Teleport to="body">
    <Transition name="base-dialog">
      <div v-if="open" class="dialog-backdrop" @mousedown.self="requestClose">
        <section
          aria-modal="true"
          class="dialog-panel"
          role="dialog"
          :aria-label="title"
          :style="{ '--dialog-width': width }"
        >
          <header class="dialog-header">
            <div>
              <h2>{{ title }}</h2>
              <p v-if="description">{{ description }}</p>
            </div>
            <button
              aria-label="关闭弹窗"
              class="dialog-close"
              type="button"
              :disabled="busy"
              @click="requestClose"
            >
              ×
            </button>
          </header>
          <div class="dialog-body">
            <slot />
          </div>
          <footer v-if="$slots.actions" class="dialog-actions">
            <slot name="actions" />
          </footer>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped src="./BaseDialog.css"></style>
