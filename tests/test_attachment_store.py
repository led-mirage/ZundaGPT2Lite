import base64
import io
import os
import pathlib
import sys
import tempfile
import unittest
from datetime import datetime

from PIL import Image

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "app"))

from attachment_store import AttachmentError, AttachmentStore  # type: ignore


class ChatStub:
    def __init__(self):
        self.chat_start_time = datetime(2026, 11, 17, 12, 0, 0)
        self.messages = []


def make_data_url(image_format="PNG", size=(640, 480)):
    buffer = io.BytesIO()
    Image.new("RGB", size, "green").save(buffer, format=image_format)
    mime = "image/jpeg" if image_format == "JPEG" else "image/png"
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


class TestAttachmentStore(unittest.TestCase):
    def test_save_load_thumbnail_and_cleanup(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            chat = ChatStub()
            store = AttachmentStore(temp_dir)

            attachments = store.save_images(chat, [make_data_url()])
            self.assertEqual(len(attachments), 1)
            attachment = attachments[0]
            self.assertTrue(attachment["path"].startswith("attachments/"))
            self.assertTrue(attachment["thumbnail_path"].endswith(".thumb.png"))

            original_path = pathlib.Path(temp_dir) / attachment["path"]
            thumbnail_path = pathlib.Path(temp_dir) / attachment["thumbnail_path"]
            self.assertTrue(original_path.is_file())
            self.assertTrue(thumbnail_path.is_file())
            with Image.open(thumbnail_path) as thumbnail:
                self.assertLessEqual(max(thumbnail.size), 320)

            ui_attachments = store.build_ui_attachments(chat, attachments)
            self.assertTrue(ui_attachments[0]["thumbnail_data_url"].startswith("data:image/png;base64,"))
            self.assertTrue(store.get_original_data_url(attachment).startswith("data:image/png;base64,"))

            chat.messages = [{"role": "user", "content": "image", "attachments": attachments}]
            store.cleanup_unreferenced(chat)
            self.assertTrue(original_path.exists())

            chat.messages = []
            store.cleanup_unreferenced(chat)
            self.assertFalse(original_path.exists())
            self.assertFalse(thumbnail_path.exists())

    def test_rejects_unsupported_format(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            chat = ChatStub()
            store = AttachmentStore(temp_dir)
            buffer = io.BytesIO()
            Image.new("RGB", (10, 10), "red").save(buffer, format="BMP")
            encoded = base64.b64encode(buffer.getvalue()).decode("ascii")

            with self.assertRaises(AttachmentError) as context:
                store.save_images(chat, [f"data:image/bmp;base64,{encoded}"])
            self.assertEqual(context.exception.code, "ERROR_ATTACHMENT_FORMAT")

    def test_rejects_more_than_ten_images(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            chat = ChatStub()
            store = AttachmentStore(temp_dir)
            image = make_data_url(size=(1, 1))

            with self.assertRaises(AttachmentError) as context:
                store.save_images(chat, [image] * 11)
            self.assertEqual(context.exception.code, "ERROR_ATTACHMENT_COUNT")

    def test_cleanup_keeps_referenced_files_with_relative_log_folder(self):
        with tempfile.TemporaryDirectory(dir=".") as temp_dir:
            relative_log_folder = os.path.relpath(temp_dir, pathlib.Path.cwd())
            chat = ChatStub()
            store = AttachmentStore(relative_log_folder)
            attachments = store.save_images(chat, [make_data_url()])
            chat.messages = [{
                "role": "user",
                "content": "image",
                "attachments": attachments,
            }]

            original_path = pathlib.Path(temp_dir) / attachments[0]["path"]
            thumbnail_path = pathlib.Path(temp_dir) / attachments[0]["thumbnail_path"]
            store.cleanup_unreferenced(chat)

            self.assertTrue(original_path.is_file())
            self.assertTrue(thumbnail_path.is_file())


if __name__ == "__main__":
    unittest.main()
