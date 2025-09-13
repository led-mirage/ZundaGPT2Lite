# ZundaGPT2 Lite
#
# メイン
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import platform
import sys

import webview

from const import APP_NAME, APP_VERSION
from config.app_config import AppConfig
from app_state import AppState
from app_window import AppWindow
from api.api_router import ApiRouter
from api.js_caller import JSCaller
from services.app_service import AppService
from services.index_service import IndexService
from services.settings_service import SettingsService
from services.cross_file_search_service import CrossFileSearchService
from utility.utils import get_screen_size

if getattr(sys, "frozen", False):
    import pyi_splash # type: ignore


# アプリケーションクラス
class Application:
    # コンストラクタ
    def __init__(self):
        self.app_config = None
        self.state = AppState()
        self._window = None # 先頭にアンダーバーをつけないと pywebview 5.0.x ではエラーになる
    
    # 開始する
    def start(self):
        self.app_config = AppConfig()
        self.app_config.load()
        width, height = self.adjust_window_size(
            self.app_config.system["window_width"],
            self.app_config.system["window_height"]
        )

        window = AppWindow(self.app_config)
        js_caller = JSCaller(window)
        window.set_js_caller(js_caller)

        app_service = AppService(self.app_config)
        index_service = IndexService(self.app_config, self.state, window)
        settings_service = SettingsService(self.app_config, self.state, window)
        cross_file_search_service = CrossFileSearchService(self.state, window)
        api = ApiRouter(app_service, index_service, settings_service, cross_file_search_service)

        window_title = f"{APP_NAME}  ver {APP_VERSION}"
        self._window = webview.create_window(window_title, url="html/index.html", width=width, height=height, js_api=api, text_select=True)
        window.set_raw_window(self._window)

        gui = None
        os_name = platform.system()
        if os_name == "Linux":
            gui = "qt"

        webview.start(gui=gui)
        #webview.start(gui=gui, debug=True) # 開発者ツールを表示する場合

    def adjust_window_size(self, width: int, height: int):
        if sys.platform != "win32": # WindowsはAppWindowのon_shownで処理する
            screen_width, screen_height = get_screen_size()
            width = min(width, screen_width)
            height = min(height, screen_height)
            return width, height
        else:
            return width, height


if __name__ == '__main__':
    if getattr(sys, "frozen", False):
        pyi_splash.close()

    app = Application()
    app.start()
