import os
import sys
import re

# project_root を sys.path に追加
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)

from app.const import APP_VERSION

def update_manifest():
    manifest_path = os.path.join(CURRENT_DIR, "app.manifest")
    
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # version="X.X.X.X" を探して置換する
        # assemblyIdentity タグの中にある version 属性をターゲットにするのが理想だが、
        # ファイル全体で version="..." が assemblyIdentity にしか出てこないなら単純置換で良い。
        # 安全のため、assemblyIdentity ... version="..." のパターンを探す。
        
        new_version = f"{APP_VERSION}.0"
        
        # Regex pattern: look for <assemblyIdentity ... version="old_version" ...
        # We capture the version part to replace it.
        pattern = r'(<assemblyIdentity[^>]*version=")([^"]+)(")'
        
        match = re.search(pattern, content)
        if match:
            current_version = match.group(2)
            print(f"Current manifest version: {current_version}")
            print(f"New manifest version: {new_version}")
            
            if current_version != new_version:
                
                # 安全のため、変更箇所が本当に assemblyIdentity 内か確認（単純なreplaceだと他にもマッチする可能性があるため）
                # regex sub を使う方が確実
                new_content = re.sub(pattern, f'\\g<1>{new_version}\\g<3>', content, count=1)
                
                with open(manifest_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Successfully updated {manifest_path}")
            else:
                print("Manifest version is already up to date.")
        else:
            print("Error: assemblyIdentity with version attribute not found")
            sys.exit(1)

    except Exception as e:
        print(f"Error updating manifest: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_manifest()
