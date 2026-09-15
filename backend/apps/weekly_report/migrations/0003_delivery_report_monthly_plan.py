from django.db import migrations, models

import apps.core.services.id_generator


class Migration(migrations.Migration):
    """增加交付专员月度计划及周任务完整字段；仅定义迁移，不随启动自动执行。"""

    dependencies = [("weekly_report", "0002_remove_review_workflow")]

    operations = [
        migrations.CreateModel(
            name="MonthlyPlan",
            fields=[
                ("id", models.BigIntegerField(default=apps.core.services.id_generator.generate_primary_id, editable=False, primary_key=True, serialize=False)),
                ("role_code", models.CharField(max_length=64)),
                ("employee_id", models.BigIntegerField()),
                ("group_id", models.BigIntegerField(blank=True, null=True)),
                ("month_key", models.CharField(max_length=7)),
                ("summary", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "monthly_plan", "ordering": ["-month_key", "-updated_at"]},
        ),
        migrations.AddConstraint(
            model_name="monthlyplan",
            constraint=models.UniqueConstraint(fields=("employee_id", "role_code", "month_key"), name="uq_monthly_plan_employee_role_month"),
        ),
        migrations.AddField(model_name="weeklyreportitem", name="work_content", field=models.TextField(blank=True, default="")),
        migrations.AddField(model_name="weeklyreportitem", name="owner_name_snapshot", field=models.CharField(blank=True, default="", max_length=128)),
        migrations.AddField(model_name="weeklyreportitem", name="collaborator_names", field=models.CharField(blank=True, default="", max_length=500)),
        migrations.AddField(model_name="weeklyreportitem", name="document_links", field=models.TextField(blank=True, default="")),
    ]
