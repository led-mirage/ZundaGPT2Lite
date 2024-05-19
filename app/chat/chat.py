# ZundaGPT2 Lite
#
# チャットクラス
#
# Copyright (c) 2024 led-mirage
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
from openai import APITimeoutError, AuthenticationError, NotFoundError
import google.generativeai as genai
import google.api_core.exceptions as google_exceptions
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# チャット基底クラス
class Chat:
    # コンストラクタ
    def __init__(self, client, model: str, instruction: str, bad_response: str, history_size: int):
        self.messages = []
        self.client = client
        self.model = model
        self.instruction = instruction
        self.bad_response = bad_response
        self.history_size = history_size
        self.chat_start_time = datetime.now()
        self.chat_update_time = datetime.now()
        self.stop_send_event = threading.Event()

    # 指定index以下のメッセージを切り捨てる
    def truncate_messages(self, index):
        self.messages = self.messages[:index]

    # 進行中のsend_message関数の送信を停止する
    def stop_send_message(self):
        self.stop_send_event.set()

    # メッセージを送信して回答を得る
    def send_message(
        self,
        text: str,
        recieve_chunk: Callable[[str], None],
        recieve_sentence: Callable[[str], None],
        end_response: Callable[[str], None],
        on_error: Callable[[Exception, str], None]) -> str:

        try:
            self.stop_send_event.clear()

            self.messages.append({"role": "user", "content": text})
            messages = self.messages[-self.history_size:]
            messages.insert(0, {"role": "system", "content": self.instruction})
            stream = self.client.chat.completions.create(model=self.model, messages=messages, stream=True)

            content = ""
            sentence = ""
            role = ""
            for chunk in stream:
                if self.stop_send_event.is_set():
                    break

                if chunk.choices[0].delta.role is not None:
                    role = chunk.choices[0].delta.role

                if chunk.choices[0].delta.content is not None:
                    chunk_content = chunk.choices[0].delta.content

                    content += chunk_content
                    sentence += chunk_content
                    recieve_chunk(chunk_content)

                    if sentence.endswith(("。", "\n", "？", "！")):
                        recieve_sentence(sentence)
                        sentence = ""

            if sentence != "":
                recieve_sentence(sentence)

            if content:
                self.messages.append({"role": role, "content": content})
                self.chat_update_time = datetime.now()
                end_response(content)
                return content
            else:
                end_response(self.bad_response)
                return self.bad_response
        except AuthenticationError as e:
            on_error(e, "Authentication")
        except (APITimeoutError, ReadTimeout, TimeoutError) as e:
            on_error(e, "Timeout")
        except NotFoundError as e:
            on_error(e, "EndPointNotFound")
        except Exception as e:
            on_error(e, "Exception")
        
# OpenAI チャットクラス
class ChatOpenAI(Chat):
    def __init__(self, model: str, instruction: str, bad_response: str, history_size: int, api_timeout: float):
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("環境変数 OPENAI_API_KEY が設定されていません。")

        client = OpenAI(timeout=httpx.Timeout(api_timeout, connect=5.0))
        super().__init__(
            client = client,
            model = model,
            instruction = instruction,
            bad_response = bad_response,
            history_size = history_size
        )

# Azure OpenAI チャットクラス
class ChatAzureOpenAI(Chat):
    def __init__(self, model: str, instruction: str, bad_response: str, history_size: int, api_timeout: float):
        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        if endpoint is None:
            raise ValueError("環境変数 AZURE_OPENAI_ENDPOINT が設定されていません。")

        api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("環境変数 AZURE_OPENAI_API_KEY が設定されていません。")

        client = AzureOpenAI(azure_endpoint=endpoint, api_key=api_key, api_version="2023-05-15", timeout=httpx.Timeout(api_timeout, connect=5.0))
        super().__init__(
            client = client,
            model = model,
            instruction = instruction,
            bad_response = bad_response,
            history_size = history_size
        )

# Azure OpenAI チャットクラス
class ChatAzureOpenAI(Chat):
    def __init__(self, model: str, instruction: str, bad_response: str, history_size: int, api_timeout: float):
        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        if endpoint is None:
            raise ValueError("環境変数 AZURE_OPENAI_ENDPOINT が設定されていません。")

        api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("環境変数 AZURE_OPENAI_API_KEY が設定されていません。")

        client = AzureOpenAI(azure_endpoint=endpoint, api_key=api_key, api_version="2023-05-15", timeout=httpx.Timeout(api_timeout, connect=5.0))
        super().__init__(
            client = client,
            model = model,
            instruction = instruction,
            bad_response = bad_response,
            history_size = history_size
        )

# Google Gemini チャットクラス
class ChatGemini(Chat):
    def __init__(self, model: str, instruction: str, bad_response: str, history_size: int, gemini_option: dict):
        self.gemini_option = gemini_option

        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key is None:
            raise ValueError("環境変数 GEMINI_API_KEY が設定されていません。")
        genai.configure(api_key=api_key)

        client = genai.GenerativeModel(model)
        super().__init__(
            client = client,
            model = model,
            instruction = instruction,
            bad_response = bad_response,
            history_size = history_size
        )

    # メッセージを送信して回答を得る
    def send_message(
        self,
        text: str,
        recieve_chunk: Callable[[str], None],
        recieve_sentence: Callable[[str], None],
        end_response: Callable[[str], None],
        on_error: Callable[[Exception, str], None]) -> str:

        try:
            self.stop_send_event.clear()

            self.messages.append({"role": "user", "content": text})
            messages = copy.deepcopy(self.messages[-self.history_size:])
            messages[-1]["content"] += f"　（{self.instruction}）"
            messages = self.convert_messages(messages)
            safety_settings = self.get_safety_settings()
            stream = self.client.generate_content(messages, safety_settings=safety_settings, stream=True)

            content = ""
            sentence = ""
            for chunk in stream:
                #print(chunk.candidates[0].safety_ratings)
                if self.stop_send_event.is_set():
                    break

                if chunk.text is not None:
                    chunk_content = chunk.text

                    content += chunk_content
                    sentence += chunk_content
                    recieve_chunk(chunk_content)

                    if sentence.endswith(("。", "\n", "？", "！")):
                        recieve_sentence(sentence)
                        sentence = ""

            if sentence != "":
                recieve_sentence(sentence)

            if content:
                self.messages.append({"role": "assistant", "content": content})
                self.chat_update_time = datetime.now()
                end_response(content)
                return content
            else:
                end_response(self.bad_response)
                return self.bad_response
        except (APITimeoutError, ReadTimeout, TimeoutError) as e:
            on_error(e, "Timeout")
        except google_exceptions.InvalidArgument as e:
            if e.reason == "API_KEY_INVALID":
                on_error(e, "Authentication")
            else:
                on_error(e, "InvalidArgument")
        except ValueError as e:
            on_error(e, "UnsafeContent")
        except Exception as e:
            on_error(e, "Exception")

    # 安全性フィルタの設定値を取得する
    def get_safety_settings(self):
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

        safty_settings = {}
        if self.gemini_option:
            if "safty_filter_harassment" in self.gemini_option:
                safty_settings[HarmCategory.HARM_CATEGORY_HARASSMENT] = convert_block_level(self.gemini_option["safty_filter_harassment"])
            if "safty_filter_hate_speech" in self.gemini_option:
                safty_settings[HarmCategory.HARM_CATEGORY_HATE_SPEECH] = convert_block_level(self.gemini_option["safty_filter_hate_speech"])
            if "safty_filter_sexually_explicit" in self.gemini_option:
                safty_settings[HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT] = convert_block_level(self.gemini_option["safty_filter_sexually_explicit"])
            if "safty_filter_dangerous_content" in self.gemini_option:
                safty_settings[HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT] = convert_block_level(self.gemini_option["safty_filter_dangerous_content"])
        return safty_settings
    
    # Geminiに送信する会話履歴をGeminiの形式に変換する
    def convert_messages(self, messages):
        gemini_messages = []
        for message in messages:
            role = message["role"]
            if role == "user":
                gemini_messages.append({"role": "user", "parts": [ message["content"] ]})
            elif role == "assistant":
                gemini_messages.append({"role": "model", "parts": [ message["content"] ]})
        return gemini_messages

# チャットファクトリー
class ChatFactory:
    # api_idに基づいてChatオブジェクトを作成する
    @staticmethod
    def create(api_id: str, model: str, instruction: str, bad_response: str, history_size: int, api_timeout: float, gemini_option: dict=None) -> Chat:
        if api_id == "OpenAI":
            return ChatOpenAI(model, instruction, bad_response, history_size, api_timeout)
        elif api_id == "AzureOpenAI":
            return ChatAzureOpenAI(model, instruction, bad_response, history_size, api_timeout)
        elif api_id == "Gemini":
            return ChatGemini(model, instruction, bad_response, history_size, gemini_option)
        else:
            raise ValueError("API IDが間違っています。")
