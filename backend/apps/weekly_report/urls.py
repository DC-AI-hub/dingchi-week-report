from django.urls import path

from . import views

app_name = "weekly_report"

urlpatterns = [
    path("dashboard/summary/", views.dashboard_view, name="dashboard"),
    path("dashboard/next-week/", views.dashboard_next_week_view, name="dashboard-next-week"),
    path("weekly-report-templates/<str:template_code>/", views.template_view, name="template"),
    path("monthly-plans/<str:month_key>/", views.monthly_plan_view, name="monthly-plan"),
    path("weekly-reports/", views.report_list_view, name="list"),
    path(
        "weekly-reports/<str:report_id>/daily-tasks/",
        views.daily_task_list_view,
        name="daily-task-list",
    ),
    path(
        "weekly-reports/<str:report_id>/daily-tasks/<str:daily_task_id>/",
        views.daily_task_detail_view,
        name="daily-task-detail",
    ),
    path(
        "weekly-reports/<str:report_id>/attachments/",
        views.attachment_upload_view,
        name="attachment-upload",
    ),
    path(
        "weekly-reports/<str:report_id>/submit/",
        views.report_submit_view,
        name="submit",
    ),
    path("weekly-reports/<str:report_id>/", views.report_detail_view, name="detail"),
]
