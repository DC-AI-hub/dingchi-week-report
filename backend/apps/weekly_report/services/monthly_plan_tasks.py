"""独立月度计划列表的读取、校验和事务保存。"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from django.db import transaction

from .. import monthly_plan_task_dao as dao
from .monthly_task_metadata import restore_metadata, task_metadata, validate_group_contents


def validate_month_key(month_key: str) -> str:
    if not re.fullmatch(r"[0-9]{4}-(0[1-9]|1[0-2])", month_key) or month_key.startswith("0000"):
        raise ValueError("所属月份必须为 YYYY-MM 格式的有效月份。")
    return month_key


def list_monthly_plan_tasks(
    *, employee_id: int, role_code: str, month_key: str
) -> list[dict[str, Any]]:
    """内部读取已获授权的员工月度明细；权限由周报服务或本人接口入口确定。"""
    rows = dao.list_tasks(
        employee_id=employee_id, role_code=role_code, month_key=validate_month_key(month_key)
    )
    items = [
        {
            "id": str(row.id),
            "scope_name": row.scope_name or "",
            # 旧客户端的输入输出兼容别名，不对应独立数据库字段。
            "customer_name": row.scope_name or "",
            "dimension": row.scope_name or "",
            "work_task": row.work_task,
            "work_content": row.work_content,
            "sort_order": row.sort_order,
            "updated_at": row.updated_at.isoformat(),
        }
        for row in rows
    ]
    return restore_metadata(
        items,
        dao.latest_task_snapshot(employee_id=employee_id, role_code=role_code, month_key=month_key),
    )


def validate_tasks(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) > 200:
        raise ValueError("月度计划必须为任务数组，最多 200 条。")
    work_tasks = []
    for item in value:
        if not isinstance(item, Mapping) or not isinstance(item.get("work_task"), str):
            raise ValueError("月度计划中的工作任务必须为文字。")
        work_task = item["work_task"].strip()
        if not work_task:
            raise ValueError("月度计划工作任务不能为空。")
        scope_name = item.get("scope_name", item.get("dimension") or item.get("customer_name", ""))
        if scope_name is None:
            scope_name = ""
        if not isinstance(scope_name, str) or len(scope_name.strip()) > 255:
            raise ValueError("月度计划客户/维度必须为文字且不能超过 255 个字符。")
        work_content = item.get("work_content", "")
        if not isinstance(work_content, str) or len(work_content) > 10000:
            raise ValueError("月度计划主要工作内容必须为文字且不能超过 10000 个字符。")
        normalized = {
            "scope_name": scope_name.strip(),
            "work_task": work_task,
            "work_content": work_content.strip(),
        }
        normalized.update(task_metadata(item))
        task_id = item.get("id")
        if task_id and str(task_id).isdigit():
            normalized["id"] = str(task_id)
        work_tasks.append(normalized)
    validate_group_contents(work_tasks)
    return work_tasks


def validate_report_monthly_data(summary: Any, tasks: Any, template_code: str) -> None:
    """月度计划保存和提交必须具备有效月度目标和至少一条有效明细。"""
    if not isinstance(summary, str) or not summary.strip():
        raise ValueError("请填写月度目标。")
    normalized = validate_tasks(tasks)
    if not normalized:
        raise ValueError("请至少填写一条月度计划。")
    if template_code == "functional_group_v1":
        return
    label = "模块" if template_code == "human_resources_v1" else (
        "维度" if template_code == "recruitment_v1" else "客户"
    )
    if any(not task["scope_name"] for task in normalized):
        raise ValueError(f"月度计划中的{label}不能为空。")


@transaction.atomic
def save_monthly_plan_tasks(
    *, employee_id: int, role_code: str, month_key: str, value: Any
) -> None:
    """由月度计划管理写用例调用，在同一事务中保存共用月度任务及变更历史。"""
    dao.replace_tasks(
        employee_id=employee_id,
        role_code=role_code,
        month_key=validate_month_key(month_key),
        work_tasks=validate_tasks(value),
    )
