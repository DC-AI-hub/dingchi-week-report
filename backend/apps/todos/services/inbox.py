from apps.approvals.public import pending_monthly_count

from . import items, sources


def list_for_user(user, role_code, page=1):
    if page < 1:
        raise ValueError("页码必须大于0。")
    sources.refresh_sources(user, role_code)
    return {
        **items.list_items(user.id, role_code, page),
        "pending_approval_count": pending_monthly_count(user.id, role_code),
    }
