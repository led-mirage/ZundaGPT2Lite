# ZundaGPT2 Lite
#
# ユーティリティ
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

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
