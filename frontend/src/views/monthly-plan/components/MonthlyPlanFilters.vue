<script setup lang="ts">
import { computed, onMounted, ref } from "vue"
import { listUserOptions } from "@/features/directory/api"
import type { DirectoryUserOption } from "@/features/directory/types"
import PersonSelect from "@/features/directory/components/PersonSelect.vue"
import { planStatusLabels, type PlanFilters, type PlanListView } from "@/features/monthly-plan/types"
const filters = defineModel<PlanFilters>({ required: true })
defineProps<{busy: boolean; view: PlanListView}>()
const emit = defineEmits<{search: []}>()
const users = ref<DirectoryUserOption[]>([])
const groups = computed(() => [...new Map(users.value.filter(user=>user.group_id).map(user=>[String(user.group_id),{id:String(user.group_id),group_name:user.group_name || "未分组"}])).values()])
const optionError = ref("")
const employee = computed({ get:()=>filters.value.employee_id || "", set:(value:string|string[])=>{ filters.value.employee_id=String(value || "") } })
onMounted(async()=>{
  try {
    users.value=(await listUserOptions()).items
  } catch(cause) { optionError.value=cause instanceof Error?cause.message:"人员和分组加载失败，请刷新重试。" }
})
</script>
<template>
  <form class="monthly-filters" @submit.prevent="emit('search')">
    <p v-if="optionError" role="alert">{{optionError}}</p>
    <label>所属月度<input v-model="filters.month_key" type="month" /></label>
    <label>状态<select v-model="filters.status"><option value="">全部</option><option v-for="status in ['draft','pending','approved','rejected']" :key="status" :value="status">{{planStatusLabels[status]}}</option></select></label>
    <label v-if="view !== 'mine'">分组<select v-model="filters.group_id"><option value="">全部分组</option><option v-for="group in groups" :key="group.id" :value="group.id">{{group.group_name}}</option></select></label>
    <label v-if="view !== 'mine'">人员<PersonSelect v-model="employee" :users="users" /></label>
    <button class="primary-button" type="submit" :disabled="busy">查询</button>
  </form>
</template>
<style scoped src="./MonthlyPlanFilters.css"></style>
