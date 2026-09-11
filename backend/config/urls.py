from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.core.urls")),
    path("api/v1/ai/", include("apps.ai_gateway.urls")),
    path("api/v1/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.weekly_report.urls")),
]
