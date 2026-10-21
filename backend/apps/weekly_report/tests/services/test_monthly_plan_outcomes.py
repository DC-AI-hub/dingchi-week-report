import pytest

from apps.accounts.services.monthly_approvers import set_monthly_approvers
from apps.weekly_report.services import reports
from apps.weekly_report.services.monthly_plan_tasks import validate_tasks
from apps.weekly_report.services.monthly_plans import change_write, read, write
from apps.weekly_report.services.monthly_plans.copy import copy_next_month

from .test_monthly_plan_workflow import people as people

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("template", [
    "delivery_specialist_v1", "delivery_assistant_v1", "recruitment_v1", "ito_sales_v1",
    "innovation_sales_v1", "functional_group_v1", "human_resources_v1",
])
def test_outcomes_save_approve_change_and_copy_all_templates(people, monkeypatch, template):
    owner = people[0]
    set_monthly_approvers(owner.id, [])
    monkeypatch.setattr(reports, "resolve_role_template", lambda role: {"template_code": template})
    parent = {"scope_name": "范围", "work_task": "工作任务", "work_content": "同一工作内容",
              "scope_group_key": "scope", "task_group_key": "task", "content_group_key": "content"}
    data = write.save(owner, "delivery", {
        "month_key": "2026-10", "summary": "月度目标", "tasks": [
            {**parent, "output_description": "成果一\n明细", "planned_date": "2026-10-25"},
            {**parent, "output_description": "成果二", "planned_date": "2026-10-28"},
        ],
    })
    plan_id = int(data["plan"]["id"])
    assert data["tasks"][0]["planned_date"] == "2026-10-25"
    assert data["tasks"][1]["output_description"] == "成果二"
    data = write.submit(owner, "delivery", plan_id)
    assert data["approvals"][0]["snapshot"]["tasks"] == data["tasks"]
    child = change_write.create(owner, "delivery", plan_id)
    change_id = int(child["change"]["id"])
    changed = [{**task} for task in child["snapshot"]["tasks"]]
    changed[1].update(output_description="新成果", planned_date="2026-10-30")
    change_write.save(owner, "delivery", change_id, {
        "revision": 0, "summary": "月度目标", "tasks": changed,
    })
    # 仅修改成果和日期也必须被识别为有效变更。
    change_write.submit(owner, "delivery", change_id)
    final = read.detail(owner, "delivery", plan_id)
    assert final["tasks"][1]["planned_date"] == "2026-10-30"
    assert final["tasks"][1]["output_description"] == "新成果"
    copied = copy_next_month(owner, "delivery", plan_id)
    assert copied["plan"]["status"] == "draft"
    for actual, original in zip(copied["tasks"], final["tasks"], strict=True):
        assert actual["id"] != original["id"]
        for field in ["output_description", "planned_date", "content_group_key", "work_content"]:
            assert actual[field] == original[field]


@pytest.mark.parametrize("fields", [
    {"planned_date": "2026-02-30"}, {"planned_date": "20261020"}, {"planned_date": 10},
    {"output_description": None}, {"output_description": "a" * 10001},
])
def test_invalid_outcome_rejected(fields):
    with pytest.raises(ValueError):
        validate_tasks([{"work_task": "任务", **fields}])


def test_old_rows_default_blank_and_shared_content_validated():
    old = validate_tasks([{"work_task": "任务"}])[0]
    assert old["output_description"] == "" and old["planned_date"] is None
    rows = [{"work_task": "任务", "scope_group_key": "s", "task_group_key": "t",
             "content_group_key": "c", "work_content": work} for work in ["内容一", "内容二"]]
    with pytest.raises(ValueError, match="工作内容不一致"):
        validate_tasks(rows)
