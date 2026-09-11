"""Authentication and role-switching services."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from django.conf import settings
from django.contrib.auth.hashers import constant_time_compare
from django.db import transaction
from django.utils import timezone

from apps.core.authentication.token import create_access_token
from apps.core.security.passwords import CryptoPayloadError, decrypt_client_password

from ..models import Role, UserAccount, UserRole


class AuthenticationError(ValueError):
    """A safe, user-facing authentication failure."""

    code = "AUTHENTICATION_FAILED"


class AuthorizationError(ValueError):
    """The identity is valid but is not allowed to perform an operation."""

    code = "FORBIDDEN"


def login(
    *, username: str, password_ciphertext: str, requested_role_code: str | None = None
) -> dict[str, Any]:
    """Decrypt the transport password, verify it and issue a signed token."""
    if not username or not password_ciphertext:
        raise AuthenticationError("用户名和密码不能为空。")
    try:
        password = decrypt_client_password(password_ciphertext)
    except CryptoPayloadError as exc:
        raise AuthenticationError("密码加密格式无效，请刷新页面后重试。") from exc

    user = UserAccount.objects.filter(username=username, status="active").first()
    if user is None:
        raise AuthenticationError("用户名或密码错误。")
    # EncryptedPasswordField decrypts only in request-local memory.  The value
    # remains RSA ciphertext in the database.
    stored_password = str(user.password_ciphertext or "")
    if not constant_time_compare(stored_password, password):
        raise AuthenticationError("用户名或密码错误。")

    roles = get_user_roles(user.id)
    if not roles:
        raise AuthenticationError("当前用户尚未分配可用角色。")
    role = _choose_role(roles, requested_role_code)
    user.last_login_at = timezone.now()
    user.save(update_fields=["last_login_at", "updated_at"])
    return build_session(user, roles, role.role_code)


def build_session(user: UserAccount, roles: list[Role], active_role_code: str) -> dict[str, Any]:
    """Return the public session contract used by the browser store."""
    active_role = next(role for role in roles if role.role_code == active_role_code)
    return {
        "access_token": create_access_token(user_id=int(user.id), role_code=active_role.role_code),
        "token_type": "Bearer",
        "expires_in": settings.AUTH_TOKEN_MAX_AGE_SECONDS,
        "user": serialize_user(user),
        "roles": [serialize_role(role) for role in roles],
        "active_role": serialize_role(active_role),
    }


def get_user_roles(user_id: int) -> list[Role]:
    """Resolve assigned roles without a database foreign key."""
    assignments = list(
        UserRole.objects.filter(user_id=user_id, status="active")
        .order_by("-is_default", "id")
        .values_list("role_id", flat=True)
    )
    role_ids = list(assignments)
    if not role_ids:
        return []
    role_map = {
        role.id: role for role in Role.objects.filter(id__in=role_ids, status="active")
    }
    return [role_map[role_id] for role_id in role_ids if role_id in role_map]


def resolve_request_user(request: Any) -> tuple[UserAccount | None, str | None]:
    """Resolve the middleware claims into an active user and role."""
    claims = getattr(request, "auth_claims", None)
    if not isinstance(claims, Mapping):
        return None, None
    try:
        user_id = int(str(claims.get("user_id")))
    except (TypeError, ValueError):
        return None, None
    user = UserAccount.objects.filter(id=user_id, status="active").first()
    if user is None:
        return None, None
    roles = get_user_roles(user.id)
    role_code = str(claims.get("role_code") or "")
    if not any(role.role_code == role_code for role in roles):
        return None, None
    return user, role_code


def require_request_user(request: Any) -> tuple[UserAccount, str]:
    user, role_code = resolve_request_user(request)
    if user is None or role_code is None:
        raise AuthenticationError("请先登录后再访问该资源。")
    return user, role_code


def switch_role(*, user: UserAccount, role_code: str) -> dict[str, Any]:
    roles = get_user_roles(user.id)
    if not any(role.role_code == role_code for role in roles):
        raise AuthorizationError("当前用户未分配该角色。")
    return build_session(user, roles, role_code)


def create_user(*, payload: Mapping[str, Any]) -> UserAccount:
    """Create a user and logical role memberships in one transaction."""
    username = str(payload.get("username") or "").strip()
    employee_no = str(payload.get("employee_no") or "").strip()
    display_name = str(payload.get("display_name") or "").strip()
    password_ciphertext = str(payload.get("password") or "")
    if not username or not employee_no or not display_name or not password_ciphertext:
        raise ValueError("用户名、工号、姓名和加密密码均不能为空。")
    try:
        plaintext = decrypt_client_password(password_ciphertext)
    except CryptoPayloadError as exc:
        raise ValueError("密码必须使用 RSA-OAEP-SHA256 加密。") from exc
    role_codes = _normalise_role_codes(payload.get("role_codes"))
    if not role_codes:
        raise ValueError("至少分配一个角色。")
    roles = list(Role.objects.filter(role_code__in=role_codes, status="active"))
    if len(roles) != len(set(role_codes)):
        raise ValueError("存在不可用的角色编码。")
    group_id = _optional_int(payload.get("group_id"))
    manager_id = _optional_int(payload.get("manager_id"))
    with transaction.atomic():
        user = UserAccount.objects.create(
            username=username,
            employee_no=employee_no,
            display_name=display_name,
            email=str(payload.get("email") or "").strip(),
            password_ciphertext=plaintext,
            group_id=group_id,
            manager_id=manager_id,
            avatar_color=str(payload.get("avatar_color") or "#2f80ed"),
            is_demo=bool(payload.get("is_demo", False)),
        )
        for index, role in enumerate(roles):
            UserRole.objects.create(user_id=user.id, role_id=role.id, is_default=index == 0)
    return user


def update_user(*, user: UserAccount, payload: Mapping[str, Any]) -> UserAccount:
    """Update profile/hierarchy and optionally replace the encrypted password."""
    allowed = {"display_name", "email", "group_id", "manager_id", "avatar_color", "status"}
    for field in allowed:
        if field in payload:
            value = payload[field]
            if field in {"group_id", "manager_id"}:
                value = _optional_int(value)
            elif field in {"display_name", "email", "avatar_color", "status"}:
                value = str(value or "").strip()
            setattr(user, field, value)
    if payload.get("password"):
        try:
            user.password_ciphertext = decrypt_client_password(str(payload["password"]))
        except CryptoPayloadError as exc:
            raise ValueError("密码必须使用 RSA-OAEP-SHA256 加密。") from exc
    user.save()
    if "role_codes" in payload:
        role_codes = _normalise_role_codes(payload.get("role_codes"))
        roles = list(Role.objects.filter(role_code__in=role_codes, status="active"))
        if len(roles) != len(set(role_codes)):
            raise ValueError("存在不可用的角色编码。")
        with transaction.atomic():
            UserRole.objects.filter(user_id=user.id).update(status="inactive")
            for index, role in enumerate(roles):
                UserRole.objects.update_or_create(
                    user_id=user.id,
                    role_id=role.id,
                    defaults={"status": "active", "is_default": index == 0},
                )
    return user


def serialize_user(user: UserAccount) -> dict[str, Any]:
    return {
        "id": str(user.id),
        "username": user.username,
        "employee_no": user.employee_no,
        "display_name": user.display_name,
        "email": user.email,
        "manager_id": str(user.manager_id) if user.manager_id is not None else None,
        "group_id": str(user.group_id) if user.group_id is not None else None,
        "avatar_color": user.avatar_color,
        "status": user.status,
    }


def serialize_role(role: Role) -> dict[str, Any]:
    return {
        "id": str(role.id),
        "role_code": role.role_code,
        "role_name": role.role_name,
        "scope": role.scope,
        "description": role.description,
        "report_template_code": role.report_template_code,
        "status": role.status,
        "sort_order": role.sort_order,
    }


def _choose_role(roles: list[Role], requested_role_code: str | None) -> Role:
    if requested_role_code:
        selected = next((role for role in roles if role.role_code == requested_role_code), None)
        if selected is None:
            raise AuthenticationError("当前用户未分配所选角色。")
        return selected
    return roles[0]


def _normalise_role_codes(value: Any) -> list[str]:
    if isinstance(value, str):
        values = [value]
    elif isinstance(value, list):
        values = value
    else:
        values = []
    return list(dict.fromkeys(str(item).strip() for item in values if str(item).strip()))


def _optional_int(value: Any) -> int | None:
    if value in (None, "", 0, "0"):
        return None
    try:
        return int(str(value))
    except (TypeError, ValueError) as exc:
        raise ValueError("组织关系 ID 必须是数字字符串。") from exc
