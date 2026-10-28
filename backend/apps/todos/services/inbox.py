from apps.accounts.public import assigned_role_codes
from apps.approvals.public import pending_monthly_count

from . import items, sources


def list_for_user(user, role_code, page=1):
    if page < 1:
        raise ValueError("页码必须大于0。")
    codes = assigned_role_codes(user.id)
    for code in codes:
        sources.refresh_sources(user, code)
    return {
        **items.list_items(user.id, codes, page),
        "role_code": role_code,
        "pending_approval_count": pending_monthly_count(user.id, role_code),
    }
