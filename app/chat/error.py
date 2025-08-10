# OpenAIのストリーミングが許可されていない場合に発生する例外
class StreamNotAllowedError(Exception):
    def __init__(self, original: Exception, detail: str | None = None):
        super().__init__(str(original))
        self.original = original
        self.detail = detail
