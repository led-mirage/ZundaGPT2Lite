# ZundaGPT2 / ZundaGPT2 Lite
#
# チャットクラス（Gemini）
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import os
import copy
from datetime import datetime

from google import genai
from google.genai.types import HarmCategory, HarmBlockThreshold, SafetySetting, GenerateContentConfig
from google.genai import errors as GenaiErrors

from .chat import Chat
from .listener import SendMessageListener
from utility.utils import parse_data_url, resize_base64_image
from utility.multi_lang import get_text_resource


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
    def send_onetime_message(self, text:str) -> str:
        response = self.client.models.generate_content(model=self.model, contents=[text])
        return response.text

    # メッセージを送信して回答を得る
    def send_message(
        self,
        text: str,
        images: list[str],
        listener: SendMessageListener) -> str:

        try:
            self.stop_send_event.clear()

            user_parts = [{"text": text}]
            for img_dataurl in images or []:
                media_type, image_format, b64 = parse_data_url(img_dataurl)
                b64 = resize_base64_image(b64, max_size_mb=15.0, output_format=image_format)
                user_parts.append({
                    "inline_data": {
                        "mime_type": media_type,
                        "data": b64
                    }
                })

            messages = copy.deepcopy(self.get_history())
            messages = self.convert_messages(messages)
            messages.append({"role": "user", "parts": user_parts})
            self.messages.append({"role": "user", "content": text})

            #self.messages.append({"role": "user", "content": text})
            #messages = copy.deepcopy(self.get_history())
            #messages = self.convert_messages(messages)

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
                        listener.on_receive_chunk(c)

                        if c == "`":
                            code_block += 1
                        else:
                            code_block = 0
                        
                        if code_block == 3:
                            code_block_inside = not code_block_inside

                        if c in ["。", "？", "！"]:
                            listener.on_receive_sentence(sentence)
                            sentence = ""

                        if not code_block_inside and c in ["\n"]:
                            listener.on_receive_paragraph(paragraph)
                            paragraph = ""

            if sentence != "":
                listener.on_receive_sentence(sentence)

            if paragraph != "":
                listener.on_receive_paragraph(paragraph)

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
