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
from .error import StreamNotAllowedError, ResponsesApiRequiredError

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
            return self.send_message_completions_streaming(text, listener)

        except StreamNotAllowedError:
            self.messages = self.messages[:-1]
            return self.send_message_completions_not_streaming(text, listener)

        except ResponsesApiRequiredError:
            self.messages = self.messages[:-1]
            try:
                return self.send_message_responses_streaming(text, listener)
            except StreamNotAllowedError:
                self.messages = self.messages[:-1]
                return self.send_message_responses_not_streaming(text, listener)

    # メッセージを送信して回答を得る（Completions API・ストリーミング版）
    def send_message_completions_streaming(
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
            if e.status_code == 404 and e.param == "model":
                raise ResponsesApiRequiredError(e, "This model requires the Responses API.")
            listener.on_error(e, "EndPointNotFound")
        except Exception as e:
            listener.on_error(e, "Exception")

    # メッセージを送信して回答を得る（Completions API・非ストリーミング版）
    def send_message_completions_not_streaming(
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

    # メッセージを送信して回答を得る（Responses API・ストリーミング版）
    def send_message_responses_streaming(
        self,
        text: str,
        listener: SendMessageListener) -> str:

        try:
            self.stop_send_event.clear()

            self.messages.append({"role": "user", "content": text})
            messages = self.get_history()
            if not self.model.startswith(("o1", "o3")) and self.instruction:
                messages.insert(0, {"role": "system", "content": self.instruction})

            def convert_message(m):
                role = m["role"]
                if role == "assistant":
                    content_type = "output_text"
                else:
                    content_type = "input_text"
                return {
                    "role": role,
                    "content": [
                        {
                            "type": content_type,
                            "text": m["content"],
                        }
                    ],
                }

            responses_input = [convert_message(m) for m in messages]

            content = ""
            sentence = ""
            paragraph = ""
            role = "assistant"
            code_block = 0
            code_block_inside = False

            with self.client.responses.stream(
                model=self.model,
                input=responses_input,
            ) as stream:

                for event in stream:
                    if self.stop_send_event.is_set():
                        stream.close()
                        break

                    if event.type == "response.error":
                        listener.on_error(event.error, "StreamError")
                        stream.close()
                        return self.bad_response

                    if event.type != "response.output_text.delta":
                        continue

                    chunk_content = event.delta or ""
                    if not chunk_content:
                        continue

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

                        if not code_block_inside and c == "\n":
                            listener.on_receive_paragraph(paragraph)
                            paragraph = ""

                if self.stop_send_event.is_set():
                    listener.on_end_response(self.bad_response)
                    return self.bad_response

                final_response = stream.get_final_response()
                if final_response and final_response.output:
                    # Responses API は output 内に role が入っている
                    role = final_response.output[0].role or "assistant"

            if sentence:
                listener.on_receive_sentence(sentence)

            if paragraph:
                listener.on_receive_paragraph(paragraph)

            if content:
                self.messages.append({"role": role, "content": content})
                self.chat_update_time = datetime.now()
                listener.on_end_response(content)
                return content

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
            if e.status_code == 404 and e.param == "model":
                raise ResponsesApiRequiredError(e, "This model requires the Responses API.")
            listener.on_error(e, "EndPointNotFound")
        except Exception as e:
            listener.on_error(e, "Exception")

    # メッセージを送信して回答を得る（Responses API・非ストリーミング版）
    def send_message_responses_not_streaming(
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

            response = self.client.responses.create(
                model=self.model,
                input=messages,
                timeout=httpx.Timeout(300.0, connect=5.0)
            )

            # 出力テキストを抽出
            content = ""
            for item in response.output:
                if item.type == "message":
                    for sub in item.content:
                        if sub.type == "output_text":
                            content += sub.text

            listener.on_non_streaming_end()
            no_exception = True

            sentence = ""
            paragraph = ""
            code_block = 0
            code_block_inside = False

            for c in content:
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

            if content:
                self.messages.append({"role": "assistant", "content": content})
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
