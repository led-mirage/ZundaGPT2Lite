# ZundaGPT2 Lite
#
# アプリケーション設定クラス
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import copy
import json
import os
import threading

class AppConfig:
    FILE_VER = 5
    FILE_CONFIG = "appConfig.json"

    def __init__(self, config_file_path=FILE_CONFIG):
        self._config_file_path = config_file_path
        self._lock = threading.Lock()
        self._init_member()

    def _init_member(self):
        self.system = {
            "log_folder": "log",
            "settings_file": "settings.json",
            "window_width": 600,
            "window_height": 800,
            "chat_api_timeout": 30,
            "language": "ja",
            "font_family": "Söhne, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, sans-serif, Helvetica Neue, Arial, Apple Color Emoji, Segoe UI Emoji, Segoe UI Symbol, Noto Color Emoji",
            "font_size": 16,
        }
        self.gemini = {
            "safty_filter_harassment": "BLOCK_MEDIUM_AND_ABOVE",
            "safty_filter_hate_speech": "BLOCK_MEDIUM_AND_ABOVE",
            "safty_filter_sexually_explicit": "BLOCK_MEDIUM_AND_ABOVE",
            "safty_filter_dangerous_content": "BLOCK_MEDIUM_AND_ABOVE",
        }

    # deepcopy
    def __deepcopy__(self, memo):
        new_copy = self.__class__(None)
        memo[id(self)] = new_copy
        new_copy._config_file_path = self._config_file_path
        new_copy.system = copy.deepcopy(self.system, memo)
        new_copy.gemini = copy.deepcopy(self.gemini, memo)
        return new_copy

    # 設定ファイルを保存する
    def save(self):
        with self._lock:
            self._save_nolock()

    def _save_nolock(self):
        with open(self._config_file_path, "w", encoding="utf-8") as file:
            config = {}
            config["file_ver"] = AppConfig.FILE_VER
            config["system"] = self.system
            config["gemini"] = self.gemini

            json.dump(config, file, ensure_ascii=False, indent=4)

    # 設定ファイルを読み込む
    def load(self):
        if not os.path.exists(self._config_file_path):
            self._init_member()
            self._save_nolock()
            return

        with self._lock:
            with open(self._config_file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                file_ver = data.get("file_ver", 0)
                self.update_dict(self.system, data.get("system", self.system))
                self.update_dict(self.gemini, data.get("gemini", self.gemini))

        if file_ver < AppConfig.FILE_VER:
            self._save_nolock()

        return data

    # targetにあるキーのみをsrcからコピーする
    def update_dict(self, target: dict, src: dict):
        for key in target.keys():
            if key in src:
                target[key] = src[key]
