# ZundaGPT2 / ZundaGPT2 Lite
#
# JSの関数を呼び出すクラス
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import sys
import json
import re
from pathlib import Path

from app_window import AppWindow
from utility.utils import escape_js_string, to_data_url


class JSCaller:
    def __init__(self, window: AppWindow):
        self.window = window

    # --------------------------------------------------------------------------
    # 共通
    # --------------------------------------------------------------------------

    def inject_custom_css(self):
        def get_custom_css_path():
            custom_css_path = Path.cwd()
            if getattr(sys, "frozen", False):
                base = Path(sys.executable).parent
                custom_css_path = base.joinpath("css", "custom.css")
            else:
                base = Path.cwd()
                custom_css_path = base.joinpath("app", "html", "css", "custom.css")
            return custom_css_path
        
        custom_css_path = get_custom_css_path()
        if custom_css_path.exists():
            css = custom_css_path.read_text(encoding="utf-8")
            css = self.replace_background_image(css, "--background-image")
            css = self.replace_background_image(css, "--dark-background-image")
            # JSONエンコードしてJS文字列に安全に埋め込む
            css_js = json.dumps(css)
            self.window.evaluate_js(f"applyCustomCSS({css_js});")

    def replace_background_image(self, css_text: str, var_name: str) -> str:
        # CSSから値を抜き出す
        image_path = self.extract_background_image(css_text, var_name)
        if not image_path:
            return css_text

        image_path = Path(image_path)
        if image_path.exists() and image_path.is_file():
            data_url = to_data_url(image_path, 1.5)
            # 元の値を data URL で置き換え
            pattern = rf'({re.escape(var_name)}\s*:\s*)([^;]+)(;)'
            return  re.sub(pattern, r'\1' + data_url + r'\3', css_text)
        else:
            # 存在しなかったら置き換えなしで返す
            return css_text

    def extract_background_image(self, css_text: str, var_name: str) -> str | None:
        pattern = rf'{re.escape(var_name)}\s*:\s*([^;]+);'
        m = re.search(pattern, css_text)
        if not m:
            return None
        raw = m.group(1).strip()
        if raw.lower().startswith("url(") and raw.endswith(")"):
            raw = raw[4:-1].strip().strip('"').strip("'")
        return raw

    # --------------------------------------------------------------------------
    # メイン画面
    # --------------------------------------------------------------------------

    def moveToMessageAt(self, message_index: int, highlight_text: str):
        self.window.evaluate_js(f"moveToMessageAt({message_index}, '{escape_js_string(highlight_text)}')")

    def setChatInfo(self, info):
        js_literal = json.dumps(info)
        self.window.evaluate_js(f"setChatInfo({js_literal})")

    def setChatMessages(self, messages: list[dict]):
        self.window.evaluate_js(f"setChatMessages({messages})")

    def newChat(self):
        self.window.evaluate_js(f"newChat()")

    def startResponse(self):
        self.window.evaluate_js(f"startResponse()")

    def addChunk(self, chunk: str):
        self.window.evaluate_js(f"addChunk('{escape_js_string(chunk)}')")

    def parsedSentence(self, sentence: str):
        self.window.evaluate_js(f"parsedSentence('{escape_js_string(sentence)}')")

    def parsedParagraph(self, paragraph: str):
        self.window.evaluate_js(f"parsedParagraph('{escape_js_string(paragraph)}')")

    def endResponse(self, content: str):
        self.window.evaluate_js(f"endResponse('{escape_js_string(content)}')")

    def handleChatTimeoutException(self, message: str):
        self.window.evaluate_js(f"handleChatTimeoutException('{escape_js_string(message)}')")

    def handleChatException(self, message: str):
        self.window.evaluate_js(f"handleChatException('{escape_js_string(message)}')")

    def addReplayMessage(self, sentence: str):
        self.window.evaluate_js(f"addReplayMessage('{escape_js_string(sentence)}')")

    def startReplayMessageBlock(self, role: str):
        self.window.evaluate_js(f"startReplayMessageBlock('{escape_js_string(role)}')")

    def endReplayMessageBlock(self, content: str):
        self.window.evaluate_js(f"endReplayMessageBlock('{escape_js_string(content)}')")

    def showProgressModal(self, message: str):
        self.window.evaluate_js(f"showProgressModal('{escape_js_string(message)}')")

    def hideProgressModal(self):
        self.window.evaluate_js("hideProgressModal()")

    # --------------------------------------------------------------------------
    # ファイル横断検索画面
    # --------------------------------------------------------------------------

    def updateProgress(self, index: int, total_count: int):
        self.window.evaluate_js(f"updateProgress({index}, {total_count})")

    def appendSearchResult(self, search_text: str, logfile: str, message_index: int, match_context:str):
        self.window.evaluate_js(f"appendSearchResult('{escape_js_string(search_text)}', '{escape_js_string(logfile)}', {message_index}, '{escape_js_string(match_context)}')")
