# ZundaGPT2 / ZundaGPT2 Lite
#
# 設定画面のサービス
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import platform
import os
import subprocess

from config.app_config import AppConfig
from config.app_settings import Settings
from app_state import AppState
from app_window import AppWindow


class SettingsService:
    def __init__(self, app_config: AppConfig, state: AppState, window: AppWindow):
        self.app_config = app_config
        self.state = state
        self.window = window

    # 設定画面遷移イベントハンドラ（UI）
    def move_to_settings(self):
        self.window.open_settings_view()

    # 設定画面ファイル一覧要求イベントハンドラ（UI）
    def get_settings_files(self):
        settings_files = Settings.get_settings_files()

        current_settings_file = self.app_config.system["settings_file"]

        view_model = []
        for filename in settings_files:
            settings = Settings(filename)
            settings.load()
            current = filename == current_settings_file
            displayName = settings.settings["display_name"]
            description = settings.settings["description"]
            group = settings.settings["group"]
            view_model.append({
                "current": current,
                "filename": filename,
                "displayName": displayName,
                "description": description,
                "group": group,
                "userName": settings.user["name"],
                "assistantName": settings.assistant["name"],
                "api": settings.chat["api"],
                "model": settings.chat["model"]
            })
        return view_model

    # 設定画面・設定編集イベントハンドラ（UI）
    def edit_settings(self, settings_file):
        path = Settings(settings_file).get_path()
        self.open_file(path)

    # 設定画面・設定削除イベントハンドラ（UI）
    def delete_settings(self, settings_file):
        path = Settings(settings_file).get_path()
        if os.path.exists(path):
            os.remove(path)

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
        self.window.open_index_view()
        self.app_config.system["settings_file"] = settings_file
        self.app_config.save()
        self.state.chat = None

    # 設定画面キャンセルイベントハンドラ（UI）
    def cancel_settings(self):
        self.window.open_index_view()
