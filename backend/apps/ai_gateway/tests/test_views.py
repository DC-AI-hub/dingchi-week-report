import json

from django.test import SimpleTestCase
from django.urls import reverse


class ChatCompletionViewTests(SimpleTestCase):
    def test_rejects_invalid_json(self) -> None:
        response = self.client.post(
            reverse("ai_gateway:chat-completion"),
            data="not-json",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "INVALID_JSON")

    def test_reports_missing_ai_configuration(self) -> None:
        response = self.client.post(
            reverse("ai_gateway:chat-completion"),
            data=json.dumps({"messages": [{"role": "user", "content": "生成周报"}]}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["error"]["code"], "AI_NOT_CONFIGURED")
