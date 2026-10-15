from datetime import date, timedelta
from types import SimpleNamespace

import pytest

from apps.weekly_report.models import WeeklyReport, WeeklyReportItem
from apps.weekly_report.services import reports

pytestmark = pytest.mark.django_db


def make_report(template="delivery_specialist_v1"):
    today = date.today()
    start = today - timedelta(days=today.weekday())
    return WeeklyReport.objects.create(
        employee_id=42, role_code="delivery", template_code=template,
        month_key=start.strftime("%Y-%m"), period_start=start,
        period_end=start + timedelta(days=6), as_of_date=today,
    )


def test_quick_fill_draft_can_save_but_requires_completion_before_submit(monkeypatch):
    monkeypatch.setattr(reports, "_get_template_fields", lambda code: [])
    monkeypatch.setattr(reports, "_role_scope", lambda role: "self")
    report = make_report()
    reports._save_items(report, [{
        "task_code": "task_1", "task_name_snapshot": "回款目标：？万元",
        "customer_name_snapshot": "客户A", "work_content": "主要障碍：？？",
    }], [], 42)
    item = WeeklyReportItem.objects.get(report_id=report.id)
    assert item.output_description == ""
    assert item.planned_completion_date is None
    assert item.owner_id == 42
    user = SimpleNamespace(id=42)
    with pytest.raises(reports.ReportError, match="输出成果"):
        reports.submit_report(user=user, role_code="delivery", report_id=report.id)
    item.output_description = "成果"
    item.save()
    with pytest.raises(reports.ReportError, match="计划完成时间"):
        reports.submit_report(user=user, role_code="delivery", report_id=report.id)
    item.planned_completion_date = report.period_end
    item.save()
    assert reports.submit_report(user=user, role_code="delivery", report_id=report.id)["submitted"]


@pytest.mark.parametrize(
    "template", ["delivery_assistant_v1", "functional_group_v1", "ito_sales_v1"]
)
def test_other_templates_keep_required_fields_on_save(monkeypatch, template):
    monkeypatch.setattr(reports, "_get_template_fields", lambda code: [])
    report = make_report(template)
    payload = {"task_name_snapshot": "任务", "work_content": "工作内容"}
    with pytest.raises(reports.ReportError, match="输出成果"):
        reports._save_items(report, [payload], [], 42)
    payload["output_description"] = "成果"
    with pytest.raises(reports.ReportError, match="计划完成时间"):
        reports._save_items(report, [payload], [], 42)
