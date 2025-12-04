# ZundaGPT2 Lite
#
# メイン画面のサービス
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import base64
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


log_settings = get_log_settings()
AppLogger.init_logger(log_settings["log_folder"], log_settings["log_level"])


class IndexService:
    def __init__(self, app_config: AppConfig, state: AppState, window: AppWindow):
        self.app_config = app_config
        self.state = state
        self.window = window
        self.last_sent_images = None

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
        self.set_chatinfo_to_ui()
        self.set_chatmessages_to_ui(loaded_chat.messages)
        self.set_window_title()

    # チャットの内容をUIに送信する
    def set_chatmessages_to_ui(self, messages: list[dict]):
        self.window.js.setChatMessages(messages)

    # カレントチャット削除イベントハンドラ（UI）
    def delete_current_chat(self):
        if not ChatLog.exists_log_file(self.state.chat):
            return
          
        next_logfile = ChatLog.get_prev_logfile(self.state.chat)
        if next_logfile is None:
            next_logfile = ChatLog.get_next_logfile(self.state.chat)
        
        ChatLog.delete_log_file(self.state.chat)

        if next_logfile is not None:
            loaded_settings, loaded_chat = ChatLog.load(next_logfile)
            if loaded_settings is None:
                return

            self.change_current_chat(loaded_settings, loaded_chat)
        else:
            self.window.js.newChat()

    # メッセージ送信イベントハンドラ（UI）
    def send_message_to_chatgpt(self, text, images):
        self.window.js.startResponse()
        self.state.last_send_message = text
        self.last_sent_images = images
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

    # メッセージ再送信イベントハンドラ（UI）
    def retry_send_message_to_chatgpt(self):
        self.state.chat.messages.pop()  # 最後のメッセージを削除（削除しないと重複する）
        self.state.chat.send_message(
            self.state.last_send_message,
            self.last_sent_images,
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

    # メッセージ送信中止イベントハンドラ（UI）
    def stop_send_message_to_chatgpt(self):
        self.state.chat.stop_send_message()

    # メッセージ削除イベントハンドラ（UI）
    def truncate_messages(self, index):
        self.state.chat.truncate_messages(index)
        ChatLog.save(self.state.settings, self.state.chat)

    # 別の回答を取得するイベントハンドラ（UI）
    def ask_another_reply_to_chatgpt(self, index):
        text = self.state.chat.messages[index - 1]["content"]
        self.state.chat.truncate_messages(index - 1)
        ChatLog.save(self.state.settings, self.state.chat)
        self.send_message_to_chatgpt(text, self.last_sent_images)

    # チャットメッセージのテキストを取得する（UI）
    def get_message_text(self, index):
        text = self.state.chat.messages[index]["content"] + "\n"
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
        ChatLog.save(self.state.settings, self.state.chat)
        self.window.js.endResponse(content)

    # チャット例外イベントハンドラ（Chat）
    def on_chat_error(self, e: Exception, cause: str, info: str=""):
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
