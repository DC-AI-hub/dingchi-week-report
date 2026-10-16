<script setup lang="ts">
import { computed, ref, watch } from "vue"
import { useRouter } from "vue-router"
import AlertDialog from "@/components/feedback/AlertDialog.vue"
import { isSupportedTemplate, TEMPLATE_UNAVAILABLE_MESSAGE } from "@/features/weekly-report/template-support"
import type { PlanContext } from "@/features/monthly-plan/types"
const props = defineProps<{ context: PlanContext | null; personal: boolean }>()
const router = useRouter()
const templateWarningOpen = ref(false)
const invalidTemplate = computed(() => Boolean(props.context && !isSupportedTemplate(props.context.template_code)))
watch(() => props.context?.template_code, () => { templateWarningOpen.value = false })
function create() {
  if (invalidTemplate.value) { templateWarningOpen.value = true;return }
  if (props.context?.can_create) void router.push({name:"monthly-plan-new",query:{tab:"mine"}})
}
</script>
<template>
  <header class="monthly-list-header">
    <div class="monthly-list-tabs"><slot /></div>
    <button v-if="personal && context && (context.can_create || invalidTemplate)" class="primary-button" type="button" @click="create">新增月度计划</button>
  </header>
  <p v-if="personal && !invalidTemplate && context?.warning" class="monthly-list-warning" role="alert">{{ context.warning }}</p>
  <AlertDialog :open="templateWarningOpen" title="月度计划模板不可用" :message="TEMPLATE_UNAVAILABLE_MESSAGE" @close="templateWarningOpen = false" />
</template>
<style scoped src="./MonthlyPlanListHeader.css"></style>
