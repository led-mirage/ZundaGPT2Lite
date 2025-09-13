# ZundaGPT2 / ZundaGPT2 Lite
#
# webview.Window ラッパー
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import threading

import webview

from config.app_config import AppConfig

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from api.js_caller import JSCaller


class AppWindow:
    def __init__(self, app_config: AppConfig):
        self.app_config = app_config
        self.js: "JSCaller" = None
        self._resize_timer = None

    def set_raw_window(self, window: webview.Window):
        self._window = window
        self._window.events.resized += self.on_resized

    def set_js_caller(self, js_caller: "JSCaller"):
        self.js = js_caller

    def set_window_title(self, title: str):
        self._window.set_title(title)

    def evaluate_js(self, js: str):
        return self._window.evaluate_js(js)

    def open_index_view(self):
        self._window.load_url("html/index.html")

    def open_settings_view(self):
        self._window.load_url("html/settings.html")

    def open_cross_file_search_view(self):
        self._window.load_url("html/cross-file-search.html")
    
    def on_resized(self, width: int, height: int):
        # 既存タイマーをキャンセル
        if self._resize_timer and self._resize_timer.is_alive():
            self._resize_timer.cancel()
        
        # 一定時間後に保存
        self._resize_timer = threading.Timer(1.0, self._save_size, args=(width, height))
        self._resize_timer.start()
  
    def _save_size(self, width: int, height: int):
        self.app_config.system["window_width"] = width
        self.app_config.system["window_height"] = height
        self.app_config.save()
