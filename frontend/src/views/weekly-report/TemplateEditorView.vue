<script setup lang="ts">
import { computed, onMounted, ref } from "vue"
import { useRoute, useRouter } from "vue-router"

import { useAuthStore } from "@/features/auth/store"
import AlertDialog from "@/components/feedback/AlertDialog.vue"
import { getReportDetail } from "@/features/weekly-report/api"
import { resolveTemplateEditor } from "@/features/weekly-report/template-registry"

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const templateCode = ref("")
const isLoading = ref(true)
const errorMessage = ref("")
const editor = computed(() => (templateCode.value ? resolveTemplateEditor(templateCode.value) : null))
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
        throw new Error("当前角色绑定的周报模板已发生变化，请返回后重新进入。")
      }
      templateCode.value = routeTemplateCode || roleTemplateCode
    }
    if (!templateCode.value) throw new Error("当前角色未配置周报模板。")
    if (!resolveTemplateEditor(templateCode.value)) {
      throw new Error("当前角色绑定的周报模板暂不支持填写。")
    }
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "周报模板加载失败。"
  } finally {
    isLoading.value = false
  }
}

function closeTemplateError() {
  errorMessage.value = ""
  void router.replace({ name: "weekly-reports" })
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
