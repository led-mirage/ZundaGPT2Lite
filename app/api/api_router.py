# ZundaGPT2 Lite
#
# JSからの要求を受け付けルーティングするクラス
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

from services.app_service import AppService
from services.index_service import IndexService
from services.settings_service import SettingsService
from services.cross_file_search_service import CrossFileSearchService


class ApiRouter:
    def __init__(self, app_service: AppService, index_service: IndexService, settings_service: SettingsService, cross_file_search_service: CrossFileSearchService):
        self.app_service = app_service
        self.index_service = index_service
        self.settings_service = settings_service
        self.cross_file_search_service = cross_file_search_service

    # --------------------------------------------------------------------------
    # アプリケーション共通のサービス
    # --------------------------------------------------------------------------

    # アプリケーション設定取得（UI）
    def get_app_config_js(self):
        return self.app_service.get_app_config_js()
    
    # クリップボードにテキストをコピーする
    def copytext_to_clipboard(self, text):
        return self.app_service.copytext_to_clipboard(text)

    # フルスクリーン状態取得
    def is_fullscreen(self):
        return self.app_service.is_fullscreen()

    # フルスクリーン切替
    def toggle_fullscreen(self):
        return self.app_service.toggle_fullscreen()

    # --------------------------------------------------------------------------
    # メイン画面のサービス
    # --------------------------------------------------------------------------

    # ページロードイベントハンドラ（UI）
    def page_loaded(self):
        return self.index_service.page_loaded()

    # 新しいチャットを開始する
    def new_chat(self):
        return self.index_service.new_chat()

    # ひとつ前のチャットを表示して続ける
    def prev_chat(self):
        return self.index_service.prev_chat()

    # ひとつ後のチャットを表示して続ける
    def next_chat(self):
        return self.index_service.next_chat()

    # カレントチャット削除イベントハンドラ（UI）
    def delete_current_chat(self):
        return self.index_service.delete_current_chat()

    # メッセージ送信イベントハンドラ（UI）
    def send_message_to_chatgpt(self, text, images):
        return self.index_service.send_message_to_chatgpt(text, images)

    # メッセージ再送信イベントハンドラ（UI）
    def retry_send_message_to_chatgpt(self):
        return self.index_service.retry_send_message_to_chatgpt()

    # メッセージ送信中止イベントハンドラ（UI）
    def stop_send_message_to_chatgpt(self):
        return self.index_service.stop_send_message_to_chatgpt()

    # メッセージ削除イベントハンドラ（UI）
    def truncate_messages(self, index):
        return self.index_service.truncate_messages(index)

    # 別の回答を取得するイベントハンドラ（UI）
    def ask_another_reply_to_chatgpt(self, index):
        return self.index_service.ask_another_reply_to_chatgpt(index)

    # チャットメッセージのテキストを取得する（UI）
    def get_message_text(self, index):
        return self.index_service.get_message_text(index)

    # チャットのすべてのメッセージを取得する（UI）
    def get_all_message_text(self, add_header=True):
        return self.index_service.get_all_message_text(add_header)

    # チャットの内容を要約する
    def summarize_chat(self):
        return self.index_service.summarize_chat()

    # --------------------------------------------------------------------------
    # 設定画面のサービス
    # --------------------------------------------------------------------------

    # 設定画面遷移イベントハンドラ（UI）
    def move_to_settings(self):
        return self.settings_service.move_to_settings()

    # 設定画面ファイル一覧要求イベントハンドラ（UI）
    def get_settings_files(self):
        return self.settings_service.get_settings_files()

    # 設定画面・設定編集イベントハンドラ（UI）
    def edit_settings(self, settings_file):
        return self.settings_service.edit_settings(settings_file)
    
    # 設定画面・設定削除イベントハンドラ（UI）
    def delete_settings(self, settings_file):
        return self.settings_service.delete_settings(settings_file)

    # 設定画面確定イベントハンドラ（UI）
    def submit_settings(self, settings_file):
        return self.settings_service.submit_settings(settings_file)

    # 設定画面キャンセルイベントハンドラ（UI）
    def cancel_settings(self):
        return self.settings_service.cancel_settings()

    # --------------------------------------------------------------------------
    # ファイル横断検索画面のサービス
    # --------------------------------------------------------------------------

    # ファイル横断検索画面遷移イベントハンドラ（UI）
    def move_to_cross_file_search(self):
        return self.cross_file_search_service.move_to_cross_file_search()

    # ファイル横断検索結果を取得する（UI）
    def get_cross_search_results(self):
        return self.cross_file_search_service.get_cross_search_results()

    # ファイル横断検索の実行
    def search_across_files(self, search_text):
        return self.cross_file_search_service.search_across_files(search_text)

    # カレントチャット変更イベントハンドラ（UI）
    def move_to_chat_at(self, logfile, messageIndex, searchText):
        return self.cross_file_search_service.move_to_chat_at(logfile, messageIndex, searchText)

    # ファイル横断検索画面クローズイベントハンドラ（UI）
    def close_cross_file_search(self):
        return self.cross_file_search_service.close_cross_file_search()
