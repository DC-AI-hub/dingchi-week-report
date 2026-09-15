"""Configurable weekly-report tables with logical relationships only."""

from django.db import models

from apps.core.models.base import SnowflakeIdModel


class ReportTemplate(SnowflakeIdModel):
    template_code = models.CharField(max_length=64)
    template_version = models.CharField(max_length=16, default="1.0")
    role_code = models.CharField(max_length=64)
    template_name = models.CharField(max_length=128)
    description = models.CharField(max_length=500, blank=True, default="")
    status = models.CharField(max_length=16, default="active")
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "report_template"
        constraints = [
            models.UniqueConstraint(
                fields=["template_code", "template_version"],
                name="uq_report_template_version",
            ),
        ]
        ordering = ["role_code", "template_code", "template_version"]


class ReportTemplateItem(SnowflakeIdModel):
    template_id = models.BigIntegerField()
    section_code = models.CharField(max_length=64)
    section_name = models.CharField(max_length=128)
    task_code = models.CharField(max_length=64)
    label = models.CharField(max_length=255)
    guidance = models.CharField(max_length=500, blank=True, default="")
    item_type = models.CharField(max_length=16, default="task")
    scope_type = models.CharField(max_length=16, default="overall")
    value_type = models.CharField(max_length=16, default="text")
    unit = models.CharField(max_length=32, blank=True, default="")
    required = models.BooleanField(default=False)
    validation_rule = models.CharField(max_length=255, blank=True, default="")
    sort_order = models.PositiveIntegerField(default=0)
    config_json = models.TextField(blank=True, default="{}")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "report_template_item"
        constraints = [
            models.UniqueConstraint(
                fields=["template_id", "task_code"],
                name="uq_report_template_item_code",
            ),
        ]
        ordering = ["sort_order", "id"]


class WeeklyReport(SnowflakeIdModel):
    role_code = models.CharField(max_length=64)
    template_code = models.CharField(max_length=64)
    template_version = models.CharField(max_length=16, default="1.0")
    employee_id = models.BigIntegerField()
    group_id = models.BigIntegerField(null=True, blank=True)
    period_type = models.CharField(max_length=16, default="week")
    month_key = models.CharField(max_length=7)
    period_start = models.DateField()
    period_end = models.DateField()
    as_of_date = models.DateField()
    # 状态由周报周期动态决定：active/pending_activation/archived。
    status = models.CharField(max_length=24, default="active")
    summary = models.TextField(blank=True, default="")
    risk_level = models.CharField(max_length=16, default="none")
    risk_blocked = models.BooleanField(default=False)
    risk_reason = models.TextField(blank=True, default="")
    next_action = models.TextField(blank=True, default="")
    support_needed = models.TextField(blank=True, default="")
    expected_resolve_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "weekly_report"
        constraints = [
            models.UniqueConstraint(
                fields=["employee_id", "role_code", "period_start"],
                name="uq_weekly_report_employee_role_period",
            ),
        ]
        ordering = ["-period_start", "-updated_at"]


class MonthlyPlan(SnowflakeIdModel):
    role_code = models.CharField(max_length=64)
    employee_id = models.BigIntegerField()
    group_id = models.BigIntegerField(null=True, blank=True)
    month_key = models.CharField(max_length=7)
    summary = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "monthly_plan"
        constraints = [
            models.UniqueConstraint(
                fields=["employee_id", "role_code", "month_key"],
                name="uq_monthly_plan_employee_role_month",
            ),
        ]
        ordering = ["-month_key", "-updated_at"]


class WeeklyReportItem(SnowflakeIdModel):
    report_id = models.BigIntegerField()
    scope_type = models.CharField(max_length=16, default="overall")
    customer_id = models.BigIntegerField(null=True, blank=True)
    customer_name_snapshot = models.CharField(max_length=255, blank=True, default="")
    section_code = models.CharField(max_length=64)
    task_code = models.CharField(max_length=64)
    task_name_snapshot = models.CharField(max_length=255)
    guidance_snapshot = models.CharField(max_length=500, blank=True, default="")
    work_content = models.TextField(blank=True, default="")
    output_description = models.TextField(blank=True, default="")
    planned_completion_date = models.DateField(null=True, blank=True)
    progress_text = models.TextField(blank=True, default="")
    progress_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    quality_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    completion_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    on_time_status = models.CharField(max_length=24, default="in_progress")
    actual_completion_date = models.DateField(null=True, blank=True)
    delay_reason = models.TextField(blank=True, default="")
    next_action = models.TextField(blank=True, default="")
    expected_completion_date = models.DateField(null=True, blank=True)
    owner_id = models.BigIntegerField(null=True, blank=True)
    owner_name_snapshot = models.CharField(max_length=128, blank=True, default="")
    collaborator_names = models.CharField(max_length=500, blank=True, default="")
    document_links = models.TextField(blank=True, default="")
    item_status = models.CharField(max_length=16, default="pending")
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "weekly_report_item"
        ordering = ["sort_order", "id"]


class WeeklyReportMetric(SnowflakeIdModel):
    report_id = models.BigIntegerField()
    item_id = models.BigIntegerField(null=True, blank=True)
    metric_code = models.CharField(max_length=64)
    metric_name_snapshot = models.CharField(max_length=255)
    value_type = models.CharField(max_length=16, default="number")
    target_value_decimal = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )
    actual_value_decimal = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )
    value_text = models.TextField(blank=True, default="")
    unit = models.CharField(max_length=32, blank=True, default="")
    precision = models.PositiveSmallIntegerField(default=0)
    baseline_value_decimal = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )
    note = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "weekly_report_metric"
        ordering = ["metric_code", "id"]


class WeeklyReportEvidence(SnowflakeIdModel):
    report_id = models.BigIntegerField()
    item_id = models.BigIntegerField(null=True, blank=True)
    evidence_type = models.CharField(max_length=16, default="link")
    file_url = models.TextField(blank=True, default="")
    file_name = models.CharField(max_length=255, blank=True, default="")
    description = models.CharField(max_length=500, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "weekly_report_evidence"
