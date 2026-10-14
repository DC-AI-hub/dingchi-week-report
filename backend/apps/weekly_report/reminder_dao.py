from .models import WeeklyReport


def has_report(employee_id, role_code, start):
    return (
        WeeklyReport.objects.filter(
            employee_id=employee_id, role_code=role_code, period_start=start
        )
        .exclude(status="deleted")
        .exists()
    )
