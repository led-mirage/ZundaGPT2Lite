# ZundaGPT2 / ZundaGPT2 Lite
#
# アプリケーション共通のサービス
#
# Copyright (c) 2024-2026 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import pyperclip

from const import COPYRIGHT
from config.app_config import AppConfig
from app_window import AppWindow


class AppService:
    def __init__(self, app_config: AppConfig, window: AppWindow):
        self.app_config = app_config
        self.window = window

    # アプリケーション設定取得（UI）
    def get_app_config_js(self):
        return {
            "fontFamily": self.app_config.system["font_family"],
            "fontSize": self.app_config.system["font_size"],
            "language": self.app_config.system["language"],
            "copyright": f"Unlimited Code Works / {COPYRIGHT}",
            "theme": self.app_config.system["theme"],
            "displayClock": self.app_config.system["display_clock"],
        }

    # クリップボードにテキストをコピーする
    def copytext_to_clipboard(self, text):
        pyperclip.copy(text)
        return True

    def is_fullscreen(self):
        return self.window.is_fullscreen()

    # フルスクリーン切替
    def toggle_fullscreen(self):
        self.window.toggle_fullscreen()
        return self.is_fullscreen()
