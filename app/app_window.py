# ZundaGPT2 / ZundaGPT2 Lite
#
# webview.Window ラッパー
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import webview

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from api.js_caller import JSCaller


class AppWindow:
    def __init__(self):
        self.js: "JSCaller" = None

    def set_raw_window(self, window: webview.Window):
        self._window = window

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
