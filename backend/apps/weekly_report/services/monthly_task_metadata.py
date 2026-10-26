"""月度计划模板信息保存在既有版本快照中，正文仍使用原文本列。"""

import json
import re

from .monthly_task_progress import progress_metadata


def _field_metadata(item, prefix):
    source = item.get(f"{prefix}_source", "custom")
    if source not in {"custom", "template"}:
        raise ValueError("月度计划任务来源无效。")
    if source == "custom":
        return {f"{prefix}_source": "custom", f"{prefix}_template": "", f"{prefix}_values": []}
    template, values = item.get(f"{prefix}_template"), item.get(f"{prefix}_values")
    if not isinstance(template, str) or not template.strip() or not isinstance(values, list):
        raise ValueError("月度计划任务模板信息无效。")
    if len(values) != len(re.findall(r"[?？]", template)) or any(
        not isinstance(value, str) or len(value) > 256 for value in values
    ):
        raise ValueError("月度计划任务模板占位值无效，每项最多256字符。")
    return {f"{prefix}_source": source, f"{prefix}_template": template, f"{prefix}_values": values}


def _group_metadata(item):
    groups = {}
    for field in ("scope_group_key", "task_group_key", "content_group_key"):
        value = item.get(field)
        if value is None:
            continue
        if not isinstance(value, str) or not value.strip() or len(value) > 128:
            raise ValueError("月度计划分组标识必须为非空文字且不能超过128字符。")
        groups[field] = value
    return groups


def task_metadata(item):
    return {
        **progress_metadata(item),
        **_group_metadata(item),
        **_field_metadata(item, "task"),
        **_field_metadata(item, "dimension"),
        **_field_metadata(item, "customer"),
    }


def restore_metadata(tasks, snapshot):
    saved = {str(task.get("id")): task for task in json.loads(snapshot or "{}").get("tasks", [])}
    for task in tasks:
        original = saved.get(str(task["id"]), {})
        if original.get("work_task") == task["work_task"] and (
            original.get("scope_name") or ""
        ) == (task.get("scope_name") or ""):
            task.update(task_metadata(original))
    return tasks


def snapshot_with_metadata(snapshot, submitted):
    for task, raw in zip(snapshot["tasks"], submitted, strict=True):
        task.update(task_metadata(raw))
    return snapshot


def task_content_key(task):
    metadata = task_metadata(task)
    return (
        metadata.get("scope_group_key", ""),
        metadata.get("task_group_key", ""),
        metadata.get("content_group_key", ""),
        task.get("scope_name") or "",
        task.get("work_task"),
        task.get("work_content", ""),
        task.get("output_description", ""),
        task.get("planned_date") or None,
        tuple(sorted(progress_metadata(task).items())),
        metadata["task_source"],
        metadata["task_template"],
        tuple(metadata["task_values"]),
        metadata["dimension_source"],
        metadata["dimension_template"],
        tuple(metadata["dimension_values"]),
        metadata["customer_source"],
        metadata["customer_template"],
        tuple(metadata["customer_values"]),
    )


def validate_group_contents(tasks):
    """分组仅在本次计划载荷内生效，共用字段及其模板信息必须一致。"""
    scopes, groups, contents = {}, {}, {}
    for task in tasks:
        scope_key = task.get("scope_group_key")
        task_key = task.get("task_group_key")
        scope = tuple(
            json.dumps(task.get(name), ensure_ascii=False, sort_keys=True)
            for name in (
                "scope_name", "customer_source", "customer_template", "customer_values",
                "dimension_source", "dimension_template", "dimension_values",
            )
        )
        content = tuple(
            json.dumps(task.get(name), ensure_ascii=False, sort_keys=True)
            for name in ("work_task", "task_source", "task_template", "task_values")
        )
        if scope_key and scopes.setdefault(scope_key, scope) != scope:
            raise ValueError("同一月度计划分组的客户/维度内容不一致。")
        if task_key and groups.setdefault((scope_key, task_key), content) != content:
            raise ValueError("同一月度计划分组的工作任务内容不一致。")

        content_key = task.get("content_group_key")
        if content_key and contents.setdefault(
            (scope_key, task_key, content_key), task.get("work_content", "")
        ) != task.get("work_content", ""):
            raise ValueError("同一月度计划分组的工作内容不一致。")
