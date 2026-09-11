from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("auth/login/", views.login_view, name="login"),
    path("auth/me/", views.me_view, name="me"),
    path("auth/switch-role/", views.switch_role_view, name="switch-role"),
    path("auth/logout/", views.logout_view, name="logout"),
    path("roles/", views.roles_view, name="roles"),
    path("roles/new/", views.role_create_view, name="role-create"),
    path("roles/<str:role_id>/", views.role_detail_view, name="role-detail"),
    path("groups/", views.groups_view, name="groups"),
    path("groups/new/", views.group_create_view, name="group-create"),
    path("groups/<str:group_id>/", views.group_update_view, name="group-update"),
    path("users/", views.users_view, name="users"),
    path("users/new/", views.user_create_view, name="user-create"),
    path("users/<str:user_id>/", views.user_update_view, name="user-update"),
]
