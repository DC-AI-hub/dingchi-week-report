from typing import Any

from django.http import JsonResponse


def api_success(data: Any, *, status: int = 200) -> JsonResponse:
    return JsonResponse({"success": True, "data": data}, status=status)


def api_error(
    code: str,
    message: str,
    *,
    status: int,
    details: Any | None = None,
) -> JsonResponse:
    error: dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        error["details"] = details
    return JsonResponse({"success": False, "error": error}, status=status)
