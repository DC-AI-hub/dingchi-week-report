"""Stable account capabilities shared by other backend modules."""

from __future__ import annotations

from typing import Any

from .manager_dao import role_name, role_names, role_scope
from .models import UserAccount
from .services.auth import get_user_roles, require_request_user
from .services.managers import profiles, visible_ids
from .services.monthly_approvers import get_monthly_approvers


def approval_managers(user_id):
    return get_monthly_approvers(user_id)


def visible_user_ids(user, role_code):
    return visible_ids(user, role_code)


def user_profiles(ids):
    return profiles(ids)


def account_role_scope(role_code):
    return role_scope(role_code)


def require_user(request: Any) -> tuple[UserAccount, str]:
    """Require a valid bearer token and return the user plus active role code."""
    return require_request_user(request)


def report_roles(user_id):
    return [
        {"role_code": role.role_code, "role_name": role.role_name}
        for role in get_user_roles(user_id)
        if role.scope != "all" and role.report_template_code
    ]


def approval_role_code(user_id, template_code=""):
    roles = get_user_roles(user_id)
    if not roles:
        raise ValueError("审批人未配置有效角色，请联系管理员配置。")
    indexed = list(enumerate(roles))
    indexed.sort(
        key=lambda item: (
            item[1].scope not in {"team", "all"},
            item[1].report_template_code != template_code,
            item[1].scope != "team",
            item[0],
        )
    )
    return indexed[0][1].role_code


def account_role_name(role_code):
    """返回职位名称；已移除的职位回退为原编码。"""
    return role_name(role_code)


def account_role_names(codes):
    """批量返回职位编码与名称，供业务列表展示使用。"""
    return role_names(codes)


def assigned_role_codes(user_id):
    """当前有效职位集合；读取、审批聚合不得包含已撤销职位。"""
    return [role.role_code for role in get_user_roles(user_id)]
