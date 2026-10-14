from apps.approvals.public import pending_todo_entries
from apps.weekly_report.public import weekly_reminder_entries

from .items import reconcile


def refresh_sources(user, role_code):
    reconcile(user.id, role_code, "approval", pending_todo_entries(user.id, role_code))
    reconcile(user.id, role_code, "weekly_report", weekly_reminder_entries(user, role_code))
