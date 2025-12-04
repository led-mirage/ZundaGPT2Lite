# ZundaGPT2 / ZundaGPT2 Lite
#
# チャットファクトリ クラス
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

from .chat_factory_options import ChatFactoryOptions
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
    def create(options: ChatFactoryOptions) -> Chat:
        if options.api_id == "OpenAI":
            return ChatOpenAI(
                options.model, options.temperature, options.instruction, options.bad_response, options.history_size, options.history_char_limit,
                options.api_timeout, options.api_key_envvar, options.api_base_url)
        elif options.api_id == "AzureOpenAI":
            return ChatAzureOpenAI(
                options.model, options.temperature, options.instruction, options.bad_response, options.history_size, options.history_char_limit,
                options.api_timeout, options.api_key_envvar, options.api_endpoint_envvar)
        elif options.api_id == "Gemini":
            return ChatGemini(
                options.model, options.temperature, options.instruction, options.bad_response, options.history_size, options.history_char_limit,
                options.api_key_envvar, options.gemini_option)
        elif options.api_id == "Claude":
            return ChatClaude(
                options.model, options.temperature, options.instruction, options.bad_response, options.history_size, options.history_char_limit,
                options.api_key_envvar, options.claude_options)
        else:
            raise ValueError(get_text_resource("ERROR_API_ID_IS_INCORRECT"))
