# ZundaGPT2 / ZundaGPT2 Lite
#
# エラー定義
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

# OpenAIのストリーミングが許可されていない場合に発生する例外
class StreamNotAllowedError(Exception):
    def __init__(self, original: Exception, detail: str | None = None):
        message = f"{detail or ''} (caused by {original.__class__.__name__}: {original})"
        super().__init__(message)
        self.original = original
        self.detail = detail

# OpenAIのResponses APIが要求されている場合に発生する例外（Completion APIが使えないモデルで発生する）
class ResponsesApiRequiredError(Exception):
    def __init__(self, original: Exception, detail: str | None = None):
        message = f"{detail or ''} (caused by {original.__class__.__name__}: {original})"
        super().__init__(message)
        self.original = original
        self.detail = detail
