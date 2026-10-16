"""月度计划模板信息保存在既有版本快照中，正文仍使用原文本列。"""

import json
import re


def task_metadata(item):
    source = item.get("task_source", "custom")
    if source not in {"custom", "template"}:
        raise ValueError("月度计划任务来源无效。")
    if source == "custom":
        return {"task_source": "custom", "task_template": "", "task_values": []}
    template, values = item.get("task_template"), item.get("task_values")
    if not isinstance(template, str) or not template.strip() or not isinstance(values, list):
        raise ValueError("月度计划任务模板信息无效。")
    if len(values) != len(re.findall(r"[?？]", template)) or any(
        not isinstance(value, str) or len(value) > 256 for value in values
    ):
        raise ValueError("月度计划任务模板占位值无效，每项最多256字符。")
    return {"task_source": source, "task_template": template, "task_values": values}


def restore_metadata(tasks, snapshot):
    saved = {str(task.get("id")): task for task in json.loads(snapshot or "{}").get("tasks", [])}
    for task in tasks:
        original = saved.get(str(task["id"]), {})
        if original.get("work_task") == task["work_task"]:
            task.update(task_metadata(original))
    return tasks


def snapshot_with_metadata(snapshot, submitted):
    for task, raw in zip(snapshot["tasks"], submitted, strict=True):
        task.update(task_metadata(raw))
    return snapshot


def task_content_key(task):
    metadata = task_metadata(task)
    return (
        task.get("scope_name") or "",
        task.get("work_task"),
        task.get("work_content", ""),
        metadata["task_source"],
        metadata["task_template"],
        tuple(metadata["task_values"]),
    )
