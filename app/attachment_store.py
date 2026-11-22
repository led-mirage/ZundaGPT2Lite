# ZundaGPT2 / ZundaGPT2 Lite
#
# チャット添付ファイルの保存・読込
#
# Copyright (c) 2024-2026 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import base64
import binascii
import io
import mimetypes
import os
import shutil
import uuid
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError


class AttachmentError(Exception):
    # 添付ファイル処理で発生したエラー情報を初期化する
    def __init__(self, code: str, **params):
        super().__init__(code)
        self.code = code
        self.params = params


class AttachmentStore:
    ATTACHMENTS_FOLDER = "attachments"
    MAX_IMAGE_COUNT = 10
    MAX_IMAGE_BYTES = 10 * 1024 * 1024
    MAX_TOTAL_BYTES = 50 * 1024 * 1024
    MAX_IMAGE_PIXELS = 40_000_000
    THUMBNAIL_MAX_SIZE = (320, 320)

    SUPPORTED_FORMATS = {
        "PNG": ("image/png", ".png"),
        "JPEG": ("image/jpeg", ".jpg"),
        "WEBP": ("image/webp", ".webp"),
    }

    # 添付ファイルの保存先となるログフォルダを設定する
    def __init__(self, log_folder: str):
        self.log_folder = Path(log_folder)

    # Data URL形式の画像を検証し、画像本体とサムネイルを保存する
    def save_images(self, chat, data_urls: list[str]) -> list[dict]:
        if not data_urls:
            return []
        if len(data_urls) > self.MAX_IMAGE_COUNT:
            raise AttachmentError("ERROR_ATTACHMENT_COUNT", max=self.MAX_IMAGE_COUNT)

        decoded = []
        total_bytes = 0
        for data_url in data_urls:
            image_bytes = self._decode_data_url(data_url)
            if len(image_bytes) > self.MAX_IMAGE_BYTES:
                raise AttachmentError("ERROR_ATTACHMENT_FILE_SIZE", max=10)
            total_bytes += len(image_bytes)
            if total_bytes > self.MAX_TOTAL_BYTES:
                raise AttachmentError("ERROR_ATTACHMENT_TOTAL_SIZE", max=50)
            decoded.append(image_bytes)

        attachment_dir = self.get_chat_attachment_dir(chat)
        attachment_dir.mkdir(parents=True, exist_ok=True)
        for temp_path in attachment_dir.glob(".*.tmp"):
            temp_path.unlink(missing_ok=True)
        created_paths = []
        attachments = []

        try:
            for image_bytes in decoded:
                attachment, paths = self._save_image(chat, attachment_dir, image_bytes)
                attachments.append(attachment)
                created_paths.extend(paths)
            return attachments
        except Exception:
            for path in created_paths:
                path.unlink(missing_ok=True)
            self._remove_empty_parents(attachment_dir)
            raise

    # 1枚の画像について画像本体とサムネイルを保存し、添付情報を作成する
    def _save_image(self, chat, attachment_dir: Path, image_bytes: bytes):
        try:
            with Image.open(io.BytesIO(image_bytes)) as image:
                image_format = (image.format or "").upper()
                if image_format not in self.SUPPORTED_FORMATS:
                    raise AttachmentError("ERROR_ATTACHMENT_FORMAT")
                if getattr(image, "is_animated", False) and getattr(image, "n_frames", 1) > 1:
                    raise AttachmentError("ERROR_ATTACHMENT_ANIMATED")

                width, height = image.size
                if width <= 0 or height <= 0 or width * height > self.MAX_IMAGE_PIXELS:
                    raise AttachmentError("ERROR_ATTACHMENT_PIXELS", max=40)

                image.verify()

            mime_type, extension = self.SUPPORTED_FORMATS[image_format]
            attachment_id = str(uuid.uuid4())
            original_path = attachment_dir / f"{attachment_id}{extension}"
            thumbnail_path = attachment_dir / f"{attachment_id}.thumb.png"
            original_temp = attachment_dir / f".{attachment_id}.original.tmp"
            thumbnail_temp = attachment_dir / f".{attachment_id}.thumbnail.tmp"

            try:
                original_temp.write_bytes(image_bytes)
                self._create_thumbnail(image_bytes, thumbnail_temp)
                os.replace(original_temp, original_path)
                os.replace(thumbnail_temp, thumbnail_path)
            except Exception:
                original_temp.unlink(missing_ok=True)
                thumbnail_temp.unlink(missing_ok=True)
                original_path.unlink(missing_ok=True)
                thumbnail_path.unlink(missing_ok=True)
                raise

            relative_original = original_path.relative_to(self.log_folder).as_posix()
            relative_thumbnail = thumbnail_path.relative_to(self.log_folder).as_posix()
            attachment = {
                "id": attachment_id,
                "type": "image",
                "mime_type": mime_type,
                "path": relative_original,
                "thumbnail_path": relative_thumbnail,
                "width": width,
                "height": height,
            }
            return attachment, [original_path, thumbnail_path]
        except AttachmentError:
            raise
        except (UnidentifiedImageError, OSError, ValueError, SyntaxError):
            raise AttachmentError("ERROR_ATTACHMENT_INVALID")

    # 画像データから最大辺320pxのPNGサムネイルを作成する
    def _create_thumbnail(self, image_bytes: bytes, destination: Path):
        with Image.open(io.BytesIO(image_bytes)) as image:
            image.seek(0)
            image = ImageOps.exif_transpose(image)
            image.thumbnail(self.THUMBNAIL_MAX_SIZE, Image.Resampling.LANCZOS)
            if image.mode not in ("1", "L", "LA", "P", "RGB", "RGBA"):
                image = image.convert("RGB")
            image.save(destination, format="PNG", optimize=True)

    # 保存済み添付情報から画面表示用のサムネイル情報を作成する
    def build_ui_attachments(self, chat, attachments: list[dict]) -> list[dict]:
        result = []
        for attachment in attachments or []:
            if attachment.get("type") != "image":
                continue

            try:
                thumbnail_path = self._resolve_path(attachment.get("thumbnail_path", ""))
                original_path = self._resolve_path(attachment.get("path", ""))
            except AttachmentError:
                thumbnail_path = None
                original_path = None
            if thumbnail_path and original_path and not thumbnail_path.is_file() and original_path.is_file():
                try:
                    temp_path = thumbnail_path.with_name(f".{thumbnail_path.name}.tmp")
                    thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
                    self._create_thumbnail(original_path.read_bytes(), temp_path)
                    os.replace(temp_path, thumbnail_path)
                except Exception:
                    temp_path.unlink(missing_ok=True)

            thumbnail_data_url = self._file_to_data_url(thumbnail_path, "image/png")
            result.append({
                "id": attachment.get("id", ""),
                "type": "image",
                "width": attachment.get("width", 0),
                "height": attachment.get("height", 0),
                "thumbnail_data_url": thumbnail_data_url,
                "missing": not bool(thumbnail_data_url),
            })
        return result

    # 保存済みの画像本体をData URL形式で読み込む
    def get_original_data_url(self, attachment: dict) -> str:
        try:
            path = self._resolve_path(attachment.get("path", ""))
        except AttachmentError:
            return ""
        return self._file_to_data_url(path, attachment.get("mime_type", "application/octet-stream"))

    # 複数の添付情報から画像本体のData URL一覧を読み込む
    def load_original_data_urls(self, attachments: list[dict]) -> list[str]:
        result = []
        for attachment in attachments or []:
            data_url = self.get_original_data_url(attachment)
            if data_url:
                result.append(data_url)
        return result

    # チャットログから参照されていない添付ファイルを削除する
    def cleanup_unreferenced(self, chat):
        # _resolve_path() が返す絶対パスと同じ形式にそろえて比較する
        attachment_dir = self.get_chat_attachment_dir(chat).resolve()
        if not attachment_dir.is_dir():
            return

        referenced = set()
        for message in chat.messages:
            for attachment in message.get("attachments", []):
                for key in ("path", "thumbnail_path"):
                    try:
                        path = self._resolve_path(attachment.get(key, ""))
                    except AttachmentError:
                        continue
                    if path is not None:
                        referenced.add(path)

        for path in attachment_dir.iterdir():
            if path.is_file() and path not in referenced:
                path.unlink(missing_ok=True)
        self._remove_empty_parents(attachment_dir)

    # 指定された添付情報に対応する画像本体とサムネイルを削除する
    def delete_attachments(self, attachments: list[dict]):
        parent_dirs = set()
        for attachment in attachments or []:
            for key in ("path", "thumbnail_path"):
                try:
                    path = self._resolve_path(attachment.get(key, ""))
                except AttachmentError:
                    continue
                if path is not None:
                    parent_dirs.add(path.parent)
                    path.unlink(missing_ok=True)
        for parent in parent_dirs:
            self._remove_empty_parents(parent)

    # 指定されたチャットに属する添付ファイルをすべて削除する
    def delete_chat_attachments(self, chat):
        attachment_dir = self.get_chat_attachment_dir(chat)
        if attachment_dir.is_dir():
            shutil.rmtree(attachment_dir)
        self._remove_empty_parents(attachment_dir)

    # 指定されたチャットの添付ファイル保存フォルダを取得する
    def get_chat_attachment_dir(self, chat) -> Path:
        logfile_stem = chat.chat_start_time.strftime("chatlog-%Y%m%d-%H%M%S")
        return self.log_folder / self.ATTACHMENTS_FOLDER / logfile_stem

    # 相対パスを安全な添付ファイル用絶対パスへ変換する
    def _resolve_path(self, relative_path: str) -> Path | None:
        if not relative_path:
            return None
        log_root = self.log_folder.resolve()
        attachment_root = (log_root / self.ATTACHMENTS_FOLDER).resolve()
        resolved = (log_root / relative_path).resolve()
        try:
            resolved.relative_to(attachment_root)
        except ValueError:
            raise AttachmentError("ERROR_ATTACHMENT_INVALID_PATH")
        return resolved

    # Data URLからBase64エンコードされたバイナリデータを取り出す
    def _decode_data_url(self, data_url: str) -> bytes:
        if not isinstance(data_url, str) or ";base64," not in data_url:
            raise AttachmentError("ERROR_ATTACHMENT_INVALID")
        encoded = data_url.split(";base64,", 1)[1]
        try:
            return base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError):
            raise AttachmentError("ERROR_ATTACHMENT_INVALID")

    # ファイルの内容をData URL形式へ変換する
    @staticmethod
    def _file_to_data_url(path: Path | None, mime_type: str) -> str:
        if path is None or not path.is_file():
            return ""
        mime_type = mime_type or mimetypes.guess_type(path)[0] or "application/octet-stream"
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:{mime_type};base64,{encoded}"

    # 添付ファイル削除後に空になった保存フォルダを削除する
    def _remove_empty_parents(self, attachment_dir: Path):
        attachments_root = self.log_folder / self.ATTACHMENTS_FOLDER
        if attachment_dir.is_dir() and not any(attachment_dir.iterdir()):
            attachment_dir.rmdir()
        if attachments_root.is_dir() and not any(attachments_root.iterdir()):
            attachments_root.rmdir()
