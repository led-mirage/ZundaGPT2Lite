# ZundaGPT2 / ZundaGPT2 Lite
#
# チャットクラス（AzureOpenAI）
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import os
import httpx

from openai import AzureOpenAI

from .chat_openai_base import ChatOpenAIBase
from utility.multi_lang import get_text_resource


# Azure OpenAI チャットクラス
class ChatAzureOpenAI(ChatOpenAIBase):
    def __init__(self, model: str, temperature: float, instruction: str, bad_response: str, history_size: int, history_char_limit: int,
                 api_timeout: float, api_key_envvar: str=None, api_endpoint: str=None):

        super().__init__(
            model = model,
            temperature = temperature,
            instruction = instruction,
            bad_response = bad_response,
            history_size = history_size,
            history_char_limit = history_char_limit
        )

        if api_key_envvar:
            api_key = os.environ.get(api_key_envvar)
        else:
            api_key = os.environ.get("AZURE_OPENAI_API_KEY")

        if api_endpoint:
            endpoint = os.environ.get(api_endpoint)
        else:
            endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")

        self._client = None
        if endpoint and api_key:
            self._client = AzureOpenAI(azure_endpoint=endpoint, api_key=api_key, api_version="2025-04-01-preview",
                                 timeout=httpx.Timeout(api_timeout, connect=5.0))

        if endpoint is None:
            self.client_creation_error = get_text_resource("ERROR_MISSING_AZURE_OPENAI_ENDPOINT")
        if api_key is None:
            self.client_creation_error = get_text_resource("ERROR_MISSING_AZURE_OPENAI_API_KEY")
