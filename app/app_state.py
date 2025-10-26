# ZundaGPT2 Lite
#
# アプリケーションステート
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from chat import Chat
    from config.app_settings import Settings

class AppState:
    def __init__(self):
        self.settings: "Settings" = None
        self.chat: "Chat" = None
        self.last_send_message: str = None
        self.initial_message_index: int = -1
        self.initial_highlight_text: str = ""
        self.cross_search_text: str = ""
        self.cross_search_results: list = []
