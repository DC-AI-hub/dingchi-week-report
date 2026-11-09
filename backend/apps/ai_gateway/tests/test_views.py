import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from django.test import SimpleTestCase
from django.urls import reverse

from apps.accounts.models import Role, UserAccount, UserRole
from apps.core.authentication.token import create_access_token


class ChatCompletionViewTests(SimpleTestCase):
    @patch("apps.ai_gateway.views.get_chat_service")
    def test_unauthenticated_request_never_calls_provider(self, service) -> None:
        response = self.client.post(
            reverse("ai_gateway:chat-completion"),
            data=json.dumps({"messages": [{"role": "user", "content": "生成周报"}]}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "AUTHENTICATION_FAILED")
        service.assert_not_called()

    @patch("apps.ai_gateway.views.require_user", return_value=(object(), "member"))
    def test_rejects_invalid_json(self, _require_user) -> None:
        response = self.client.post(
            reverse("ai_gateway:chat-completion"),
            data="not-json",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "INVALID_JSON")

    @patch("apps.ai_gateway.views.require_user", return_value=(object(), "member"))
    def test_reports_missing_ai_configuration(self, _require_user) -> None:
        response = self.client.post(
            reverse("ai_gateway:chat-completion"),
            data=json.dumps({"messages": [{"role": "user", "content": "生成周报"}]}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["error"]["code"], "AI_NOT_CONFIGURED")


@pytest.mark.django_db
def test_valid_bearer_token_allows_ai_chat(client) -> None:
    user = UserAccount.objects.create(
        username="ai-user",
        employee_no="AI001",
        display_name="AI用户",
        password_ciphertext="test-secret-8",
    )
    role = Role.objects.create(role_code="ai-member", role_name="成员")
    UserRole.objects.create(user_id=user.id, role_id=role.id)
    token = create_access_token(user_id=int(user.id), role_code=role.role_code)
    result = SimpleNamespace(to_dict=lambda: {"content": "周报总结"})
    with patch("apps.ai_gateway.views.get_chat_service") as service:
        service.return_value.complete = AsyncMock(return_value=result)
        response = client.post(
            reverse("ai_gateway:chat-completion"),
            data=json.dumps({"messages": [{"role": "user", "content": "生成周报"}]}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
    assert response.status_code == 200
    assert response.json()["data"]["content"] == "周报总结"
    service.return_value.complete.assert_awaited_once()
