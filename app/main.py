# ZundaGPT2 Lite
#
# メイン
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import base64
import json
import os
import platform
import re
import subprocess
import sys

import langdetect
import webview

from app_config import AppConfig
from app_settings import Settings
from chat import ChatFactory, Chat
from chat_log import ChatLog
from multi_lang import set_current_language, get_text_resource

if getattr(sys, "frozen", False):
    import pyi_splash # type: ignore

APP_NAME = "ZundaGPT2 Lite"
APP_VERSION = "1.15.1"
COPYRIGHT = "Copyright 2024-2025 led-mirage"

# アプリケーションクラス
class Application:
    # コンストラクタ
    def __init__(self):
        self.app_config = None
        self.chat = None
        self.settings = None
        self.last_send_message = None
        self.initial_message_index = -1
        self.initial_highlight_text = ""
        self.cross_search_text = ""
        self.cross_search_results = []
        self._window = None # 先頭にアンダーバーをつけないと pywebview 5.0.x ではエラーになる
    
    # 開始する
    def start(self):
        self.app_config = AppConfig()
        self.app_config.load()
        width = self.app_config.system["window_width"]
        height = self.app_config.system["window_height"]

        window_title = f"{APP_NAME}  ver {APP_VERSION}"
        self._window = webview.create_window(window_title, url="html/index.html", width=width, height=height, js_api=self, text_select=True)
        webview.start()
        #webview.start(debug=True) # 開発者ツールを表示する場合

    # ページロードイベントハンドラ（UI）
    def page_loaded(self):
        lang = self.app_config.system["language"]
        set_current_language(lang)
        self._window.evaluate_js(f"initUIComponents('{self.escape_js_string(lang)}')")

        if self.chat == None:
            self.new_chat()
        else:
            self.set_chatinfo_to_ui()
            self.set_chatmessages_to_ui(self.chat.messages)
            self.set_window_title()
            if self.initial_message_index >= 0:
                self._window.evaluate_js(f"moveToMessageAt({self.initial_message_index}, '{self.escape_js_string(self.initial_highlight_text)}')")
                self.initial_message_index = -1
                self.initial_highlight_text = ""

    # 新しいチャットを開始する
    def new_chat(self):
        self.settings = Settings()
        self.settings.load()
        
        ChatLog.LOG_FOLDER = self.app_config.system["log_folder"]

        self.chat = ChatFactory.create(
            self.settings.chat["api"],
            self.settings.chat["model"],
            self.settings.chat["instruction"],
            self.settings.chat["bad_response"],
            self.settings.chat["history_size"],
            self.app_config.system["chat_api_timeout"],
            self.settings.chat["api_key_envvar"],
            self.settings.chat["api_endpoint_envvar"],
            self.app_config.gemini,
            self.settings.claude_options
        )

        self.set_chatinfo_to_ui()
        self.set_window_title()

    # ウィンドウのタイトルを設定する
    def set_window_title(self):
        logfile = ChatLog.get_logfile_name(self.chat)
        window_title = f"{APP_NAME}  ver {APP_VERSION} - {logfile}"
        self._window.set_title(window_title)

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
        display_name = self.settings.settings.get("display_name", "")
        user_name = self.settings.user["name"]
        user_color = self.settings.user["name_color"]
        user_icon = self.get_image_base64(self.settings.user["icon"])
        assistant_name = self.settings.assistant["name"]
        assistant_color = self.settings.assistant["name_color"]
        assistant_icon = self.get_image_base64(self.settings.assistant["icon"])
        welcome_title = self.settings.settings.get("welcome_title", "")
        welcome_message = self.settings.settings.get("welcome_message", "")
        ai_agent_available = "true" if self.chat.is_ai_agent_available() else "false"
        ai_agent_creation_error = self.chat.client_creation_error

        self._window.evaluate_js(
            f"setChatInfo("
            f"'{self.escape_js_string(display_name)}', "
            f"'{self.escape_js_string(user_name)}', "
            f"'{self.escape_js_string(user_color)}', "
            f"'{self.escape_js_string(user_icon)}', "
            f"'{self.escape_js_string(assistant_name)}', "
            f"'{self.escape_js_string(assistant_color)}', "
            f"'{self.escape_js_string(assistant_icon)}', "
            f"'{self.escape_js_string(welcome_title)}', "
            f"'{self.escape_js_string(welcome_message)}', "
            f"{ai_agent_available}, "
            f"'{self.escape_js_string(ai_agent_creation_error)}'"
            f")"
        )

    # ひとつ前のチャットを表示して続ける
    def prev_chat(self):
        logfile = ChatLog.get_prev_logfile(self.chat)
        if logfile is None:
            return

        loaded_settings, loaded_chat = ChatLog.load(logfile)
        if loaded_settings is None:
            return
        
        self.change_current_chat(loaded_settings, loaded_chat)

    # ひとつ後のチャットを表示して続ける
    def next_chat(self):
        logfile = ChatLog.get_next_logfile(self.chat)
        if logfile is None:
            return

        loaded_settings, loaded_chat = ChatLog.load(logfile)
        if loaded_settings is None:
            return
        
        self.change_current_chat(loaded_settings, loaded_chat)

    # カレントチャットを変更する
    def change_current_chat(self, loaded_settings: Settings, loaded_chat: Chat):
        self.settings = loaded_settings
        self.chat = loaded_chat
        self.set_chatinfo_to_ui()
        self.set_chatmessages_to_ui(loaded_chat.messages)
        self.set_window_title()

    # チャットの内容をUIに送信する
    def set_chatmessages_to_ui(self, messages: list[dict]):
        self._window.evaluate_js(f"setChatMessages({messages})")

    # コピーライト取得
    def get_copyright(self):
        return COPYRIGHT

    # カレントチャット削除イベントハンドラ（UI）
    def delete_current_chat(self):
        if not ChatLog.exists_log_file(self.chat):
            return
          
        next_logfile = ChatLog.get_prev_logfile(self.chat)
        if next_logfile is None:
            next_logfile = ChatLog.get_next_logfile(self.chat)
        
        ChatLog.delete_log_file(self.chat)

        if next_logfile is not None:
            loaded_settings, loaded_chat = ChatLog.load(next_logfile)
            if loaded_settings is None:
                return

            self.change_current_chat(loaded_settings, loaded_chat)
        else:
            self._window.evaluate_js(f"newChat()")

    # 設定画面遷移イベントハンドラ（UI）
    def move_to_settings(self):
        self._window.load_url("html/settings.html")

    # 設定画面ファイル一覧要求イベントハンドラ（UI）
    def get_settings_files(self):
        settings_files = Settings.get_settings_files()

        current_settings_file = self.app_config.system["settings_file"]

        view_model = []
        for filename in settings_files:
            settings = Settings(filename)
            settings.load()
            current = filename == current_settings_file
            diaplayName = settings.settings["display_name"]
            description = settings.settings["description"]
            group = settings.settings["group"]
            view_model.append({
                "current": current,
                "filename": filename,
                "displayName": diaplayName,
                "description": description,
                "group": group,
                "userName": settings.user["name"],
                "assistantName": settings.assistant["name"],
                "api": settings.chat["api"],
                "model": settings.chat["model"]
            })
        return view_model

    # 設定画面編集イベントハンドラ（UI）
    def edit_settings(self, settings_file):
        path = Settings(settings_file).get_path()
        self.open_file(path)

    # ファイルを開く
    def open_file(self, path):
        system = platform.system().lower()
        if system == "windows":
            os.startfile(path)
        elif system == "darwin":
            subprocess.Popen(["open", path])
        elif system == "linux":
            subprocess.Popen(["xdg-open", path])
        else:
            raise OSError(f'Unsupported OS: {platform.system()}')
            
    # 設定画面確定イベントハンドラ（UI）
    def submit_settings(self, settings_file):
        self._window.load_url("html/index.html")
        self.app_config.system["settings_file"] = settings_file
        self.app_config.save()
        self.chat = None

    # 設定画面キャンセルイベントハンドラ（UI）
    def cancel_settings(self):
        self._window.load_url("html/index.html")

    # ファイル横断検索画面遷移イベントハンドラ（UI）
    def move_to_cross_file_search(self):
        self._window.load_url("html/cross_file_search.html")

    # ファイル横断検索画面クローズイベントハンドラ（UI）
    def close_cross_file_search(self):
        self._window.load_url("html/index.html")

    # ファイル横断検索結果を取得する（UI）
    def get_cross_search_results(self):
        data = {
            "search_text": self.cross_search_text,
            "results": self.cross_search_results,
        }
        return json.dumps(data)

    # ファイル横断検索の実行
    def search_across_files(self, search_text):
        self.cross_search_text = search_text
        self.cross_search_results = []
        logfiles = ChatLog.get_logfiles()
        logfiles.reverse()
        total_count = len(logfiles)
        for index, logfile in enumerate(logfiles):
            self._window.evaluate_js(f"updateProgress({index}, {total_count})")
            results = ChatLog.search_text_in_file(logfile, search_text)
            for result in results:
                message_index = result["message_index"]
                message_content = result["message_content"]
                match_context = self.extract_match_context(message_content, search_text)
                self.cross_search_results.append((logfile, message_index, match_context))
                self._window.evaluate_js(f"appendSearchResult('{self.escape_js_string(search_text)}', '{self.escape_js_string(logfile)}', {message_index}, '{self.escape_js_string(match_context)}')")
        self._window.evaluate_js(f"updateProgress({total_count}, {total_count})")

    # 見つかったテキストの周囲の文字列を切り取り、改行を空白に置き換えて返す
    def extract_match_context(self, content, search_text, before_length=20, after_length=35):
        start_index = content.lower().find(search_text.lower())
        if start_index == -1:
            return ""
        
        start = max(0, start_index - before_length)
        end = min(len(content), start_index + len(search_text) + after_length)

        match_text = content[start:end].replace('\\n', ' ')

        if start > 0:
            match_text = "..." + match_text
        if end < len(content):
            match_text = match_text + "..."

        return match_text

    # カレントチャット変更イベントハンドラ（UI）
    def move_to_chat_at(self, logfile, messageIndex, searchText):
        loaded_settings, loaded_chat = ChatLog.load(logfile)
        if loaded_settings:
            self.settings = loaded_settings
            self.chat = loaded_chat
            self.initial_message_index = messageIndex
            self.initial_highlight_text = searchText
            self._window.load_url("html/index.html")
            
    # メッセージ送信イベントハンドラ（UI）
    def send_message_to_chatgpt(self, text):
        self._window.evaluate_js(f"startResponse()")
        self.last_send_message = text
        self.chat.send_message(
            text,
            self.on_recieve_chunk,
            self.on_recieve_sentence,
            self.on_end_response,
            self.on_chat_error)

    # メッセージ再送信イベントハンドラ（UI）
    def retry_send_message_to_chatgpt(self):
        self.chat.send_message(
            self.last_send_message,
            self.on_recieve_chunk,
            self.on_recieve_sentence,
            self.on_end_response,
            self.on_chat_error)

    # メッセージ送信中止イベントハンドラ（UI）
    def stop_send_message_to_chatgpt(self):
        self.chat.stop_send_message()

    # メッセージ削除イベントハンドラ（UI）
    def trancate_messages(self, index):
        self.chat.truncate_messages(index)
        ChatLog.save(self.settings, self.chat)

    # 別の回答を取得するイベントハンドラ（UI）
    def ask_another_reply_to_chatgpt(self, index):
        text = self.chat.messages[index - 1]["content"]
        self.chat.truncate_messages(index - 1)
        ChatLog.save(self.settings, self.chat)
        self.send_message_to_chatgpt(text)

    # チャットメッセージのテキストを取得する（UI）
    def get_message_text(self, index):
        text = self.chat.messages[index]["content"] + "\n"
        return text

    # チャットのすべてのメッセージを取得する（UI）
    def get_all_message_text(self, add_header=True):
        text = ""

        if add_header:
            text += "---\n"
            text += f"{self.settings.settings["display_name"]}\n"
            text += f"チャット開始日時: {self.chat.chat_start_time.strftime("%Y-%m-%d %H:%M:%S")}\n"
            text += f"チャット更新日時: {self.chat.chat_update_time.strftime("%Y-%m-%d %H:%M:%S")}\n"
            text += f"ログファイル: {ChatLog.get_logfile_name(self.chat)}\n"
            text += f"API: {self.settings.chat["api"]}\n"
            text += f"モデル: {self.settings.chat["model"]}\n"
            text += "---\n"
            text += "\n"

        for message in self.chat.messages:
            role = message["role"]
            if role == "user":
                name = self.settings.user["name"]
            elif role == "assistant":
                name = self.settings.assistant["name"]
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
            summary = self.chat.send_onetime_message(query)

            # 回答全体がコードブロックで囲まれていたら、それを外す
            pattern = r'```[a-zA-Z]*\n(.*?)\n```'
            match = re.search(pattern, summary, re.DOTALL)
            if match:
                summary = match.group(1)

            return summary
        except Exception as e:
            print(e)
            return ""

    # チャンク受信イベントハンドラ（Chat）
    def on_recieve_chunk(self, chunk):
        self._window.evaluate_js(f"addChunk('{self.escape_js_string(chunk)}')")

    # センテンス読み上げイベントハンドラ（Chat）
    def on_recieve_sentence(self, sentence):
        self._window.evaluate_js(f"parsedSentence('{self.escape_js_string(sentence)}')")
    
    # レスポンス受信完了イベントハンドラ（Chat）
    def on_end_response(self, content):
        ChatLog.save(self.settings, self.chat)
        self._window.evaluate_js(f"endResponse('{self.escape_js_string(content)}')")

    # チャット例外イベントハンドラ（Chat）
    def on_chat_error(self, e: Exception, cause: str, info: str=""):
        module_name = type(e).__module__
        class_name = type(e).__name__
        print(f"{module_name}.{class_name}")
        print(e)

        if cause == "Timeout":
            message = get_text_resource("ERROR_API_TIMEOUT")
            self._window.evaluate_js(f"handleChatTimeoutException('{self.escape_js_string(message)}')")
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
                message = get_text_resource("ERROR_UNKNOWN_OCCURRED") + f"（{class_name}）"
            self._window.evaluate_js(f"handleChatException('{self.escape_js_string(message)}')")

    # 文字をエスケープする
    def escape_js_string(self, s):
        return (
            s.replace('\\', '\\\\')  # バックスラッシュを最初にエスケープ
            .replace('\n', '\\n')    # 改行
            .replace('\r', '\\r')    # キャリッジリターン
            .replace('\t', '\\t')    # タブ
            .replace('"', '\\"')     # ダブルクォーテーション
            .replace('\'', '\\\'')   # シングルクォート
        )

if __name__ == '__main__':
    if getattr(sys, "frozen", False):
        pyi_splash.close()

    app = Application()
    app.start()
