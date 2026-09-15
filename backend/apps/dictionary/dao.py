"""Data access for the single-table static dictionary."""

from __future__ import annotations

from typing import Any

from .models import DictionaryItem


def list_active_items(*, dict_type: str) -> list[dict[str, Any]]:
    """Return active options for one dictionary type using Django ORM."""
    return list(
        DictionaryItem.objects.filter(dict_type=dict_type, status="active")
        .order_by("sort_order", "id")
        .values(
            "id",
            "dict_type",
            "dict_code",
            "dict_name",
            "dict_value",
            "description",
            "status",
            "sort_order",
        )
    )


def active_code_exists(*, dict_type: str, dict_code: str) -> bool:
    """Check that a code is currently selectable in a dictionary type."""
    return DictionaryItem.objects.filter(
        dict_type=dict_type,
        dict_code=dict_code,
        status="active",
    ).exists()
