# ZundaGPT2 / ZundaGPT2 Lite
#
# チャットクラス
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import os
import httpx
import threading
import copy
from datetime import datetime
from typing import Callable

from httpx import ReadTimeout
from openai import OpenAI
from openai import AzureOpenAI
from openai import APITimeoutError, AuthenticationError, NotFoundError, BadRequestError
from google import genai
from google.genai.types import HarmCategory, HarmBlockThreshold, SafetySetting, GenerateContentConfig
from google.genai import errors as GenaiErrors
import anthropic

from utility.multi_lang import get_text_resource
from chat.error import StreamNotAllowedError


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


# チャット基底クラス
class Chat:
    # コンストラクタ
    def __init__(self, client, model: str, instruction: str, bad_response: str, history_size: int, history_char_limit: int):
        self.messages = []
        self.client = client
        self.model = model
        self.instruction = instruction
        self.bad_response = bad_response
        self.history_size = history_size
        self.history_char_limit = history_char_limit
        self.chat_start_time = datetime.now()
        self.chat_update_time = datetime.now()
        self.stop_send_event = threading.Event()
        self.client_creation_error = ""

    # AIエージェントが利用可能かどうかを返す
    def is_ai_agent_available(self):
        return self.client is not None

    # 指定index以下のメッセージを切り捨てる
    def truncate_messages(self, index):
        self.messages = self.messages[:index]

    # 進行中のsend_message関数の送信を停止する
    def stop_send_message(self):
        self.stop_send_event.set()

    # メッセージを送信して回答を得る（同期処理、一度きりの質問）
    def send_onetime_message(self, text:str):
        messages = []
        messages.append({"role": "system", "content": self.instruction})
        messages.append({"role": "user", "content": text})
        completion = self.client.chat.completions.create(model=self.model, messages=messages)
        return completion.choices[0].message.content

    # 送信する会話履歴を取得するメッセージメッセージ
    def get_history(self):
        # まずhistory_size件だけ切り出す
        target_messages = self.messages[-self.history_size:]

        # history_char_limitの指定がなければそのまま返す
        if self.history_char_limit <= 0:
            return target_messages

        # 末尾（新しい順）から合計文字数をカウントしつつ、history_char_limitで切る
        result = []
        total_chars = 0

        # 新しい順から遡って処理
        for msg in reversed(target_messages):
            msg_len = len(msg["content"])
            # 3件以上あって、かつ文字数が上限を超えたらbreak
            if len(result) >= 3 and total_chars + msg_len > self.history_char_limit:
                break
            result.append(msg)
            total_chars += msg_len
        
        if len(result) % 2 == 0:
            # 偶数件なら、一番古いメッセージを削除する（アシスタントのメッセージ）
            result.pop()

        # 新しい順に並び替えて返却
        return list(reversed(result))

    # メッセージを送信して回答を得る
    def send_message(
        self,
        text: str,
        listener: SendMessageListener) -> str:

        try:
            return self.send_message_streaming(text, listener)
        except StreamNotAllowedError as e:
            self.messages = self.messages[:-1]
            return self.send_message_not_streaming(text, listener)

    # メッセージを送信して回答を得る（ストリーミング機能有効）
    def send_message_streaming(
        self,
        text: str,
        listener: SendMessageListener) -> str:

        try:
            self.stop_send_event.clear()

            self.messages.append({"role": "user", "content": text})
            messages = self.get_history()
            if not self.model.startswith("o1") and not self.model.startswith("o3") and self.instruction:
                messages.insert(0, {"role": "system", "content": self.instruction})
            stream = self.client.chat.completions.create(model=self.model, messages=messages, stream=True)

            content = ""
            sentence = ""
            paragraph = ""
            role = ""
            code_block = 0
            code_block_inside = False

            for chunk in stream:
                if self.stop_send_event.is_set():
                    break

                if chunk.choices and chunk.choices[0].delta.role is not None:
                    role = chunk.choices[0].delta.role

                if chunk.choices and chunk.choices[0].delta.content is not None:
                    chunk_content = chunk.choices[0].delta.content

                    content += chunk_content

                    for c in chunk_content:
                        sentence += c
                        paragraph += c
                        listener.on_recieve_chunk(c)

                        if c == "`":
                            code_block += 1
                        else:
                            code_block = 0
                        
                        if code_block == 3:
                            code_block_inside = not code_block_inside

                        if c in ["。", "？", "！"]:
                            listener.on_recieve_sentence(sentence)
                            sentence = ""

                        if not code_block_inside and c in ["\n"]:
                            listener.on_recieve_paragraph(paragraph)
                            paragraph = ""

            if sentence != "":
                listener.on_recieve_sentence(sentence)
            
            if paragraph != "":
                listener.on_recieve_paragraph(paragraph)

            if content:
                self.messages.append({"role": role, "content": content})
                self.chat_update_time = datetime.now()
                listener.on_end_response(content)
                return content
            else:
                listener.on_end_response(self.bad_response)
                return self.bad_response
        except BadRequestError as e:
            if e.status_code == 400 and e.param == "stream":
                raise StreamNotAllowedError(e, "This model/organization does not allow streaming.")
            else:
                listener.on_error(e, "BadRequestError")
        except AuthenticationError as e:
            listener.on_error(e, "Authentication")
        except (APITimeoutError, ReadTimeout, TimeoutError) as e:
            listener.on_error(e, "Timeout")
        except NotFoundError as e:
            listener.on_error(e, "EndPointNotFound")
        except Exception as e:
            listener.on_error(e, "Exception")

    # メッセージを送信して回答を得る（ストリーミング機能無効）
    def send_message_not_streaming(
        self,
        text: str,
        listener: SendMessageListener) -> str:

        try:
            no_exception = False
            listener.on_non_streaming_start()

            self.messages.append({"role": "user", "content": text})
            messages = self.get_history()
            if not self.model.startswith("o1") and not self.model.startswith("o3") and self.instruction:
                messages.insert(0, {"role": "system", "content": self.instruction})

            completion = self.client.chat.completions.create(model=self.model, messages=messages, timeout=httpx.Timeout(300.0, connect=5.0))
            content = completion.choices[0].message.content
            role = completion.choices[0].message.role

            listener.on_non_streaming_end()
            no_exception = True

            sentence = ""
            paragraph = ""
            code_block = 0
            code_block_inside = False

            for c in content:
                sentence += c
                paragraph += c
                listener.on_recieve_chunk(c)

                if c == "`":
                    code_block += 1
                else:
                    code_block = 0
                
                if code_block == 3:
                    code_block_inside = not code_block_inside

                if c in ["。", "？", "！"]:
                    listener.on_recieve_sentence(sentence)
                    sentence = ""

                if not code_block_inside and c in ["\n"]:
                    listener.on_recieve_paragraph(paragraph)
                    paragraph = ""

            if content:
                self.messages.append({"role": role, "content": content})
                self.chat_update_time = datetime.now()
                listener.on_end_response(content)
                return content
            else:
                listener.on_end_response(self.bad_response)
                return self.bad_response
            
        except AuthenticationError as e:
            listener.on_error(e, "Authentication")
        except (APITimeoutError, ReadTimeout, TimeoutError) as e:
            listener.on_error(e, "Timeout")
        except NotFoundError as e:
            listener.on_error(e, "EndPointNotFound")
        except Exception as e:
            listener.on_error(e, "Exception")
        finally:
            if not no_exception:
                listener.on_non_streaming_end()


# OpenAI チャットクラス
class ChatOpenAI(Chat):
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


# Azure OpenAI チャットクラス
class ChatAzureOpenAI(Chat):
    def __init__(self, model: str, instruction: str, bad_response: str, history_size: int, history_char_limit: int,
                 api_timeout: float, api_key_envvar: str=None, api_endpoint: str=None):

        if api_key_envvar:
            api_key = os.environ.get(api_key_envvar)
        else:
            api_key = os.environ.get("AZURE_OPENAI_API_KEY")

        if api_endpoint:
            endpoint = os.environ.get(api_endpoint)
        else:
            endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")

        client = None
        if endpoint and api_key:
            client = AzureOpenAI(azure_endpoint=endpoint, api_key=api_key, api_version="2025-04-01-preview",
                                 timeout=httpx.Timeout(api_timeout, connect=5.0))

        super().__init__(
            client = client,
            model = model,
            instruction = instruction,
            bad_response = bad_response,
            history_size = history_size,
            history_char_limit = history_char_limit
        )

        if endpoint is None:
            self.client_creation_error = get_text_resource("ERROR_MISSING_AZURE_OPENAI_ENDPOINT")
        if api_key is None:
            self.client_creation_error = get_text_resource("ERROR_MISSING_AZURE_OPENAI_API_KEY")


# Google Gemini チャットクラス
class ChatGemini(Chat):
    def __init__(self, model: str, instruction: str, bad_response: str, history_size: int, history_char_limit: int,
                 api_key_envvar: str=None, gemini_option: dict=None):

        self.gemini_option: dict = gemini_option

        if api_key_envvar:
            api_key = os.environ.get(api_key_envvar)
        else:
            api_key = os.environ.get("GEMINI_API_KEY")

        client = None
        if api_key:
            client = genai.Client(api_key=api_key)

        super().__init__(
            client = client,
            model = model,
            instruction = instruction,
            bad_response = bad_response,
            history_size = history_size,
            history_char_limit = history_char_limit
        )

        if api_key is None:
            self.client_creation_error = get_text_resource("ERROR_MISSING_GEMINI_API_KEY")

    # メッセージを送信して回答を得る（同期処理、一度きりの質問）
    def send_onetime_message(self, text:str):
        response = self.client.models.generate_content(model=self.model, contents=[text])
        return response.text

    # メッセージを送信して回答を得る
    def send_message(
        self,
        text: str,
        listener: SendMessageListener) -> str:

        try:
            self.stop_send_event.clear()

            self.messages.append({"role": "user", "content": text})
            messages = copy.deepcopy(self.get_history())
            messages = self.convert_messages(messages)

            stream = self.client.models.generate_content_stream(
                model=self.model,
                contents=messages,
                config=GenerateContentConfig(
                    system_instruction=self.instruction,
                    safety_settings=self.get_safety_settings()
                )
            )

            content = ""
            sentence = ""
            paragraph = ""
            code_block = 0
            code_block_inside = False

            for chunk in stream:
                #print(chunk.candidates[0].safety_ratings)
                if self.stop_send_event.is_set():
                    break

                if chunk.text is not None:
                    chunk_content = chunk.text

                    content += chunk_content

                    for c in chunk_content:
                        sentence += c
                        paragraph += c
                        listener.on_recieve_chunk(c)

                        if c == "`":
                            code_block += 1
                        else:
                            code_block = 0
                        
                        if code_block == 3:
                            code_block_inside = not code_block_inside

                        if c in ["。", "？", "！"]:
                            listener.on_recieve_sentence(sentence)
                            sentence = ""

                        if not code_block_inside and c in ["\n"]:
                            listener.on_recieve_paragraph(paragraph)
                            paragraph = ""

            if sentence != "":
                listener.on_recieve_sentence(sentence)

            if paragraph != "":
                listener.on_recieve_paragraph(paragraph)

            if content:
                self.messages.append({"role": "assistant", "content": content})
                self.chat_update_time = datetime.now()
                listener.on_end_response(content)
                return content
            else:
                listener.on_end_response(self.bad_response)
                return self.bad_response
        except GenaiErrors.APIError as e:
            """
            https://ai.google.dev/gemini-api/docs/troubleshooting?hl=ja
            400 INVALID_ARGUMENT
            400 FAILED_PRECONDITION
            403 PERMISSION_DENIED
            404 NOT_FOUND
            429 RESOURCE_EXHAUSTED
            500 INTERNAL
            503 UNAVAILABLE
            504 DEADLINE_EXCEEDED
            """
            message = f"{e.code} {e.status} - {e.message}"
            listener.on_error(e, "APIError", message)
        except Exception as e:
            listener.on_error(e, "Exception")

    # 安全性フィルタの設定値を取得する
    def get_safety_settings(self):
        def convert_category(category: str):
            value = HarmCategory.HARM_CATEGORY_UNSPECIFIED
            if category == "safety_filter_harassment":
                value = HarmCategory.HARM_CATEGORY_HARASSMENT
            elif category == "safety_filter_hate_speech":
                value = HarmCategory.HARM_CATEGORY_HATE_SPEECH
            elif category == "safety_filter_sexually_explicit":
                value = HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT
            elif category == "safety_filter_dangerous_content":
                value = HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT
            return value

        def convert_block_level(block_level: str):
            value =  HarmBlockThreshold.HARM_BLOCK_THRESHOLD_UNSPECIFIED
            if block_level == "BLOCK_NONE":
                value = HarmBlockThreshold.BLOCK_NONE
            elif block_level == "BLOCK_ONLY_HIGH":
                value = HarmBlockThreshold.BLOCK_ONLY_HIGH
            elif block_level == "BLOCK_MEDIUM_AND_ABOVE":
                value = HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
            elif block_level == "BLOCK_LOW_AND_ABOVE":
                value = HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
            return value

        safety_settings = []
        for key, value in self.gemini_option.items():
            safety_settings.append(
                SafetySetting(
                    category=convert_category(key),
                    threshold=convert_block_level(value)
                )
            )
        return safety_settings
    
    # Geminiに送信する会話履歴をGeminiの形式に変換する
    def convert_messages(self, messages):
        gemini_messages = []
        for message in messages:
            role = message["role"]
            if role == "user":
                gemini_messages.append({"role": "user", "parts": [{"text": message["content"]}]})
            elif role == "assistant":
                gemini_messages.append({"role": "model", "parts": [{"text": message["content"]}]})
        return gemini_messages


# Anthropic Claude チャットクラス
class ChatClaude(Chat):
    def __init__(self, model: str, instruction: str, bad_response: str, history_size: int, history_char_limit: int,
                 api_key_envvar: str=None, claude_options: dict=None):

        self.claude_options = claude_options

        if api_key_envvar:
            api_key = os.environ.get(api_key_envvar)
        else:
            api_key = os.environ.get("ANTHROPIC_API_KEY")

        client = None
        if api_key:
            client = anthropic.Anthropic(api_key=api_key)

        super().__init__(
            client = client,
            model = model,
            instruction = instruction,
            bad_response = bad_response,
            history_size = history_size,
            history_char_limit = history_char_limit
        )

        if api_key is None:
            self.client_creation_error = get_text_resource("ERROR_MISSING_ANTHROPIC_API_KEY")

    # メッセージを送信して回答を得る（同期処理、一度きりの質問）
    def send_onetime_message(self, text:str):
        messages = []
        messages.append({"role": "user", "content": text})
        response = self.client.messages.create(
            max_tokens=4096,
            system=self.instruction,
            messages=messages,
            model=self.model)
        return response.content[0].text

    # メッセージを送信して回答を得る
    def send_message(
        self,
        text: str,
        listener: SendMessageListener) -> str:

        try:
            self.stop_send_event.clear()

            self.messages.append({"role": "user", "content": text})
            messages = self.get_history()

            content = ""
            sentence = ""
            paragraph = ""

            max_tokens = self.claude_options["max_tokens"]
            if self.claude_options["extended_thinking"]:
                thinking = {
                    "type": "enabled",
                    "budget_tokens": self.claude_options["budget_tokens"]
                }
            else:
                thinking = {
                    "type": "disabled"
                }

            with self.client.messages.stream(
                max_tokens=max_tokens,
                thinking=thinking,
                system=self.instruction,
                messages=messages,
                model=self.model,
            ) as stream:
                code_block = 0
                code_block_inside = False

                for text in stream.text_stream:
                    if self.stop_send_event.is_set():
                        break

                    if text is not None:
                        chunk_content = text

                        content += chunk_content

                        for c in chunk_content:
                            sentence += c
                            paragraph += c
                            listener.on_recieve_chunk(c)

                            if c == "`":
                                code_block += 1
                            else:
                                code_block = 0
                            
                            if code_block == 3:
                                code_block_inside = not code_block_inside

                            if c in ["。", "？", "！"]:
                                listener.on_recieve_sentence(sentence)
                                sentence = ""

                            if not code_block_inside and c in ["\n"]:
                                listener.on_recieve_paragraph(paragraph)
                                paragraph = ""

                if sentence != "":
                    listener.on_recieve_sentence(sentence)

                if paragraph != "":
                    listener.on_recieve_paragraph(paragraph)

                if content:
                    self.messages.append({"role": "assistant", "content": content})
                    self.chat_update_time = datetime.now()
                    listener.on_end_response(content)
                    return content
                else:
                    listener.on_end_response(self.bad_response)
                    return self.bad_response
        except anthropic.APITimeoutError as e:
            listener.on_error(e, "Timeout")
        except anthropic.APIConnectionError as e:
            listener.on_error(e, "APIConnectionError")
        except anthropic.RateLimitError as e:
            listener.on_error(e, "RateLimit")
        except anthropic.APIStatusError as e:
            if e.status_code == 400:
                listener.on_error(e, "APIError", "Invalid Request(400)")
            elif e.status_code == 401:
                listener.on_error(e, "Authentication")
            elif e.status_code == 403:
                listener.on_error(e, "APIError", "Permission Denied(403)")
            elif e.status_code == 404:
                listener.on_error(e, "APIError", "Not Found(404)")
            elif e.status_code == 413:
                listener.on_error(e, "APIError", "Request too large(413)")
            elif e.status_code == 422:
                listener.on_error(e, "APIError", "UnprocessableEntity(422)")
            elif e.status_code == 429:
                listener.on_error(e, "APIError", "RateLimit")
            elif e.status_code == 529:
                listener.on_error(e, "APIError", "Overloaded(529)")
            else:
                listener.on_error(e, "APIError", f"Internal Server Error({e.status_code})")
        except Exception as e:
            listener.on_error(e, "Exception")


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
