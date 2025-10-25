# ZundaGPT2 / ZundaGPT2 Lite
#
# チャットクラス（OpenAI基底）
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import httpx
from datetime import datetime
from httpx import ReadTimeout

from openai import APITimeoutError, AuthenticationError, NotFoundError, BadRequestError

from .chat import Chat
from .listener import SendMessageListener
from .error import StreamNotAllowedError

class ChatOpenAIBase(Chat):
    # メッセージを送信して回答を得る（同期処理、一度きりの質問）
    def send_onetime_message(self, text:str):
        messages = []
        messages.append({"role": "system", "content": self.instruction})
        messages.append({"role": "user", "content": text})
        completion = self.client.chat.completions.create(model=self.model, messages=messages)
        return completion.choices[0].message.content

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
