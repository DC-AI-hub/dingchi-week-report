import { computed, reactive, ref } from "vue"
import { isSupportedTemplate } from "@/features/weekly-report/template-support"
import { useUnsavedChanges } from "@/shared/forms/useUnsavedChanges"
import { getManagedPlan, getPlanContext, saveManagedPlan, submitManagedPlan, getPlanChange,savePlanChange,submitPlanChange } from "./api"
import type { ChangeDetail, PlanContext, PlanDetail, PlanInput } from "./types"

export function useMonthlyPlanEditor() {
  const context=ref<PlanContext|null>(null)
  const detail=ref<PlanDetail|null>(null)
  const changeDetail=ref<ChangeDetail|null>(null)
  const flowPlan=computed(()=>changeDetail.value?{...changeDetail.value.plan,...changeDetail.value.change,employee_name:changeDetail.value.plan.employee_name}:detail.value?.plan)
  const today=new Date()
  const month=`${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,"0")}`
  const input=reactive<PlanInput>({month_key:month,summary:"",tasks:[]})
  const busy=ref(false)
  const loading=ref(true)
  const error=ref("")
  const templateUnavailable=ref(false)
  const loadFailed=ref(false)
  const unsavedChanges=useUnsavedChanges(()=>input,()=>!loading.value)
  const canEdit=computed(()=>Boolean(!loading.value && !loadFailed.value && !templateUnavailable.value && isSupportedTemplate(templateCode.value) && context.value?.can_create && (!detail.value || detail.value.can_edit)))
  const templateCode=computed(()=>detail.value?.plan.template_code || context.value?.template_code || "")
  function setChange(data:ChangeDetail) {
    changeDetail.value=data
    detail.value={plan:data.plan,tasks:data.snapshot.tasks,approvals:data.approvals,history:[],can_edit:data.can_edit}
    Object.assign(input,{month_key:data.plan.month_key,summary:data.snapshot.summary,tasks:data.snapshot.tasks.map(task=>({...task})),revision:data.change.revision})
  }
  async function load(id: string, isChange=false) {
    loading.value=true;error.value="";templateUnavailable.value=false;loadFailed.value=false
    try {
      context.value=await getPlanContext()
      if (!isSupportedTemplate(context.value.template_code)) { templateUnavailable.value=true;return }
      if(isChange) {setChange(await getPlanChange(id))}
      else if(id) {
        detail.value=await getManagedPlan(id)
        Object.assign(input,{month_key:detail.value.plan.month_key,summary:detail.value.plan.summary,tasks:detail.value.tasks.map(task=>({...task})),revision:detail.value.plan.revision})
      }
      if (!isSupportedTemplate(templateCode.value)) templateUnavailable.value=true
    } catch(cause) {loadFailed.value=true;error.value=cause instanceof Error?cause.message:"计划加载失败。"}
    finally {loading.value=false}
  }
  async function save(submit: boolean) {
    if(!canEdit.value)return ""
    busy.value=true;error.value=""
    try {
      if(changeDetail.value) {
        setChange(await savePlanChange(changeDetail.value.change.id,input))
        unsavedChanges.markSaved()
        if(submit)setChange(await submitPlanChange(changeDetail.value!.change.id))
        return changeDetail.value!.change.id
      }
      detail.value=await saveManagedPlan(input,detail.value?.plan.id)
      input.revision=detail.value.plan.revision
      input.tasks=detail.value.tasks.map(task=>({...task}))
      unsavedChanges.markSaved()
      if(submit)detail.value=await submitManagedPlan(detail.value.plan.id)
      return detail.value.plan.id
    } catch(cause) {error.value=cause instanceof Error?cause.message:"计划保存失败。";return ""}
    finally {busy.value=false}
  }
  return {context,detail,changeDetail,flowPlan,input,busy,loading,error,templateUnavailable,canEdit,templateCode,load,save,unsavedChanges}
}
