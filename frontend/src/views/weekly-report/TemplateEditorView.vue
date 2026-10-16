<script setup lang="ts">
import { computed, onMounted, ref } from "vue"
import { useRoute, useRouter } from "vue-router"

import { useAuthStore } from "@/features/auth/store"
import AlertDialog from "@/components/feedback/AlertDialog.vue"
import { ApiError } from "@/shared/api/errors"
import { TEMPLATE_UNAVAILABLE_MESSAGE } from "@/features/weekly-report/template-support"
import { getReportDetail, getReportTemplate } from "@/features/weekly-report/api"
import { resolveTemplateEditor } from "@/features/weekly-report/template-registry"

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const templateCode = ref("")
const isLoading = ref(true)
const errorMessage = ref("")
const editor = computed(() => (!errorMessage.value && templateCode.value ? resolveTemplateEditor(templateCode.value) : null))
const reportId = computed(() => String(route.params.reportId || ""))

async function loadTemplateCode() {
  isLoading.value = true
  errorMessage.value = ""
  try {
    if (reportId.value) {
      // 编辑历史/当前周报时严格使用周报保存的模板编码，避免角色后来换绑模板造成页面错乱。
      const detail = await getReportDetail(reportId.value)
      templateCode.value = detail.report.template_code
    } else {
      const roleTemplateCode = authStore.activeRole?.report_template_code || ""
      const routeTemplateCode = String(route.query.template_code || "").trim()
      if (routeTemplateCode && routeTemplateCode !== roleTemplateCode) {
        throw new Error(TEMPLATE_UNAVAILABLE_MESSAGE)
      }
      templateCode.value = routeTemplateCode || roleTemplateCode
    }
    if (!templateCode.value) throw new Error(TEMPLATE_UNAVAILABLE_MESSAGE)
    if (!resolveTemplateEditor(templateCode.value)) {
      throw new Error(TEMPLATE_UNAVAILABLE_MESSAGE)
    }
    await getReportTemplate(templateCode.value)
  } catch (error) {
    errorMessage.value = error instanceof ApiError && Boolean(templateCode.value) && ["REPORT_NOT_FOUND", "REPORT_INVALID"].includes(error.code)
      ? TEMPLATE_UNAVAILABLE_MESSAGE : error instanceof Error ? error.message : "周报模板加载失败。"
    templateCode.value = ""
  } finally {
    isLoading.value = false
  }
}

function closeTemplateError() {
  errorMessage.value = ""
  void router.replace({ name: "weekly-reports", query: route.query })
}

onMounted(() => void loadTemplateCode())
</script>

<template>
  <div v-if="isLoading" class="dashboard-card loading-card">正在加载周报模板</div>
  <component :is="editor" v-else-if="editor" />
  <AlertDialog
    :open="Boolean(errorMessage)"
    title="周报模板不可用"
    :message="errorMessage"
    @close="closeTemplateError"
  />
</template>
