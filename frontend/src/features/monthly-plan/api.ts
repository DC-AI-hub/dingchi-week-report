import { request } from "@/shared/api/http"
import type { ChangeDetail, PlanContext, PlanDetail, PlanFilters, PlanGate, PlanInput, PlanList } from "./types"

const base = "/v1/monthly-plan-management/"
/** 查询本人当前角色的模板及按顺序审批人；GET context/，无参数；Bearer/X-Trace-ID；返回告警和可创建状态，401认证失败。 */
export function getPlanContext(): Promise<PlanContext> { return request<PlanContext>({ method: "GET", url: base + "context/" }).then(context => ({...context, warning: context.warning.replaceAll("角色", "职位")})) }
/** 月度计划筛选分页：GET；view=mine/members/approvals，月份、状态、人员/分组ID、pending_only及分页；审批视图按每次提交分页，返回本人分配的审批记录及has_approval_tasks；400/401/403。 */
export function listMonthlyPlans(params: PlanFilters): Promise<PlanList> { return request({ method: "GET", url: base, params }) }
/** 读取指定计划、任务、审批快照及变更历史；GET {id}/，ID为字符串；可见范围及审批人鉴权；401/403/404，统一trace。 */
export function getManagedPlan(id: string): Promise<PlanDetail> { return request({ method: "GET", url: base + id + "/" }) }
/** 保存本人计划：POST新增、PATCH修改；月份、目标、任务必填；工作任务为长文本；可带task_source/task_template/task_values（来源、模板原文、每项最多256字的占位值，旧数据默认custom）；任务可带work_content（最多10000字符，默认空文本）；修改携带revision防覆盖；未配置上级/审批中禁止；400/401/403，返回完整详情。 */
export function saveManagedPlan(input: PlanInput, id?: string): Promise<PlanDetail> { return request({ method: id ? "PATCH" : "POST", url: base + (id ? id + "/" : ""), data: input }) }
/** 提交审批：POST {id}/submit/，无请求体；按有序上级创建新审批单及快照；不可重复，驳回需先修改；400/403，返回详情。 */
export function submitManagedPlan(id: string): Promise<PlanDetail> { return request({ method: "POST", url: base + id + "/submit/" }) }
/** 软删除本人计划并留历史：DELETE {id}/；审批中禁止；403/404/400；返回字符串id和deleted，trace统一。 */
export function deleteManagedPlan(id: string): Promise<{id: string; deleted: true}> { return request({ method: "DELETE", url: base + id + "/" }) }
/** 按序审批：POST {id}/decide/；action=approve/reject，驳回reason必填最多2000字符；只有当前审批人可操作；400/403/404，返回详情。 */
export function decideManagedPlan(id: string, action: "approve" | "reject", reason: string, approvalId?: string): Promise<PlanDetail> { return request({ method: "POST", url: base + id + "/decide/", data: {action, reason, approval_id: approvalId} }) }
/** 检查本人当前角色指定月份已审批计划：GET gate/{YYYY-MM}/；返回approved/message和只读内容；用于周报加载及周期切换，400/401，trace统一。 */
export function getMonthlyPlanGate(month: string): Promise<PlanGate> { return request({ method: "GET", url: base + "gate/" + encodeURIComponent(month) + "/" }) }

/** 创建已通过计划的变更草稿：POST {id}/changes/，无请求体；锁定基准版本，有未完成申请返回400；Bearer、trace，返回独立申请及原始/拟变更快照，不修改生效数据。 */
export function createPlanChange(id:string):Promise<ChangeDetail> { return request({method:"POST",url:base+id+"/changes/"}) }
/** GET changes/{id}/：查看获授权的变更快照、不可变原始快照和审批记录；字符串ID；401/403/404，统一trace。 */
export function getPlanChange(id:string):Promise<ChangeDetail> { return request({method:"GET",url:base+"changes/"+id+"/"}) }
/** PATCH changes/{id}/：保存目标/tasks/revision，月份不可变；审批中不可编辑；原始快照不可写；400/403/404，返回ChangeDetail。 */
export function savePlanChange(id:string,input:PlanInput):Promise<ChangeDetail> { return request({method:"PATCH",url:base+"changes/"+id+"/",data:input}) }
/** POST changes/{id}/submit/：逐级审批变更，未改内容或基准版本过期返回400；主流程保持生效。 */
export function submitPlanChange(id:string):Promise<ChangeDetail> { return request({method:"POST",url:base+"changes/"+id+"/submit/"}) }
/** POST changes/{id}/decide/：action、reason、approval_id，驳回原因必填；最终通过原子发布到主流程，401/403/400；返回ChangeDetail。 */
export function decidePlanChange(id:string,action:"approve"|"reject",reason:string,approvalId:string):Promise<ChangeDetail> { return request({method:"POST",url:base+"changes/"+id+"/decide/",data:{action,reason,approval_id:approvalId}}) }
/** DELETE changes/{id}/：删除本人草稿或驳回的变更申请并保留审批历史；主流程不变，400/403/404。 */
export function deletePlanChange(id:string):Promise<{id:string;deleted:true}> { return request({method:"DELETE",url:base+"changes/"+id+"/"}) }

/** GET approvals/{id}/：本人分配审批单的冻结快照及变更基线，不受列表筛选分页影响；Bearer/trace，400/401/403；返回ApprovalRecord，v1新增。 */
export function getAssignedApproval(id:string):Promise<import("./types").ApprovalRecord>{return request({method:"GET",url:base+"approvals/"+id+"/"})}
