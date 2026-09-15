from django.db import migrations, models


class Migration(migrations.Migration):
    """移除周报审核流程字段，状态只由周期计算。"""

    dependencies = [
        ("weekly_report", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="reporttemplate",
            name="review_deadline_rule",
        ),
        migrations.RemoveField(
            model_name="reporttemplate",
            name="submit_deadline_rule",
        ),
        migrations.RemoveField(
            model_name="weeklyreport",
            name="reviewer_id",
        ),
        migrations.RemoveField(
            model_name="weeklyreport",
            name="review_comment",
        ),
        migrations.RemoveField(
            model_name="weeklyreport",
            name="submitted_at",
        ),
        migrations.RemoveField(
            model_name="weeklyreport",
            name="reviewed_at",
        ),
        migrations.DeleteModel(
            name="WeeklyReportReviewRecord",
        ),
        migrations.AlterField(
            model_name="weeklyreport",
            name="status",
            field=models.CharField(default="active", max_length=24),
        ),
    ]
