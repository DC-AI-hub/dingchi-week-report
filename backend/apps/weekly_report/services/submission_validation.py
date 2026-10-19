"""提交时统一校验业务必填项，草稿不执行这些非空检查。"""

from apps.weekly_report.models import WeeklyReportDailyTask, WeeklyReportMetric


def submission_errors(report, items, fields, template):
    errors = []
    codes = {field.get("field_code") for field in fields}
    required = [
        ("task_name_snapshot", "工作任务"),
        ("work_content", "主要工作内容"),
        ("output_description", "输出成果"),
        ("planned_completion_date", "计划完成时间"),
    ]
    if "customer_name" in codes:
        required.append(("customer_name_snapshot", "客户"))
    if "dimension" in codes:
        required.append(("section_code", "维度"))
    if not items:
        errors.append("本周工作至少需要一条任务。")
    for index, item in enumerate(items, 1):
        for key, label in required:
            if not str(item.get(key) or "").strip():
                errors.append(f"第{index}行{label}不能为空。")
        if item.get("task_source") == "template" and any(
            not value.strip() for value in item.get("task_values", [])
        ):
            errors.append(f"第{index}行工作任务的模板占位值尚未填写完整。")
        if item.get("dimension_source") == "template" and any(
            not value.strip() for value in item.get("dimension_values", [])
        ):
            errors.append(f"第{index}行维度的模板占位值尚未填写完整。")
        if item.get("customer_source") == "template" and any(
            not value.strip() for value in item.get("customer_values", [])
        ):
            errors.append(f"第{index}行客户的模板占位值尚未填写完整。")
        if (
            item.get("on_time_status") in {"late", "overdue"}
            and not str(item.get("delay_reason") or "").strip()
        ):
            errors.append(f"第{index}行进度缓慢原因说明不能为空。")
    for row in WeeklyReportDailyTask.objects.filter(report_id=report.id):
        if not row.work_content.strip():
            errors.append(f"{row.work_date}日报主要工作内容不能为空。")
    metrics = {
        row.metric_code: row for row in WeeklyReportMetric.objects.filter(report_id=report.id)
    }
    for config in template.get("metrics", []):
        row = metrics.get(config["task_code"])
        if config.get("required") and (
            row is None or (row.actual_value_decimal is None and not row.value_text.strip())
        ):
            errors.append(f"指标{config['label']}不能为空。")
    return errors
