import os, sys, yaml

# project_root を sys.path に追加
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)

from app.const import APP_NAME, APP_VERSION, COPYRIGHT

# バージョン情報ファイル
input_path = "build_tools/version.yaml"

# 書き換える内容
new_version = APP_VERSION + ".0"
new_copyright = COPYRIGHT.replace("Copyright", "©")
new_product_name = APP_NAME

# 元ファイル読み込み
with open(input_path, "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

# 書き換え
data["Version"] = new_version
data["LegalCopyright"] = new_copyright
data["ProductName"] = new_product_name

# 書き戻し
with open(input_path, "w", encoding="utf-8") as f:
    yaml.dump(data, f, allow_unicode=True, sort_keys=False)
