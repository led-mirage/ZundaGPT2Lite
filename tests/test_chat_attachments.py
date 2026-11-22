import pathlib
import sys
import unittest

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "app"))

from chat.chat import Chat  # type: ignore
from chat.chat_openai_base import ChatOpenAIBase  # type: ignore
from chat.error import StreamNotAllowedError  # type: ignore


class ChatStub(Chat):
    def send_onetime_message(self, text):
        return text

    def send_message(self, text, images, listener):
        return text


class OpenAIFallbackStub(ChatOpenAIBase):
    def __init__(self):
        super().__init__("model", None, "", "", 10, 0)
        self.request_histories = []

    def send_message_completions_streaming(self, text, images, listener):
        self.request_histories.append(self._get_history())
        raise StreamNotAllowedError(RuntimeError("stream unavailable"))

    def send_message_completions_not_streaming(self, text, images, listener):
        self.request_histories.append(self._get_history())
        return "response"


class TestChatAttachments(unittest.TestCase):
    def make_chat(self):
        return ChatStub("model", None, "", "", 10, 0)

    def test_message_history_keeps_attachment_metadata(self):
        chat = self.make_chat()
        attachments = [{"id": "image-id", "type": "image"}]
        chat.messages.append({
            "role": "user",
            "content": "hello",
            "attachments": attachments,
        })

        self.assertEqual(len(chat.messages), 1)
        self.assertEqual(chat.messages[0]["attachments"], attachments)

    def test_api_history_excludes_attachment_metadata(self):
        chat = self.make_chat()
        chat.messages.append({
            "role": "user",
            "content": "hello",
            "attachments": [{"id": "image-id", "type": "image"}],
        })

        history = chat._get_history()
        self.assertEqual(history, [{"role": "user", "content": "hello"}])

    def test_openai_fallback_reuses_history_without_duplicating_user_message(self):
        chat = OpenAIFallbackStub()

        response = chat.send_message("hello", [], None)

        self.assertEqual(response, "response")
        self.assertEqual(len(chat.messages), 1)
        self.assertEqual(chat.request_histories, [
            [{"role": "user", "content": "hello"}],
            [{"role": "user", "content": "hello"}],
        ])


if __name__ == "__main__":
    unittest.main()
