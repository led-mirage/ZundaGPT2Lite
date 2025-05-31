# ZundaGPT2 Lite
#
# ユーティリティ
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import inspect
import os


# 文字をエスケープする
def escape_js_string(s: str):
    return (
        s.replace('\\', '\\\\')  # バックスラッシュを最初にエスケープ
        .replace('\n', '\\n')    # 改行
        .replace('\r', '\\r')    # キャリッジリターン
        .replace('\t', '\\t')    # タブ
        .replace('"', '\\"')     # ダブルクォーテーション
        .replace('\'', '\\\'')   # シングルクォート
    )

# 実行中の関数の場所を取得する
def get_location(obj: object):
    frame = inspect.currentframe().f_back   # 呼び出し元のフレーム（1つ上のフレーム）
    filename = os.path.basename(frame.f_code.co_filename)
    lineno = frame.f_lineno
    funcname = frame.f_code.co_name
    classname = obj.__class__.__name__ + "." if obj and hasattr(obj, "__class__") else ""
    return f"{filename} ({lineno}) : {classname}{funcname}"

# 例外の型情報を取得する
def get_exception_name(e: Exception):
    module_name = type(e).__module__
    class_name = type(e).__name__
    return f"{module_name}.{class_name}"
