import base64
import io
import json
import pathlib
import sys
import tempfile
import unittest

from PIL import Image

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "app"))

from chat.chat import Chat  # type: ignore
from chat_log import ChatLog  # type: ignore
from services.index_service import IndexService  # type: ignore


def make_data_url():
    buffer = io.BytesIO()
    Image.new("RGB", (640, 480), "green").save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


class SettingsStub:
    settings = {}
    user = {}
    assistant = {}
    chat = {}
    custom_style = {}
    claude_options = {}


class AppConfigStub:
    system = {"speaker_on": False}


class StateStub:
    def __init__(self, chat):
        self.chat = chat
        self.settings = SettingsStub()
        self.last_send_message = None
        self.user_character = None
        self.assistant_character = None


class JSStub:
    def __init__(self):
        self.sent_user_messages = []
        self.chat_messages = []
        self.errors = []
        self.completed_prompts = 0
        self.rolled_back_messages = 0

    def addSendingUserMessage(self, text, attachments):
        self.sent_user_messages.append((text, attachments))

    def completeSentPrompt(self):
        self.completed_prompts += 1

    def rollbackSendingMessage(self):
        self.rolled_back_messages += 1

    def startResponse(self):
        pass

    def endResponse(self, content):
        pass

    def setChatMessages(self, messages, preserve_pending=False):
        self.chat_messages = messages

    def handleChatException(self, message):
        self.errors.append(message)

    def handleChatTimeoutException(self, message):
        self.errors.append(message)

    def handleAttachmentException(self, message):
        self.errors.append(message)


class WindowStub:
    def __init__(self):
        self.js = JSStub()


class FailingChat(Chat):
    def send_onetime_message(self, text):
        return text

    def send_message(self, text, images, listener):
        self.messages.append({"role": "user", "content": text})
        listener.on_error(RuntimeError("api failed"), "APIError", "api failed")


class SuccessfulChat(Chat):
    def send_onetime_message(self, text):
        return text

    def send_message(self, text, images, listener):
        self.messages.append({"role": "user", "content": text})
        self.messages.append({"role": "assistant", "content": "response"})
        listener.on_end_response("response")


class TestIndexServiceAttachments(unittest.TestCase):
    def test_image_only_api_error_discards_message_and_keeps_prompt(self):
        old_log_folder = ChatLog.LOG_FOLDER
        old_cache = ChatLog.cache
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                ChatLog.LOG_FOLDER = temp_dir
                ChatLog.cache = {}
                chat = FailingChat("model", None, "", "", 10, 0)
                state = StateStub(chat)
                window = WindowStub()
                service = IndexService(AppConfigStub(), state, window)

                result = service.send_message_to_chatgpt("", [make_data_url()])

                self.assertTrue(result)
                self.assertEqual(chat.messages, [])
                self.assertEqual(len(window.js.sent_user_messages), 1)
                self.assertEqual(window.js.completed_prompts, 0)
                self.assertEqual(window.js.rolled_back_messages, 1)
                self.assertTrue(window.js.errors)

                log_path = pathlib.Path(temp_dir) / ChatLog.get_logfile_name(chat)
                attachment_dir = pathlib.Path(temp_dir) / "attachments" / log_path.stem
                self.assertFalse(log_path.exists())
                self.assertFalse(attachment_dir.exists())
        finally:
            ChatLog.LOG_FOLDER = old_log_folder
            ChatLog.cache = old_cache

    def test_successful_image_only_message_is_saved_with_attachment(self):
        old_log_folder = ChatLog.LOG_FOLDER
        old_cache = ChatLog.cache
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                ChatLog.LOG_FOLDER = temp_dir
                ChatLog.cache = {}
                chat = SuccessfulChat("model", None, "", "", 10, 0)
                state = StateStub(chat)
                window = WindowStub()
                service = IndexService(AppConfigStub(), state, window)

                result = service.send_message_to_chatgpt("", [make_data_url()])

                self.assertTrue(result)
                self.assertEqual(len(chat.messages), 2)
                self.assertEqual(len(chat.messages[0]["attachments"]), 1)
                self.assertEqual(window.js.completed_prompts, 1)
                self.assertEqual(window.js.rolled_back_messages, 0)

                log_path = pathlib.Path(temp_dir) / ChatLog.get_logfile_name(chat)
                data = json.loads(log_path.read_text(encoding="utf-8"))
                self.assertEqual(data["file_ver"], 11)
                self.assertEqual(len(data["messages"][0]["attachments"]), 1)

                attachment_dir = pathlib.Path(temp_dir) / "attachments" / log_path.stem
                self.assertTrue(attachment_dir.is_dir())
                ChatLog.delete_log_file(chat)
                self.assertFalse(log_path.exists())
                self.assertFalse(attachment_dir.exists())
        finally:
            ChatLog.LOG_FOLDER = old_log_folder
            ChatLog.cache = old_cache


if __name__ == "__main__":
    unittest.main()
