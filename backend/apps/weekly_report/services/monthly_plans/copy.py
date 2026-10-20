"""将当前生效的本人月度计划独立复制到下一月。"""

from django.db import transaction

from ... import monthly_plan_management_dao as dao
from ..monthly_plan_tasks import save_monthly_plan_tasks
from ..monthly_task_metadata import snapshot_with_metadata
from .policy import editable_plan
from .read import detail
from .write import record_change, snapshot


@transaction.atomic
def copy_next_month(user, role_code, plan_id):
    source = editable_plan(user, role_code, plan_id)
    if source.status != "approved":
        raise ValueError("仅审批通过的月度计划可以复制。")
    year, month = map(int, source.month_key.split("-"))
    target_month = f"{year + (month == 12):04d}-{month % 12 + 1:02d}"
    if year == 9999 and month == 12:
        raise ValueError("下个月份超出支持范围。")
    target = dao.find_plan(
        employee_id=user.id, role_code=role_code, month_key=target_month, lock=True
    )
    if target and target.status != "deleted":
        raise ValueError("下个月度计划已存在。")
    # 未通过的变更仅在子流程快照内，主计划始终保存最新已生效版本。
    data = snapshot(source)
    tasks = [{key: value for key, value in task.items() if key != "id"}
             for task in data["tasks"]]
    target = target or dao.create_plan(
        employee_id=user.id, role_code=role_code, month_key=target_month, group_id=user.group_id
    )
    target.summary, target.template_code = source.summary, source.template_code
    target.status, target.rejection_reason = "draft", ""
    target.revision += 1
    dao.save_plan(target)
    save_monthly_plan_tasks(
        employee_id=user.id, role_code=role_code, month_key=target_month, value=tasks
    )
    record_change(target, user.id, "create", {}, snapshot_with_metadata(snapshot(target), tasks))
    return detail(user, role_code, target.id)
