# ZundaGPT2 / ZundaGPT2 Lite
#
# チャットクラス
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

from abc import abstractmethod
from dataclasses import dataclass
import threading
from datetime import datetime

from .listener import SendMessageListener


# チャット基底クラス
class Chat:
    messages: list
    chat_start_time: datetime
    chat_update_time: datetime
    client_creation_error: str
    _client: object
    _model: str
    _temperature: float
    _instruction: str
    _bad_response: str
    _history_size: int
    _history_char_limit: int
    _stop_send_event: threading.Event

    # コンストラクタ
    def __init__(self, model: str, temperature: float, instruction: str, bad_response: str, history_size: int, history_char_limit: int):
        self.messages = []
        self.chat_start_time = datetime.now()
        self.chat_update_time = datetime.now()
        self.client_creation_error = ""
        self._client = None
        self._model = model
        self._temperature = temperature
        self._instruction = instruction
        self._bad_response = bad_response
        self._history_size = history_size
        self._history_char_limit = history_char_limit
        self._stop_send_event = threading.Event()

    # AIエージェントが利用可能かどうかを返す
    def is_ai_agent_available(self):
        return self._client is not None

    # 指定index以下のメッセージを切り捨てる
    def truncate_messages(self, index):
        self.messages = self.messages[:index]

    # 進行中のsend_message関数の送信を停止する
    def stop_send_message(self):
        self._stop_send_event.set()

    @abstractmethod
    def send_onetime_message(self, text: str) -> str:
        pass

    @abstractmethod
    def send_message(self, text: str, images: list[str], listener: SendMessageListener) -> str:
        pass

    # 送信する会話履歴を取得するメッセージメッセージ
    def _get_history(self):
        # まずhistory_size件だけ切り出す
        target_messages = self.messages[-self._history_size:]

        # history_char_limitの指定がなければそのまま返す
        if self._history_char_limit <= 0:
            return target_messages

        # 末尾（新しい順）から合計文字数をカウントしつつ、history_char_limitで切る
        result = []
        total_chars = 0

        # 新しい順から遡って処理
        for msg in reversed(target_messages):
            msg_len = len(msg["content"])
            # 3件以上あって、かつ文字数が上限を超えたらbreak
            if len(result) >= 3 and total_chars + msg_len > self._history_char_limit:
                break
            result.append(msg)
            total_chars += msg_len
        
        if len(result) % 2 == 0:
            # 偶数件なら、一番古いメッセージを削除する（アシスタントのメッセージ）
            result.pop()

        # 新しい順に並び替えて返却
        return list(reversed(result))
