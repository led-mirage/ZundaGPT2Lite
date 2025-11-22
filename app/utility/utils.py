# ZundaGPT2 / ZundaGPT2 Lite
#
# ユーティリティ
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import base64
import inspect
import io
import mimetypes
import os
import re
import sys
import tkinter as tk
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image


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
#   URLでもPathでもない場合は空文字を返す
def to_css_url_format(url_or_path: str, filesize_limit_mb: float) -> str:
    if is_url(url_or_path):
        return f'url("{url_or_path}")'
    
    path = Path(url_or_path)
    if path.is_file():
        return to_data_url(path, filesize_limit_mb)
    
    return ""

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

# data URL 形式の文字列を解析して (media_type, subtype, base64_data) を返す
# 想定外の形式の場合は ('image/png', 'png', data_url) を返す
def parse_data_url(data_url: str) -> tuple[str, str, str]:
    if not isinstance(data_url, str):
        return "image/png", "png", ""

    match = re.match(r"^data:(.*?);base64,(.*)$", data_url)
    if match:
        media_type = match.group(1).strip() or "image/png"
        b64_data = match.group(2).strip()

        # 画像タイプ部分だけ抽出する
        subtype_match = re.match(r"^image/(\w+)$", media_type)
        subtype = subtype_match.group(1) if subtype_match else "png"

        return media_type, subtype, b64_data
    else:
        # 想定外の場合はPNG扱い
        return "image/png", "png", data_url.strip()

# Base64エンコードされた画像データを指定サイズ以下に圧縮する
def resize_base64_image(b64_data: str, max_size_mb: float, output_format="JPEG", quality_step=5) -> str:
    img_bytes = base64.b64decode(b64_data)
    image = Image.open(io.BytesIO(img_bytes))
    size_mb = len(img_bytes) / (1024 * 1024)
    if size_mb <= max_size_mb:
        return b64_data

    buffer = io.BytesIO()
    if output_format.upper() == "JPEG":
        # JPEGは画質を下げながら圧縮
        quality = 95
        while True:
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=quality)
            new_data = buffer.getvalue()
            new_size = len(new_data) / (1024 * 1024)
            if new_size <= max_size_mb or quality <= 10:
                break
            quality -= quality_step

    else:
        # PNGなどはリサイズ主体で対応
        width, height = image.size
        while True:
            buffer = io.BytesIO()
            image.save(buffer, format=output_format, optimize=True, compress_level=9)
            new_data = buffer.getvalue()
            new_size = len(new_data) / (1024 * 1024)
            if new_size <= max_size_mb or (width < 100 or height < 100):
                break
            # サイズがまだ大きいなら10%ずつ縮小
            width, height = int(width * 0.9), int(height * 0.9)
            image = image.resize((width, height), Image.LANCZOS)

    return base64.b64encode(buffer.getvalue()).decode("utf-8")
