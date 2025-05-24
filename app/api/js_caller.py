# ZundaGPT2 Lite
#
# JSの関数を呼び出すクラス
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

from app_window import AppWindow
from utility.utils import escape_js_string


class JSCaller:
    def __init__(self, window: AppWindow):
        self.window = window

    # --------------------------------------------------------------------------
    # メイン画面
    # --------------------------------------------------------------------------

    def moveToMessageAt(self, message_index: int, highlight_text: str):
        self.window.evaluate_js(f"moveToMessageAt({message_index}, '{escape_js_string(highlight_text)}')")

    def setChatInfo(self, display_name, user_name, user_color, user_icon,
                    assistant_name, assistant_color, assistant_icon,
                    welcome_title, welcome_message, ai_agent_available, ai_agent_creation_error):
        self.window.evaluate_js(
            f"setChatInfo("
            f"'{display_name}', "
            f"'{user_name}', "
            f"'{user_color}', "
            f"'{user_icon}', "
            f"'{assistant_name}', "
            f"'{assistant_color}', "
            f"'{assistant_icon}', "
            f"'{welcome_title}', "
            f"'{welcome_message}', "
            f"{ai_agent_available}, "
            f"'{ai_agent_creation_error}'"
            f")"
        )

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

    # --------------------------------------------------------------------------
    # ファイル横断検索画面
    # --------------------------------------------------------------------------

    def updateProgress(self, index: int, total_count: int):
        self.window.evaluate_js(f"updateProgress({index}, {total_count})")

    def appendSearchResult(self, search_text: str, logfile: str, message_index: int, match_context:str):
        self.window.evaluate_js(f"appendSearchResult('{escape_js_string(search_text)}', '{escape_js_string(logfile)}', {message_index}, '{escape_js_string(match_context)}')")
