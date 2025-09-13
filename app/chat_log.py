# ZundaGPT2 / ZundaGPT2 Lite
#
# チャットログクラス
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import glob
import json
import os
from datetime import datetime

from config.app_config import AppConfig
from config.app_settings import Settings
from chat import Chat
from chat import ChatFactory

# チャットログクラス
class ChatLog:
    FILE_VER = 9
    LOG_FOLDER = "log"

    cache = {}

    # ログをファイルに保存する
    @staticmethod
    def save(settings: Settings, chat: Chat):
        log_folder = ChatLog.LOG_FOLDER
        if log_folder == "":
            return

        if not os.path.exists(log_folder):
            os.mkdir(log_folder)

        data = {}
        data["file_ver"] = ChatLog.FILE_VER
        data["logid"] = chat.chat_start_time.strftime("%Y%m%d%H%M%S")
        data["chat_start_time"] = chat.chat_start_time.isoformat()
        data["chat_update_time"] = chat.chat_update_time.isoformat()
        data["settings"] = settings.settings
        data["user"] = settings.user
        data["assistant"] = settings.assistant
        data["chat"] = settings.chat
        data["custom_style"] = settings.custom_style
        data["claude_options"] = settings.claude_options
        data["messages"] = chat.messages

        filename = ChatLog.get_logfile_name(chat)
        path = os.path.join(log_folder, filename)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        ChatLog.cache[filename] = (settings, chat)

    # ログファイルの名前を取得する
    @staticmethod
    def get_logfile_name(chat: Chat):
        return chat.chat_start_time.strftime("chatlog-%Y%m%d-%H%M%S.json")

    # ログファイルを読み込んで、SettingsオブジェクトとChatオブジェクトを返す
    @staticmethod
    def load(logfile: str):
        if logfile in ChatLog.cache:
            return ChatLog.cache[logfile]

        path = os.path.join(ChatLog.LOG_FOLDER, logfile)
        if not os.path.exists(path):
            return (None, None)

        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

            if data["file_ver"] == 1:
                return (None, None)
            
            if data["file_ver"] <= 2:
                data["settings"] = {
                    "display_name": "ZundaGPT",
                    "description": ""
                }

            if data["file_ver"] <= 3:
                data["user"]["icon"] = ""
                data["assistant"]["icon"] = ""

            if data["file_ver"] <= 4:
                data["claude_options"] = {
                    "max_tokens": 4096,
                    "extended_thinking": False,
                    "budget_tokens": 2048,
                }

            if data["file_ver"] <= 5:
                data["chat"]["api_key_envvar"] = ""
                data["chat"]["api_endpoint_envvar"] = ""

            if data["file_ver"] <= 6:
                # バグ修正 v1.21.0
                if "history_char_limit" not in data["chat"]:
                    data["chat"]["history_char_limit"] = 0

            if data["file_ver"] <= 7:
                if "api_base_url" not in data["chat"]:
                    data["chat"]["api_base_url"] = ""

            if data["file_ver"] <= 8:
                data["custom_style"] = {
                    "enable": False,
                    "background_image": "",
                    "background_image_opacity": "0.8",
                    "body_bgcolor": "",
                    "header_color": "",
                    "welcome_title_color": "",
                    "welcome_message_color": "",
                    "speaker_name_text_shadow": "",
                    "message_text_bgcolor": "",
                    "message_text_color": "",
                    "message_text_shadow": "",
                    "message_text_border_radius": "",
                    "message_text_em_color": "",
                }

            app_config = AppConfig()
            app_config.load()

            settings = Settings()
            settings.load()
            settings.settings = data["settings"]
            settings.user = data["user"]
            settings.assistant = data["assistant"]
            settings.chat = data["chat"]
            settings.custom_style = data["custom_style"]
            settings.claude_options = data["claude_options"]

            chat = ChatFactory.create(
                settings.chat["api"],
                settings.chat["model"],
                settings.chat["instruction"],
                settings.chat["bad_response"],
                settings.chat["history_size"],
                settings.chat["history_char_limit"],
                app_config.system["chat_api_timeout"],
                settings.chat["api_key_envvar"],
                settings.chat["api_endpoint_envvar"],
                settings.chat["api_base_url"],
                app_config.gemini,
                settings.claude_options
            )
            chat.messages = data["messages"]
            chat.chat_start_time = datetime.fromisoformat(data["chat_start_time"])
            chat.chat_update_time = datetime.fromisoformat(data["chat_update_time"])

            ChatLog.cache[logfile] = (settings, chat)

            return (settings, chat)

    # ひとつ前のチャットファイル名を取得する
    @staticmethod
    def get_prev_logfile(chat: Chat):
        logfiles = ChatLog.get_logfiles()
        logfile_name = ChatLog.get_logfile_name(chat)
        index = ChatLog.get_index(logfiles, logfile_name)
        if index > 0:
            return logfiles[index - 1]
        elif index == -1 and len(logfiles) > 0:
            return logfiles[len(logfiles) - 1]
        else:
            return None

    # ひとつ後のチャットファイル名を取得する
    @staticmethod
    def get_next_logfile(chat: Chat):
        logfiles = ChatLog.get_logfiles()
        logfile_name = ChatLog.get_logfile_name(chat)
        index = ChatLog.get_index(logfiles, logfile_name)
        if index == -1 or index == len(logfiles) - 1:
            return None
        else:
            return logfiles[index + 1]

    # ログファイルのインデックスを取得する
    @staticmethod
    def get_index(logfiles: list[str], logfile_name: str):
        if logfile_name in logfiles:
            return logfiles.index(logfile_name)
        else:
            return -1

    # ログファイルの一覧を取得する
    @staticmethod
    def get_logfiles() -> list[str]:
        pattern = os.path.join(ChatLog.LOG_FOLDER, "chatlog*.json")
        files = glob.glob(pattern)
        files_sorted = sorted(files, key=os.path.getmtime, reverse=False)
        filenames_only = [os.path.basename(f) for f in files_sorted]
        return filenames_only

    # ログファイルが存在するかどうかを調べる
    @staticmethod
    def exists_log_file(chat: Chat) -> bool:
        logfile = ChatLog.get_logfile_name(chat)
        path = os.path.join(ChatLog.LOG_FOLDER, logfile)
        return os.path.exists(path)
    
    # ログファイルを削除する
    @staticmethod
    def delete_log_file(chat: Chat):
        logfile = ChatLog.get_logfile_name(chat)
        path = os.path.join(ChatLog.LOG_FOLDER, logfile)
        os.remove(path)

        if logfile in ChatLog.cache:
            del ChatLog.cache[logfile]

    @staticmethod
    def search_text_in_file(logfile: str, search_text: str):
        results = []

        path = os.path.join(ChatLog.LOG_FOLDER, logfile)
        if not os.path.exists(path):
            return results

        search_text = search_text.lower()

        message_index = 0
        keyword = "\"content\":"
        with open(path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line.startswith(keyword):
                    content = line[len(keyword):].strip(" \"")
                    content_lower = content.lower()
                    if search_text in content_lower:
                        results.append({"message_index": message_index, "message_content": content})
                    message_index += 1 
                    
        return results
