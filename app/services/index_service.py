# ZundaGPT2 Lite
#
# メイン画面のサービス
#
# Copyright (c) 2024-2026 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import base64
import copy
import re

import langdetect

from config.app_config import AppConfig, get_log_settings
from config.app_settings import Settings
from app_logger import AppLogger
from app_state import AppState
from app_window import AppWindow
from chat_log import ChatLog
from const import APP_NAME, APP_VERSION
from utility.utils import get_location, get_exception_name, to_css_url_format
from utility.multi_lang import set_current_language, get_text_resource
from chat import Chat, ChatFactory, ChatFactoryOptions, SendMessageListener
from attachment_store import AttachmentError, AttachmentStore


log_settings = get_log_settings()
AppLogger.init_logger(log_settings["log_folder"], log_settings["log_level"])


class IndexService:
    def __init__(self, app_config: AppConfig, state: AppState, window: AppWindow):
        self.app_config = app_config
        self.state = state
        self.window = window
        self._pending_send = None

    def get_attachment_store(self):
        return AttachmentStore(ChatLog.LOG_FOLDER)

    # ページロードイベントハンドラ（UI）
    def page_loaded(self):
        self.window.js.inject_custom_css()

        lang = self.app_config.system["language"]
        set_current_language(lang)

        if self.state.chat == None:
            self.new_chat()
        else:
            self.set_chatinfo_to_ui()
            self.set_chatmessages_to_ui(self.state.chat.messages)
            self.set_window_title()
            if self.state.initial_message_index >= 0:
                self.window.js.moveToMessageAt(self.state.initial_message_index, self.state.initial_highlight_text)
                self.state.initial_message_index = -1
                self.state.initial_highlight_text = ""

    # 新しいチャットを開始する
    def new_chat(self):
        self.state.settings = Settings()
        self.state.settings.load()
        
        ChatLog.LOG_FOLDER = self.app_config.system["log_folder"]

        options = ChatFactoryOptions(
            api_id = self.state.settings.chat["api"],
            model = self.state.settings.chat["model"],
            temperature = self.state.settings.chat["temperature"],
            instruction = self.state.settings.chat["instruction"],
            bad_response = self.state.settings.chat["bad_response"],
            history_size = self.state.settings.chat["history_size"],
            history_char_limit = self.state.settings.chat["history_char_limit"],
            api_timeout = self.app_config.system["chat_api_timeout"],
            api_key_envvar = self.state.settings.chat["api_key_envvar"],
            api_endpoint_envvar = self.state.settings.chat["api_endpoint_envvar"],
            api_base_url = self.state.settings.chat["api_base_url"],
            gemini_option = self.app_config.gemini,
            claude_options = self.state.settings.claude_options
        )

        self.state.chat = ChatFactory.create(options)
        self.state.last_send_message = None

        self.set_chatinfo_to_ui()
        self.set_window_title()

    # ウィンドウのタイトルを設定する
    def set_window_title(self):
        logfile = ChatLog.get_logfile_name(self.state.chat)
        window_title = f"{APP_NAME}  ver {APP_VERSION} - {logfile}"
        self.window.set_window_title(window_title)

    # 画像をBase64エンコードする
    def get_image_base64(self, path: str):
        if not path:
            return ""
        try:
            with open(path, 'rb') as f:
                data = base64.b64encode(f.read())
                return data.decode('utf-8')
        except:
            return ""

    # チャットの情報をUIに通知する
    def set_chatinfo_to_ui(self):
        settings = {
            "display_name": self.state.settings.settings.get("display_name", ""),
            "welcome_title": self.state.settings.settings.get("welcome_title", ""),
            "welcome_message": self.state.settings.settings.get("welcome_message", ""),
            "welcome_icon_visible": self.state.settings.settings.get("welcome_icon_visible", True),
        }

        user = {
            "name": self.state.settings.user["name"],
            "color": self.state.settings.user["name_color"],
            "icon": self.get_image_base64(self.state.settings.user["icon"])
        }

        assistant = {
            "name": self.state.settings.assistant["name"],
            "color": self.state.settings.assistant["name_color"],
            "icon": self.get_image_base64(self.state.settings.assistant["icon"])
        }

        custom_style = {
            "enable": self.state.settings.custom_style.get("enable", False),
            "background_image": to_css_url_format(self.state.settings.custom_style.get("background_image", ""), 1.5),
            "background_image_opacity": self.state.settings.custom_style.get("background_image_opacity", "0.8"),
            "body_bgcolor": self.state.settings.custom_style.get("body_bgcolor", ""),
            "header_color": self.state.settings.custom_style.get("header_color", ""),
            "welcome_title_color": self.state.settings.custom_style.get("welcome_title_color", ""),
            "welcome_message_color": self.state.settings.custom_style.get("welcome_message_color", ""),
            "speaker_name_text_shadow": self.state.settings.custom_style.get("speaker_name_text_shadow", ""),
            "message_text_bgcolor": self.state.settings.custom_style.get("message_text_bgcolor", ""),
            "message_text_color": self.state.settings.custom_style.get("message_text_color", ""),
            "message_text_shadow": self.state.settings.custom_style.get("message_text_shadow", ""),
            "message_text_border_radius": self.state.settings.custom_style.get("message_text_border_radius", ""),
            "message_text_em_color": self.state.settings.custom_style.get("message_text_em_color", ""),
        }

        chat = {
            "ai_agent_available": self.state.chat.is_ai_agent_available(),
            "ai_agent_creation_error": self.state.chat.client_creation_error
        }

        info = {
            "settings": settings,
            "user": user,
            "assistant": assistant,
            "custom_style": custom_style,
            "chat": chat
        }

        self.window.js.setChatInfo(info)

    # ひとつ前のチャットを表示して続ける
    def prev_chat(self):
        logfile = ChatLog.get_prev_logfile(self.state.chat)
        if logfile is None:
            return

        loaded_settings, loaded_chat = ChatLog.load(logfile)
        if loaded_settings is None:
            return
        
        self.change_current_chat(loaded_settings, loaded_chat)

    # ひとつ後のチャットを表示して続ける
    def next_chat(self):
        logfile = ChatLog.get_next_logfile(self.state.chat)
        if logfile is None:
            return

        loaded_settings, loaded_chat = ChatLog.load(logfile)
        if loaded_settings is None:
            return
        
        self.change_current_chat(loaded_settings, loaded_chat)

    # カレントチャットを変更する
    def change_current_chat(self, loaded_settings: Settings, loaded_chat: Chat):
        self.state.settings = loaded_settings
        self.state.chat = loaded_chat
        self.state.last_send_message = None
        self.set_chatinfo_to_ui()
        self.set_chatmessages_to_ui(loaded_chat.messages)
        self.set_window_title()

    # チャットの内容をUIに送信する
    def set_chatmessages_to_ui(self, messages: list[dict], preserve_pending=False):
        ui_messages = copy.deepcopy(messages)
        store = self.get_attachment_store()
        for message in ui_messages:
            message["ui_attachments"] = store.build_ui_attachments(
                self.state.chat,
                message.get("attachments", [])
            )
        self.window.js.setChatMessages(ui_messages, preserve_pending)

    # カレントチャット削除イベントハンドラ（UI）
    def delete_current_chat(self):
        if not ChatLog.exists_log_file(self.state.chat):
            return

        prev_logfile = ChatLog.get_prev_logfile(self.state.chat)
        next_logfile = ChatLog.get_next_logfile(self.state.chat)

        is_empty = (prev_logfile is None) and (next_logfile is None)
        is_tail = (next_logfile is None)
        ChatLog.delete_log_file(self.state.chat)
        if is_empty or is_tail:
            self.window.js.newChat()
        else:
            loaded_settings, loaded_chat = ChatLog.load(prev_logfile)
            if loaded_settings is None:
                return
            self.change_current_chat(loaded_settings, loaded_chat)

    # メッセージ送信イベントハンドラ（UI）
    def send_message_to_chatgpt(self, text, images):
        images = images or []
        if not text and not images:
            return False

        attachments = []
        store = self.get_attachment_store()
        try:
            if images:
                if not ChatLog.LOG_FOLDER:
                    raise AttachmentError("ERROR_ATTACHMENT_SAVE")
                attachments = store.save_images(self.state.chat, images)
        except AttachmentError as e:
            self.window.js.handleAttachmentException(self.format_attachment_error(e))
            return False
        except Exception:
            self.window.js.handleAttachmentException(
                get_text_resource("ERROR_ATTACHMENT_SAVE")
            )
            return False

        self._pending_send = {
            "user_index": len(self.state.chat.messages),
            "attachments": attachments,
            "delete_attachments_on_error": True,
            "restore_messages": None,
            "clear_prompt_on_success": True,
        }
        ui_attachments = store.build_ui_attachments(self.state.chat, attachments)
        self.window.js.addSendingUserMessage(text, ui_attachments)
        self.window.js.startResponse()
        self.state.chat.send_message(
            text,
            images,
            listener=SendMessageListener(
                self.on_receive_chunk,
                self.on_receive_sentence,
                self.on_receive_paragraph,
                self.on_non_streaming_start,
                self.on_non_streaming_end,
                self.on_end_response,
                self.on_chat_error
            )
        )
        return True

    def format_attachment_error(self, error: AttachmentError):
        message = get_text_resource(error.code)
        for key, value in error.params.items():
            message = message.replace(f"${{{key}}}", str(value))
        return message

    def find_attachment(self, attachment_id: str):
        for message in self.state.chat.messages:
            for attachment in message.get("attachments", []):
                if attachment.get("id") == attachment_id:
                    return attachment
        return None

    def get_attachment_image(self, attachment_id: str):
        attachment = self.find_attachment(attachment_id)
        if attachment is None:
            return ""
        return self.get_attachment_store().get_original_data_url(attachment)

    # メッセージ送信中止イベントハンドラ（UI）
    def stop_send_message_to_chatgpt(self):
        self.state.chat.stop_send_message()

    # メッセージ削除イベントハンドラ（UI）
    def truncate_messages(self, index):
        original_messages = self.state.chat.messages
        self.state.chat.messages = self.state.chat.messages[:index]
        try:
            ChatLog.save(self.state.settings, self.state.chat)
            self.get_attachment_store().cleanup_unreferenced(self.state.chat)
        except Exception:
            self.state.chat.messages = original_messages
            raise

    # 別の回答を取得するイベントハンドラ（UI）
    def ask_another_reply_to_chatgpt(self, index):
        original_messages = copy.deepcopy(self.state.chat.messages)
        message = self.state.chat.messages[index - 1]
        text = message["content"]
        attachments = copy.deepcopy(message.get("attachments", []))
        images = self.get_attachment_store().load_original_data_urls(attachments)
        if attachments and len(images) != len(attachments):
            self.window.js.handleAttachmentException(
                get_text_resource("ERROR_ATTACHMENT_LOAD")
            )
            self.set_chatmessages_to_ui(self.state.chat.messages)
            return
        self.state.chat.truncate_messages(index - 1)
        self._pending_send = {
            "user_index": len(self.state.chat.messages),
            "attachments": attachments,
            "delete_attachments_on_error": False,
            "restore_messages": original_messages,
            "clear_prompt_on_success": False,
        }
        self.window.js.startResponse()
        self.state.chat.send_message(
            text,
            images,
            listener=SendMessageListener(
                self.on_receive_chunk,
                self.on_receive_sentence,
                self.on_receive_paragraph,
                self.on_non_streaming_start,
                self.on_non_streaming_end,
                self.on_end_response,
                self.on_chat_error
            )
        )

    # チャットメッセージのテキストを取得する（UI）
    def get_message_text(self, index):
        message = self.state.chat.messages[index]
        text = message["content"] + "\n"
        attachment_count = len(message.get("attachments", []))
        if attachment_count:
            marker = get_text_resource("ATTACHED_IMAGE_COUNT").replace(
                "${count}", str(attachment_count)
            )
            text += marker + "\n"
        return text

    # チャットのすべてのメッセージを取得する（UI）
    def get_all_message_text(self, add_header=True):
        text = ""

        if add_header:
            text += "---\n"
            text += f"{self.state.settings.settings['display_name']}\n"
            text += f"チャット開始日時: {self.state.chat.chat_start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            text += f"チャット更新日時: {self.state.chat.chat_update_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            text += f"ログファイル: {ChatLog.get_logfile_name(self.state.chat)}\n"
            text += f"API: {self.state.settings.chat['api']}\n"
            text += f"モデル: {self.state.settings.chat['model']}\n"
            text += "---\n"
            text += "\n"

        for message in self.state.chat.messages:
            role = message["role"]
            if role == "user":
                name = self.state.settings.user["name"]
            elif role == "assistant":
                name = self.state.settings.assistant["name"]
            else:
                continue

            text += f"## {name}\n\n"
            text += f"{message['content']}\n\n"
            attachment_count = len(message.get("attachments", []))
            if attachment_count:
                marker = get_text_resource("ATTACHED_IMAGE_COUNT").replace(
                    "${count}", str(attachment_count)
                )
                text += marker + "\n\n"
        return text

    # チャットの内容を要約する
    def summarize_chat(self):
        messages = self.get_all_message_text(add_header=False)
        lang = langdetect.detect(messages)
        query = get_text_resource("SUMMARIZE_PROMPT", lang) + messages

        try:
            summary = self.state.chat.send_onetime_message(query)

            # 回答全体がコードブロックで囲まれていたら、それを外す
            pattern = r'```[a-zA-Z]*\n(.*?)\n```'
            match = re.search(pattern, summary, re.DOTALL)
            if match:
                summary = match.group(1)

            return summary
        except Exception as e:
            location = get_location(self)
            error_type = get_exception_name(e)
            AppLogger.error(f"Failed to summarize chat")
            AppLogger.error(f"  -> location : {location}")
            AppLogger.error(f"  -> exception : {error_type}")
            print(e)
            return ""

    # チャンク受信イベントハンドラ（Chat）
    def on_receive_chunk(self, chunk: str):
        self.window.js.addChunk(chunk)

    # センテンス受信イベントハンドラ（Chat）
    def on_receive_sentence(self, sentence: str):
        self.window.js.parsedSentence(sentence)

    # 段落受信イベントハンドラ（Chat）
    def on_receive_paragraph(self, paragraph: str):
        self.window.js.parsedParagraph(paragraph)

    # 非ストリーミング開始イベントハンドラ（Chat）
    def on_non_streaming_start(self):
        self.window.js.showProgressModal(get_text_resource("GENERATING_RESPONSE"))

    # 非ストリーミング終了イベントハンドラ（Chat）
    def on_non_streaming_end(self):
        self.window.js.hideProgressModal()

    # レスポンス受信完了イベントハンドラ（Chat）
    def on_end_response(self, content: str):
        pending_send = self._pending_send
        self._pending_send = None
        if pending_send is not None:
            user_index = pending_send["user_index"]
            if user_index < len(self.state.chat.messages):
                user_message = self.state.chat.messages[user_index]
                if user_message.get("role") == "user":
                    attachments = pending_send["attachments"]
                    if attachments:
                        user_message["attachments"] = copy.deepcopy(attachments)
        try:
            ChatLog.save(self.state.settings, self.state.chat)
            self.get_attachment_store().cleanup_unreferenced(self.state.chat)
        except Exception as e:
            AppLogger.error(f"Failed to save chat log: {e}")
        if pending_send is not None and pending_send["clear_prompt_on_success"]:
            self.window.js.completeSentPrompt()
        self.window.js.endResponse(content)

    # チャット例外イベントハンドラ（Chat）
    def on_chat_error(self, e: Exception, cause: str, info: str=""):
        pending_send = self._pending_send
        self._pending_send = None
        if pending_send is not None:
            restore_messages = pending_send["restore_messages"]
            if restore_messages is not None:
                self.state.chat.messages = restore_messages
                self.set_chatmessages_to_ui(
                    self.state.chat.messages,
                    preserve_pending=True
                )
            else:
                user_index = pending_send["user_index"]
                self.state.chat.messages = self.state.chat.messages[:user_index]
                if pending_send["delete_attachments_on_error"]:
                    self.get_attachment_store().delete_attachments(
                        pending_send["attachments"]
                    )
                self.window.js.rollbackSendingMessage()
        location = get_location(self)
        error_type = get_exception_name(e)
        AppLogger.error(f"{cause} : {info}")
        AppLogger.error(f"  -> location : {location}")
        AppLogger.error(f"  -> exception : {error_type}")
        print(e)

        if cause == "Timeout":
            message = get_text_resource("ERROR_API_TIMEOUT")
            self.window.js.handleChatTimeoutException(message)
        else:
            if cause == "Authentication":
                message = get_text_resource("ERROR_API_AUTHENTICATION_FAILED")
            elif cause == "EndPointNotFound":
                message = get_text_resource("ERROR_API_ENDPOINT_INCORRECT")
            elif cause == "UnsafeContent":
                message = get_text_resource("ERROR_CONVERSATION_CONTENT_INAPPROPRIATE")
            elif cause == "RateLimit":
                message = get_text_resource("ERROR_RATE_LIMIT_REACHED")
            elif cause == "APIError":
                message = get_text_resource("ERROR_API_ERROR_OCCURRED") + f"\n{info}"
            else:
                message = get_text_resource("ERROR_UNKNOWN_OCCURRED") + f"（{error_type}）"
            self.window.js.handleChatException(message)
