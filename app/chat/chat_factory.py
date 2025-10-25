# ZundaGPT2 / ZundaGPT2 Lite
#
# チャットファクトリ クラス
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

from .chat import Chat
from .chat_openai import ChatOpenAI
from .chat_azureopenai import ChatAzureOpenAI
from .chat_gemini import ChatGemini
from .chat_claude import ChatClaude
from utility.multi_lang import get_text_resource


# チャットファクトリー
class ChatFactory:
    # api_idに基づいてChatオブジェクトを作成する
    @staticmethod
    def create(api_id: str, model: str, instruction: str, bad_response: str, history_size: int, history_char_limit: int, api_timeout: float,
               api_key_envvar: str=None, api_key_endpoint: str=None, api_base_url: str=None, gemini_option: dict=None, claude_options: dict=None) -> Chat:
        if api_id == "OpenAI":
            return ChatOpenAI(model, instruction, bad_response, history_size, history_char_limit, api_timeout, api_key_envvar, api_base_url)
        elif api_id == "AzureOpenAI":
            return ChatAzureOpenAI(model, instruction, bad_response, history_size, history_char_limit, api_timeout, api_key_envvar, api_key_endpoint)
        elif api_id == "Gemini":
            return ChatGemini(model, instruction, bad_response, history_size, history_char_limit, api_key_envvar, gemini_option)
        elif api_id == "Claude":
            return ChatClaude(model, instruction, bad_response, history_size, history_char_limit, api_key_envvar, claude_options)
        else:
            raise ValueError(get_text_resource("ERROR_API_ID_IS_INCORRECT"))
