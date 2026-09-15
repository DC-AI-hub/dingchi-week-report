"""Built-in role templates used before the database seed is applied.

Template items are persisted by ``docs/数据库脚本/02_初始化DML.sql`` and task-list
columns are optionally overridden by the role field dictionaries.  Keeping a
small fallback makes the local UI useful while a developer is preparing MySQL.
"""

from __future__ import annotations

from typing import Any


def _task_fields() -> list[dict[str, Any]]:
    """Return the built-in task-list columns in the Excel-defined order.

    The order is part of the template contract rather than an implementation
    detail of the Vue table.  A dictionary override can replace these values
    without changing the report tables or the task editor form.
    """
    labels = [
        ("customer_name", "客户"),
        ("task_name", "工作任务"),
        ("work_content", "主要工作内容"),
        ("output_description", "输出成果"),
        ("planned_completion_date", "计划完成时间"),
        ("progress_text", "工作进展（截至月日）"),
        ("progress_percent", "完成进度（百分比）"),
        ("delay_reason", "进度缓慢原因说明"),
        ("on_time_status", "是否在计划时间内完成"),
        ("actual_completion_date", "实际完成时间"),
        ("owner_name", "责任人"),
        ("collaborator_names", "协作人"),
        ("document_links", "相关文档链接或佐证材料"),
    ]
    default_visible = {
        "customer_name",
        "task_name",
        "output_description",
        "planned_completion_date",
        "progress_percent",
        "on_time_status",
    }
    return [
        {
            "field_code": code,
            "label": label,
            "sort_order": index,
            "default_visible": code in default_visible,
        }
        for index, (code, label) in enumerate(labels, start=1)
    ]


# Field order/visibility can be overridden by system_dictionary rows named
# ``weekly_report_fields_{role_code}``.  Keep the built-in list for local
# development and for databases that have not loaded the optional DML yet.
ROLE_TASK_FIELDS: dict[str, list[dict[str, Any]]] = {
    "delivery_specialist": _task_fields(),
    "interaction_assistant": _task_fields(),
}


def get_default_task_fields(role_code: str) -> list[dict[str, Any]]:
    """Return a copy of a role's built-in task-list column definition."""
    return [dict(item) for item in ROLE_TASK_FIELDS.get(role_code, [])]


def _task(
    section_code: str, section_name: str, code: str, label: str, guidance: str
) -> dict[str, Any]:
    return {
        "item_type": "task",
        "section_code": section_code,
        "section_name": section_name,
        "task_code": code,
        "label": label,
        "guidance": guidance,
        "scope_type": "customer" if section_code in {"customer", "delivery"} else "overall",
        "value_type": "text",
        "unit": "",
        "required": False,
    }


def _metric(
    section_code: str, section_name: str, code: str, label: str, unit: str = "个"
) -> dict[str, Any]:
    return {
        "item_type": "metric",
        "section_code": section_code,
        "section_name": section_name,
        "task_code": code,
        "label": label,
        "guidance": "填写本周目标与实际值，单位清晰可追溯。",
        "scope_type": "overall",
        "value_type": "number",
        "unit": unit,
        "required": False,
    }


ROLE_TEMPLATES: dict[str, dict[str, Any]] = {
    "recruitment_specialist": {
        "role_name": "招聘专员",
        "template_code": "recruitment_specialist_v1",
        "template_name": "招聘专员周总结计划",
        "description": "围绕候选人漏斗、需求响应和入职结果填写周报。",
        "sections": [
            ("funnel", "招聘漏斗"),
            ("customer", "客户需求"),
            ("other", "其他工作"),
        ],
        "metrics": [
            ("funnel", "招聘漏斗", "resume_recommendations", "简历推荐", "份"),
            ("funnel", "招聘漏斗", "interviews", "到面人数", "人"),
            ("funnel", "招聘漏斗", "onboarded", "有效入职", "人"),
            ("customer", "客户需求", "需求响应率", "需求响应率", "%"),
        ],
        "tasks": [
            (
                "customer",
                "客户需求",
                "candidate_follow_up",
                "重点候选人跟进",
                "记录候选人推进、阻塞和下一步。",
            ),
            (
                "funnel",
                "招聘漏斗",
                "pipeline_cleanup",
                "招聘漏斗清理",
                "更新候选人阶段和预计入职时间。",
            ),
            ("other", "其他工作", "other_work", "其他工作", "填写不属于以上模块的交付物。"),
        ],
    },
    "delivery_specialist": {
        "role_name": "交付专员",
        "template_code": "delivery_specialist_v1",
        "template_name": "交付专员周总结计划",
        "description": "围绕客户交付、招聘转化、成本和回款填写周报。",
        "sections": [
            ("overall", "总体目标"),
            ("customer", "客户需求和招聘转化"),
            ("risk", "风险控制"),
            ("other", "其他工作"),
        ],
        "metrics": [
            ("overall", "总体目标", "net_headcount", "净增人数", "人"),
            ("customer", "客户需求和招聘转化", "new_demands", "新增需求数", "个"),
            ("customer", "客户需求和招聘转化", "incremental_onboarded", "增量入职人数", "人"),
            ("overall", "总体目标", "collection_amount", "回款金额", "万元"),
            ("risk", "风险控制", "high_risk_items", "高风险事项", "个"),
        ],
        "tasks": [
            (
                "customer",
                "客户需求和招聘转化",
                "customer_progress",
                "重点客户交付进展",
                "按客户记录需求、入职与交付成果。",
            ),
            (
                "risk",
                "风险控制",
                "risk_resolution",
                "延期/风险项处理",
                "必须填写原因、下一步和预计完成日期。",
            ),
            ("other", "其他工作", "other_work", "其他工作", "填写不属于以上模块的交付物。"),
        ],
    },
    "interaction_assistant": {
        "role_name": "交互助理",
        "template_code": "interaction_assistant_v1",
        "template_name": "交互助理周总结计划",
        "description": "围绕人员构成、沟通维护、薪酬与客户关系填写周报。",
        "sections": [
            ("people", "客户人员构成"),
            ("risk", "流失与风险"),
            ("customer", "客情关系维护"),
            ("other", "其他工作"),
        ],
        "metrics": [
            ("people", "客户人员构成", "total_headcount", "当月总人数", "人"),
            ("people", "客户人员构成", "incremental_headcount", "增量人数", "人"),
            ("risk", "流失与风险", "attrition_count", "流失人数", "人"),
            ("customer", "客情关系维护", "customer_visits", "客情拜访数", "次"),
            ("other", "其他工作", "salary_confirmation", "薪酬确认书签订", "人"),
        ],
        "tasks": [
            (
                "people",
                "客户人员构成",
                "headcount_review",
                "人员构成复核",
                "同步存量、增量和试用期人员。",
            ),
            (
                "risk",
                "流失与风险",
                "attrition_replacement",
                "流失与替补管控",
                "记录释放、替补和空岗人日。",
            ),
            (
                "customer",
                "客情关系维护",
                "customer_touch",
                "客户沟通维护",
                "记录拜访、沟通结果和待办。",
            ),
            ("other", "其他工作", "other_work", "其他工作", "填写不属于以上模块的交付物。"),
        ],
    },
    "recruitment_manager": {
        "role_name": "招聘经理",
        "template_code": "recruitment_manager_v1",
        "template_name": "招聘经理周总结计划",
        "description": "汇总招聘团队目标、产能、风险与下周行动。",
        "sections": [("team", "团队目标"), ("risk", "风险与支持"), ("other", "其他工作")],
        "metrics": [
            ("team", "团队目标", "team_onboarded", "团队有效入职", "人"),
            ("team", "团队目标", "demand_fill_rate", "需求满足率", "%"),
            ("risk", "风险与支持", "team_risk_items", "团队风险事项", "个"),
        ],
        "tasks": [
            ("team", "团队目标", "team_review", "团队周度复盘", "汇总下属招聘专员的完成情况。"),
            (
                "risk",
                "风险与支持",
                "support_request",
                "资源与风险协调",
                "记录需要跨团队决策的事项。",
            ),
            ("other", "其他工作", "other_work", "其他工作", "填写管理类专项工作。"),
        ],
    },
    "delivery_manager": {
        "role_name": "交付经理",
        "template_code": "delivery_manager_v1",
        "template_name": "交付经理周总结计划",
        "description": "汇总交付团队、客户经营、回款和风险。",
        "sections": [("team", "交付团队"), ("customer", "客户经营"), ("risk", "风险与支持")],
        "metrics": [
            ("team", "交付团队", "team_completion_rate", "团队完成率", "%"),
            ("customer", "客户经营", "collection_amount", "回款金额", "万元"),
            ("risk", "风险与支持", "high_risk_items", "高风险事项", "个"),
        ],
        "tasks": [
            ("team", "交付团队", "team_review", "交付团队复盘", "汇总交付专员与交互助理工作。"),
            (
                "customer",
                "客户经营",
                "customer_review",
                "重点客户经营",
                "记录合同、续签、回款及客情。",
            ),
            (
                "risk",
                "风险与支持",
                "risk_resolution",
                "风险闭环",
                "记录阻塞、责任人与预计解除日期。",
            ),
        ],
    },
    "president": {
        "role_name": "总裁",
        "template_code": "president_v1",
        "template_name": "总裁经营周报",
        "description": "从全局视角填写经营重点、关键决策和组织风险。",
        "sections": [("business", "经营概览"), ("decision", "关键决策"), ("risk", "经营风险")],
        "metrics": [
            ("business", "经营概览", "overall_completion_rate", "整体完成率", "%"),
            ("business", "经营概览", "collection_amount", "本周回款", "万元"),
            ("risk", "经营风险", "high_risk_items", "高风险事项", "个"),
        ],
        "tasks": [
            (
                "business",
                "经营概览",
                "business_review",
                "经营重点复盘",
                "填写跨部门关键进展与结果。",
            ),
            (
                "decision",
                "关键决策",
                "decision_items",
                "关键决策事项",
                "填写需要管理层拍板的事项。",
            ),
            (
                "risk",
                "经营风险",
                "risk_resolution",
                "经营风险处置",
                "填写风险影响、支持和预计解除日期。",
            ),
        ],
    },
    "system_admin": {
        "role_name": "系统管理员",
        "template_code": "system_admin_v1",
        "template_name": "系统运营周报",
        "description": "填写系统运行、数据质量和运营支持事项。",
        "sections": [("operation", "系统运营"), ("data", "数据质量"), ("other", "其他工作")],
        "metrics": [
            ("operation", "系统运营", "service_availability", "服务可用率", "%"),
            ("data", "数据质量", "report_completion_rate", "周报提交率", "%"),
            ("data", "数据质量", "data_issues", "数据问题数", "个"),
        ],
        "tasks": [
            (
                "operation",
                "系统运营",
                "service_operation",
                "系统运行维护",
                "记录发布、告警和问题闭环。",
            ),
            ("data", "数据质量", "data_quality", "数据质量巡检", "记录用户、角色和周报数据检查。"),
            ("other", "其他工作", "other_work", "其他工作", "填写运维支持类专项。"),
        ],
    },
}


def get_default_template(role_code: str) -> dict[str, Any]:
    source = ROLE_TEMPLATES.get(role_code) or ROLE_TEMPLATES["delivery_specialist"]
    sections = [
        {"section_code": code, "section_name": name, "tasks": []}
        for code, name in source["sections"]
    ]
    section_map = {item["section_code"]: item for item in sections}
    items: list[dict[str, Any]] = []
    for index, (section_code, section_name, code, label, guidance, *_rest) in enumerate(
        source["tasks"]
    ):
        item = _task(section_code, section_name, code, label, guidance)
        item["sort_order"] = index
        item["required"] = code != "other_work"
        section_map[section_code]["tasks"].append(item)
        items.append(item)
    metrics: list[dict[str, Any]] = []
    for index, (section_code, section_name, code, label, unit) in enumerate(source["metrics"]):
        item = _metric(section_code, section_name, code, label, unit)
        item["sort_order"] = index
        metrics.append(item)
    return {
        "role_code": role_code,
        "role_name": source["role_name"],
        "template_code": source["template_code"],
        "template_version": "1.0",
        "template_name": source["template_name"],
        "description": source["description"],
        "sections": sections,
        "tasks": items,
        "metrics": metrics,
        "fields": get_default_task_fields(role_code),
    }
