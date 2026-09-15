from django.urls import path

from . import views

app_name = "weekly_report"

urlpatterns = [
    path("dashboard/summary/", views.dashboard_view, name="dashboard"),
    path("weekly-report-templates/<str:role_code>/", views.template_view, name="template"),
    path("monthly-plans/<str:month_key>/", views.monthly_plan_view, name="monthly-plan"),
    path("weekly-reports/", views.report_list_view, name="list"),
    path("weekly-reports/new/", views.report_create_view, name="create"),
    path(
        "weekly-reports/<str:report_id>/attachments/",
        views.attachment_upload_view,
        name="attachment-upload",
    ),
    path("weekly-reports/<str:report_id>/", views.report_detail_view, name="detail"),
]
