# ZundaGPT2 / ZundaGPT2 Lite
#
# チャットファクトリオプション クラス
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

from dataclasses import dataclass


@dataclass
class ChatFactoryOptions:
    api_id: str
    model: str
    temperature: float
    instruction: str
    bad_response: str
    history_size: int
    history_char_limit: int
    api_timeout: float
    api_key_envvar: str
    api_endpoint_envvar: str
    api_base_url: str
    gemini_option: dict
    claude_options: dict
