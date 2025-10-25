# ZundaGPT2 / ZundaGPT2 Lite
#
# チャットクラス（Claude）
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import os
from datetime import datetime

import anthropic

from .chat import Chat
from .listener import SendMessageListener
from utility.multi_lang import get_text_resource


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
