# ZundaGPT2 / ZundaGPT2 Lite
#
# ユーティリティ
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import base64
import inspect
import mimetypes
import os
import sys
import tkinter as tk
from pathlib import Path
from urllib.parse import urlparse


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

# 文字列がURLかどうかを調べる
def is_url(text: str) -> bool:
    try:
        result = urlparse(text)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

# URLまたはPathをCSSのurl()フォーマットに変換する
#   Pathの場合はBase64エンコードされる
#   URLでもPathでもない場合はNoneを返す
def to_css_url_format(url_or_path: str, filesize_limit_mb: float) -> str:
    if is_url(url_or_path):
        return f'url("{url_or_path}")'
    
    path = Path(url_or_path)
    if path.is_file():
        return to_data_url(path, filesize_limit_mb)
    
    return None

# ファイルをBase64エンコードしてurl()形式にして返す
def to_data_url(path: Path, filesize_limit_mb: float) -> str:
    if path.stat().st_size <= filesize_limit_mb * 1024 * 1024:
        mime, _ = mimetypes.guess_type(path)
        if not mime:
            mime = "application/octet-stream"
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        return f'url("data:{mime};base64,{b64}")'
    else:
        return ""

# プライマリディスプレイのサイズを取得する
def get_screen_size(window_handle=None) -> tuple[int, int]:
    if sys.platform == "win32":
        from utility.win32 import get_monitor_size_for_window
        return get_monitor_size_for_window(window_handle, use_work_area=True)
    else:
        try:
            root = tk.Tk()
            root.withdraw()
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.destroy()
            return screen_width, screen_height
        except Exception:
            # 取得できない場合はデフォルトサイズを返す
            return 800, 600
