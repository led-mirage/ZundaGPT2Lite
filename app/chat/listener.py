# ZundaGPT2 / ZundaGPT2 Lite
#
# メッセージ送信時のイベントリスナー
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

from typing import Callable


# メッセージ送信時のイベントリスナー
class SendMessageListener:
    def __init__(
        self,
        on_recieve_chunk: Callable[[str], None] | None = None,
        on_recieve_sentence: Callable[[str], None] | None = None,
        on_recieve_paragraph: Callable[[str], None] | None = None,
        on_non_streaming_start: Callable[[], None] | None = None,
        on_non_streaming_end: Callable[[], None] | None = None,
        on_end_response: Callable[[str], None] | None = None,
        on_error: Callable[[Exception, str, str | None], None] | None = None,
    ) -> None:
        self._on_recieve_chunk = on_recieve_chunk or (lambda _t: None)
        self._on_recieve_sentence = on_recieve_sentence or (lambda _t: None)
        self._on_recieve_paragraph = on_recieve_paragraph or (lambda _t: None)
        self._on_non_streaming_start = on_non_streaming_start or (lambda: None)
        self._on_non_streaming_end = on_non_streaming_end or (lambda: None)
        self._end_response = on_end_response or (lambda _t: None)
        self._on_error = on_error or (lambda _e, _p, _m: None)

    def on_recieve_chunk(self, text: str) -> None: self._on_recieve_chunk(text)
    def on_recieve_sentence(self, text: str) -> None: self._on_recieve_sentence(text)
    def on_recieve_paragraph(self, text: str) -> None: self._on_recieve_paragraph(text)
    def on_non_streaming_start(self) -> None: self._on_non_streaming_start()
    def on_non_streaming_end(self) -> None: self._on_non_streaming_end()
    def on_end_response(self, text: str) -> None: self._end_response(text)
    def on_error(self, exc: Exception, phase: str, meta: str | None=None) -> None:
        self._on_error(exc, phase, meta)
