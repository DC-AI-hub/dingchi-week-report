"""Stable account capabilities shared by other backend modules."""

from __future__ import annotations

from typing import Any

from .models import UserAccount
from .services.auth import require_request_user


def require_user(request: Any) -> tuple[UserAccount, str]:
    """Require a valid bearer token and return the user plus active role code."""
    return require_request_user(request)
