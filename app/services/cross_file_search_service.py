# ZundaGPT2 / ZundaGPT2 Lite
#
# ファイル横断検索画面のサービス
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import json

from app_state import AppState
from app_window import AppWindow
from chat_log import ChatLog


class CrossFileSearchService:
    def __init__(self, state: AppState, window: AppWindow):
        self.state = state
        self.window = window

    # ファイル横断検索画面遷移イベントハンドラ（UI）
    def move_to_cross_file_search(self):
        self.window.open_cross_file_search_view()

    # ファイル横断検索結果を取得する（UI）
    def get_cross_search_results(self):
        data = {
            "search_text": self.state.cross_search_text,
            "results": self.state.cross_search_results,
        }
        return json.dumps(data)

    # ファイル横断検索の実行
    def search_across_files(self, search_text):
        self.state.cross_search_text = search_text
        self.state.cross_search_results = []
        logfiles = ChatLog.get_logfiles()
        logfiles.reverse()
        total_count = len(logfiles)
        for index, logfile in enumerate(logfiles):
            self.window.js.updateProgress(index, total_count)
            results = ChatLog.search_text_in_file(logfile, search_text)
            for result in results:
                message_index = result["message_index"]
                message_content = result["message_content"]
                match_context = self.extract_match_context(message_content, search_text)
                self.state.cross_search_results.append((logfile, message_index, match_context))
                self.window.js.appendSearchResult(search_text, logfile, message_index, match_context)
        self.window.js.updateProgress(total_count, total_count)

    # 見つかったテキストの周囲の文字列を切り取り、改行を空白に置き換えて返す
    def extract_match_context(self, content: str, search_text: str, before_length: int=20, after_length: int=35):
        start_index = content.lower().find(search_text.lower())
        if start_index == -1:
            return ""
        
        start = max(0, start_index - before_length)
        end = min(len(content), start_index + len(search_text) + after_length)

        match_text = content[start:end].replace('\\n', ' ')

        if start > 0:
            match_text = "..." + match_text
        if end < len(content):
            match_text = match_text + "..."

        return match_text

    # カレントチャット変更イベントハンドラ（UI）
    def move_to_chat_at(self, logfile, messageIndex, searchText):
        loaded_settings, loaded_chat = ChatLog.load(logfile)
        if loaded_settings:
            self.state.settings = loaded_settings
            self.state.chat = loaded_chat
            self.state.initial_message_index = messageIndex
            self.state.initial_highlight_text = searchText
            self.window.open_index_view()

    # ファイル横断検索画面クローズイベントハンドラ（UI）
    def close_cross_file_search(self):
        self.window.open_index_view()
