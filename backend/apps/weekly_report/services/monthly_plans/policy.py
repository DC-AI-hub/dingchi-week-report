from apps.accounts.public import approval_managers, shared_report_owner_ids, visible_user_ids

from ... import monthly_plan_management_dao as dao
from ..submission_scope import check_part
from .versions import assigned_root_ids


class PlanNotFound(ValueError):
    pass


def readable_plan(user, role_code, plan_id, *, lock=False):
    plan = dao.find_plan(plan_id, lock=lock)
    if plan is None or plan.status == "deleted":
        raise PlanNotFound("月度计划不存在或已删除。")
    visible = int(plan.employee_id) in visible_user_ids(user, role_code) or int(
        plan.employee_id
    ) in shared_report_owner_ids(user.id)
    if not visible and int(plan.id) not in assigned_root_ids(user.id, role_code):
        raise PermissionError("无权查看该月度计划。")
    return plan


def editable_plan(user, role_code, plan_id):
    plan = readable_plan(user, role_code, plan_id, lock=True)
    check_part(plan)
    if int(plan.employee_id) != int(user.id) or plan.role_code != role_code:
        raise PermissionError("只能修改当前角色下自己的月度计划。")
    if plan.status == "pending":
        raise ValueError("审批期间不允许修改或删除月度计划。")
    configured_approvers(user.id)
    return plan


def configured_approvers(user_id):
    return approval_managers(user_id)


def ensure_approved(user, role_code, month_key, *, missing_message=None):
    plan = dao.find_plan(employee_id=user.id, role_code=role_code, month_key=month_key, lock=True)
    if missing_message and (plan is None or plan.status == "deleted"):
        raise ValueError(missing_message)
    if plan is None or plan.status != "approved":
        raise ValueError(f"{month_key} 尚无审批通过的月度计划，请先填写并完成审批后再填写周报。")
    return plan
