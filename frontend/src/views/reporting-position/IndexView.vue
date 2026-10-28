<script setup lang="ts">
import { ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import BaseDialog from "@/components/overlay/BaseDialog.vue"
import { useAuthStore } from "@/features/auth/store"
const auth = useAuthStore(), route = useRoute(), router = useRouter()
const selected = ref("")
const target = route.query.target === "monthly-plan-new" ? "monthly-plan-new" : "weekly-report-new"
function confirm() {
  if (!auth.reportingRoles.some(role => role.role_code === selected.value)) return
  const query = { ...route.query }
  delete query.target
  void router.replace({ name: target, query: { ...query, role_code: selected.value } })
}
function close() { void router.replace({ name: target === "monthly-plan-new" ? "monthly-plans" : "weekly-reports" }) }
</script>
<template>
  <BaseDialog open title="选择填写职位" @close="close">
    <div class="position-options">
      <label v-for="role in auth.reportingRoles" :key="role.role_code" class="position-option">
        <input v-model="selected" type="radio" name="reporting-position" :value="role.role_code" />{{ role.role_name }}
      </label>
    </div>
    <template #actions><button class="ghost-button" @click="close">取消</button><button class="primary-button" :disabled="!selected" @click="confirm">确定</button></template>
  </BaseDialog>
</template>
<style scoped src="./IndexView.css"></style>
