# ZundaGPT2 Lite
#
# メイン
#
# Copyright (c) 2024 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import json
import os
from datetime import datetime

from app_config import AppConfig
from app_settings import Settings
from chat import Chat
from chat import ChatFactory

# チャットログクラス
class ChatLog:
    FILE_VER = 3
    LOG_FOLDER = "log"

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
        data["messages"] = chat.messages

        filename = ChatLog.get_logfile_name(chat)
        path = os.path.join(log_folder, filename)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    # ログファイルの名前を取得する
    @staticmethod
    def get_logfile_name(chat: Chat):
        return chat.chat_start_time.strftime("chatlog-%Y%m%d-%H%M%S.json")

    # ログファイルを読み込んで、SettingsオブジェクトとChatオブジェクトを返す
    @staticmethod
    def load(logfile: str):
        path = os.path.join(ChatLog.LOG_FOLDER, logfile)
        if not os.path.exists(path):
            return (None, None)

        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

            if data["file_ver"] == 1:
                return (None, None)
            
            if data["file_ver"] == 2:
                data["settings"] = {
                    "display_name": "ZundaGPT",
                    "description": ""
                }

            app_config = AppConfig()
            app_config.load()

            settings = Settings()
            settings.load()
            settings.settings = data["settings"]
            settings.user = data["user"]
            settings.assistant = data["assistant"]
            settings.chat = data["chat"]

            chat = ChatFactory.create(
                settings.chat["api"],
                settings.chat["model"],
                settings.chat["instruction"],
                settings.chat["bad_response"],
                settings.chat["history_size"],
                app_config.system["chat_api_timeout"]
            )
            chat.messages = data["messages"]
            chat.chat_start_time = datetime.fromisoformat(data["chat_start_time"])
            chat.chat_update_time = datetime.fromisoformat(data["chat_update_time"])

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
        files = os.listdir(ChatLog.LOG_FOLDER)
        files_sorted = sorted(files, key=lambda x: os.path.getmtime(os.path.join(ChatLog.LOG_FOLDER, x)), reverse=False)
        return files_sorted
    
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
