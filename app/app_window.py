# ZundaGPT2 / ZundaGPT2 Lite
#
# webview.Window ラッパー
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import sys
import threading

import webview

from config.app_config import AppConfig
from utility.utils import get_screen_size

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from api.js_caller import JSCaller


class AppWindow:
    def __init__(self, app_config: AppConfig):
        self.app_config = app_config
        self.js: "JSCaller" = None
        self._resize_timer = None
        self._is_minimized = False
        self._is_maximized = False
        self._is_fullscreen = False

    def set_raw_window(self, window: webview.Window):
        self._window = window
        self.setup_window_events()

    def set_js_caller(self, js_caller: "JSCaller"):
        self.js = js_caller

    def set_window_title(self, title: str):
        self._window.set_title(title)

    def is_fullscreen(self):
        return self._is_fullscreen

    def toggle_fullscreen(self):
        self._is_fullscreen = not self._is_fullscreen
        self._window.toggle_fullscreen()
        return self._is_fullscreen

    def evaluate_js(self, js: str):
        return self._window.evaluate_js(js)

    def open_index_view(self):
        self._window.load_url("html/index.html")

    def open_settings_view(self):
        self._window.load_url("html/settings.html")

    def open_cross_file_search_view(self):
        self._window.load_url("html/cross-file-search.html")
    
    def setup_window_events(self):
        self._window.events.minimized += self.on_minimized
        self._window.events.maximized += self.on_maximized
        self._window.events.restored += self.on_restored
        self._window.events.resized += self.on_resized
        self._window.events.shown += self.on_shown

    def get_window_handle_for_windows(self):
        if sys.platform == "win32":
            return self._window.native.Handle
        else:
            return self._window.native

    def on_shown(self):
        if sys.platform == "win32":
            # Windowsの場合、画面スケーリングが100%以外だと、
            # webviewの初期表示が拡大率に影響され物理ピクセル数にならない。
            # そのため、表示後にウィンドウサイズを調整する。
            #
            # また、LinuxではPyWebViewのresizeメソッドを呼ぶと、
            # それ以降ウィンドウサイズの変更ができなくなるため（たぶんPyWebViewのバグ）
            # main.pyの中でサイズ調整を行っている。
            # Linuxには画面スケーリングの概念がないため、これで問題ない。
            width = self.app_config.system["window_width"]
            height = self.app_config.system["window_height"]
            screen_width, screen_height = get_screen_size(self.get_window_handle_for_windows())
            adj_width = min(width, screen_width)
            adj_height = min(height, screen_height)
            self._window.resize(adj_width, adj_height)

    def on_minimized(self):
        self._is_minimized = True

    def on_maximized(self):
        self._is_maximized = True

    def on_restored(self):
        self._is_minimized = self._is_maximized = False

    def on_resized(self, width: int, height: int):
        if self._is_minimized or self._is_maximized or self._is_fullscreen:
            return

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
