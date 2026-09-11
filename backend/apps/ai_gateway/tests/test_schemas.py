from django.test import SimpleTestCase

from apps.ai_gateway.schemas import ChatPayloadError, ChatRequest


class ChatRequestTests(SimpleTestCase):
    def test_parses_valid_messages(self) -> None:
        request = ChatRequest.from_payload(
            {"messages": [{"role": "user", "content": "  生成周报  "}]}
        )

        self.assertEqual(len(request.messages), 1)
        self.assertEqual(request.messages[0].content, "生成周报")

    def test_rejects_empty_messages(self) -> None:
        with self.assertRaises(ChatPayloadError):
            ChatRequest.from_payload({"messages": []})
