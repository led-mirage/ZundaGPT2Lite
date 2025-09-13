# ZundaGPT2 / ZundaGPT2 Lite
#
# アプリケーション共通のサービス
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import pyperclip

from const import COPYRIGHT
from config.app_config import AppConfig


class AppService:
    def __init__(self, app_config: AppConfig):
        self.app_config = app_config

    # アプリケーション設定取得（UI）
    def get_app_config_js(self):
        return {
            "fontFamily": self.app_config.system["font_family"],
            "fontSize": self.app_config.system["font_size"],
            "language": self.app_config.system["language"],
            "copyright": f"Unlimited Code Works / {COPYRIGHT}",
            "theme": self.app_config.system["theme"],
        }

    # クリップボードにテキストをコピーする
    def copytext_to_clipboard(self, text):
        pyperclip.copy(text)
        return True
