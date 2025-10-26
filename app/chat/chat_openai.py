# ZundaGPT2 / ZundaGPT2 Lite
#
# チャットクラス（OpenAI）
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import os
import httpx

from openai import OpenAI

from .chat_openai_base import ChatOpenAIBase
from utility.multi_lang import get_text_resource


# OpenAI チャットクラス
class ChatOpenAI(ChatOpenAIBase):
    def __init__(self, model: str, instruction: str, bad_response: str, history_size: int, history_char_limit: int,
                 api_timeout: float, api_key_envvar: str=None, api_base_url: str=None):

        if api_key_envvar:
            api_key = os.environ.get(api_key_envvar)
        else:
            api_key = os.environ.get("OPENAI_API_KEY")

        client = None
        if api_key:
            base_url = api_base_url if api_base_url else None
            client = OpenAI(base_url=base_url, api_key=api_key, timeout=httpx.Timeout(api_timeout, connect=5.0))

        super().__init__(
            client = client,
            model = model,
            instruction = instruction,
            bad_response = bad_response,
            history_size = history_size,
            history_char_limit = history_char_limit
        )

        if api_key is None:
            self.client_creation_error = get_text_resource("ERROR_MISSING_OPENAI_API_KEY")
