# ZundaGPT2 / ZundaGPT2 Lite
#
# チャットクラス（Claude）
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import copy
import os
from datetime import datetime

import anthropic

from .chat import Chat
from .listener import SendMessageListener
from utility.utils import parse_data_url, resize_base64_image
from utility.multi_lang import get_text_resource


# Anthropic Claude チャットクラス
class ChatClaude(Chat):
    MAX_IMAGE_SIZE_MB = 4.0

    def __init__(self, model: str, temperature: float, instruction: str, bad_response: str, history_size: int, history_char_limit: int,
                 api_key_envvar: str=None, claude_options: dict=None):

        super().__init__(
            model = model,
            temperature = temperature,
            instruction = instruction,
            bad_response = bad_response,
            history_size = history_size,
            history_char_limit = history_char_limit
        )

        self.claude_options = claude_options

        if api_key_envvar:
            api_key = os.environ.get(api_key_envvar)
        else:
            api_key = os.environ.get("ANTHROPIC_API_KEY")

        self._client = None
        if api_key:
            self._client = anthropic.Anthropic(api_key=api_key)

        if api_key is None:
            self.client_creation_error = get_text_resource("ERROR_MISSING_ANTHROPIC_API_KEY")

    # メッセージを送信して回答を得る（同期処理、一度きりの質問）
    def send_onetime_message(self, text:str):
        messages = []
        messages.append({"role": "user", "content": text})

        response = self._client.messages.create(
            max_tokens=4096,
            system=self._instruction,
            messages=messages,
            model=self._model
            )
        return response.content[0].text

    # メッセージを送信して回答を得る
    def send_message(
        self,
        text: str,
        images: list[str],
        listener: SendMessageListener) -> str:

        try:
            self._stop_send_event.clear()

            self.messages.append({"role": "user", "content": text})
            messages = copy.deepcopy(self._get_history())

            if images and len(images) > 0:
                messages = messages[:-1]
                content = []
                if text:
                    content.append({"type": "text", "text": text})

                for image in images:
                    media_type, image_format, b64 = parse_data_url(image)
                    b64 = resize_base64_image(b64, max_size_mb=self.MAX_IMAGE_SIZE_MB, output_format=image_format)
                    content.append(
                        {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}}
                    )

                messages.append({"role": "user", "content": content})

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

            temperature = anthropic.omit
            if self._temperature:
                temperature = self._temperature

            with self._client.messages.stream(
                max_tokens=max_tokens,
                thinking=thinking,
                system=self._instruction,
                messages=messages,
                model=self._model,
                temperature=temperature
            ) as stream:
                code_block = 0
                code_block_inside = False

                for text in stream.text_stream:
                    if self._stop_send_event.is_set():
                        break

                    if text is not None:
                        chunk_content = text

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
                    listener.on_end_response(self._bad_response)
                    return self._bad_response
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
