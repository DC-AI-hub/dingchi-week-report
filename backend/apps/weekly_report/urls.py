from django.urls import path

from . import views

app_name = "weekly_report"

urlpatterns = [
    path("dashboard/summary/", views.dashboard_view, name="dashboard"),
    path("weekly-report-templates/<str:role_code>/", views.template_view, name="template"),
    path("weekly-reports/", views.report_list_view, name="list"),
    path("weekly-reports/new/", views.report_create_view, name="create"),
    path("weekly-reports/<str:report_id>/", views.report_detail_view, name="detail"),
    path("weekly-reports/<str:report_id>/submit/", views.report_submit_view, name="submit"),
    path("weekly-reports/<str:report_id>/review/", views.report_review_view, name="review"),
    path("weekly-reports/<str:report_id>/history/", views.report_history_view, name="history"),
]
