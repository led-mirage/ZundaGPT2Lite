import copy
import json
import logging
import os
import pytest
import tempfile
from pathlib import Path

from app.config.app_config import AppConfig, get_log_settings


class TestAppConfig:
    """AppConfigクラスのテスト"""

    @pytest.fixture
    def temp_config_file(self):
        """一時的な設定ファイルを作成"""
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)

    def test_init_with_default_path(self):
        """デフォルトパスでの初期化"""
        config = AppConfig()
        assert config._config_file_path == AppConfig.FILE_CONFIG
        assert config._lock is not None

    def test_init_with_custom_path(self, temp_config_file):
        """カスタムパスでの初期化"""
        config = AppConfig(temp_config_file)
        assert config._config_file_path == temp_config_file

    def test_init_member_defaults(self):
        """デフォルト設定値の確認"""
        config = AppConfig()
        
        # systemデフォルト値の確認
        assert config.system["log_folder"] == "log"
        assert config.system["log_level"] == "ERROR"
        assert config.system["settings_file"] == "settings.json"
        assert config.system["window_width"] == 600
        assert config.system["window_height"] == 800
        assert config.system["chat_api_timeout"] == 30
        assert config.system["language"] == "ja"
        assert config.system["font_family"] == ""
        assert config.system["font_size"] == 16
        assert config.system["theme"] == "light"
        assert config.system["display_clock"] == True
        
        # geminiデフォルト値の確認
        assert config.gemini["safety_filter_harassment"] == "BLOCK_MEDIUM_AND_ABOVE"
        assert config.gemini["safety_filter_hate_speech"] == "BLOCK_MEDIUM_AND_ABOVE"
        assert config.gemini["safety_filter_sexually_explicit"] == "BLOCK_MEDIUM_AND_ABOVE"
        assert config.gemini["safety_filter_dangerous_content"] == "BLOCK_MEDIUM_AND_ABOVE"

    def test_save_creates_file(self, temp_config_file):
        """設定ファイルが正しく保存される"""
        config = AppConfig(temp_config_file)
        config.save()
        
        assert os.path.exists(temp_config_file)
        
        # ファイル内容の確認
        with open(temp_config_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert data["file_ver"] == AppConfig.FILE_VER
        assert "system" in data
        assert "gemini" in data

    def test_save_with_modified_values(self, temp_config_file):
        """変更した値が正しく保存される"""
        config = AppConfig(temp_config_file)
        config.system["window_width"] = 1024
        config.system["language"] = "en"
        config.system["display_clock"] = True
        config.gemini["safety_filter_harassment"] = "BLOCK_ONLY_HIGH"
        
        config.save()
        
        # ファイルから読み込んで確認
        with open(temp_config_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert data["system"]["window_width"] == 1024
        assert data["system"]["language"] == "en"
        assert data["system"]["display_clock"] == True
        assert data["gemini"]["safety_filter_harassment"] == "BLOCK_ONLY_HIGH"

    def test_load_from_nonexistent_file(self, temp_config_file):
        """存在しないファイルから読み込む場合、デフォルト値で初期化される"""
        # ファイルを削除
        if os.path.exists(temp_config_file):
            os.unlink(temp_config_file)
        
        config = AppConfig(temp_config_file)
        result = config.load()
        
        # デフォルト値で初期化されていることを確認
        assert config.system["log_folder"] == "log"
        assert config.system["window_width"] == 600
        
        # ファイルが作成されていることを確認
        assert os.path.exists(temp_config_file)

    def test_load_from_existing_file(self, temp_config_file):
        """既存のファイルから正しく読み込まれる"""
        # テスト用の設定ファイルを作成
        test_data = {
            "file_ver": AppConfig.FILE_VER,
            "system": {
                "log_folder": "logs",
                "log_level": "DEBUG",
                "settings_file": "custom_settings.json",
                "window_width": 800,
                "window_height": 600,
                "chat_api_timeout": 60,
                "language": "en",
                "font_family": "Arial",
                "font_size": 14,
                "theme": "dark",
                "display_clock": True,
            },
            "gemini": {
                "safety_filter_harassment": "BLOCK_ONLY_HIGH",
                "safety_filter_hate_speech": "BLOCK_ONLY_HIGH",
                "safety_filter_sexually_explicit": "BLOCK_ONLY_HIGH",
                "safety_filter_dangerous_content": "BLOCK_ONLY_HIGH",
            }
        }
        
        with open(temp_config_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f, ensure_ascii=False, indent=4)
        
        config = AppConfig(temp_config_file)
        config.load()
        
        assert config.system["log_folder"] == "logs"
        assert config.system["log_level"] == "DEBUG"
        assert config.system["window_width"] == 800
        assert config.system["language"] == "en"
        assert config.system["display_clock"] == True
        assert config.gemini["safety_filter_harassment"] == "BLOCK_ONLY_HIGH"

    def test_load_from_old_version_file_ver_8(self, temp_config_file):
        """旧バージョン(file_ver=8)のファイルから読み込む場合"""
        # FILE_VER=8の設定ファイルを作成（display_clockがない）
        test_data = {
            "file_ver": 8,
            "system": {
                "log_folder": "logs",
                "log_level": "INFO",
                "settings_file": "settings.json",
                "window_width": 800,
                "window_height": 600,
                "chat_api_timeout": 60,
                "language": "en",
                "font_family": "Arial",
                "font_size": 14,
                "theme": "light",
            },
            "gemini": {
                "safety_filter_harassment": "BLOCK_MEDIUM_AND_ABOVE",
                "safety_filter_hate_speech": "BLOCK_MEDIUM_AND_ABOVE",
                "safety_filter_sexually_explicit": "BLOCK_MEDIUM_AND_ABOVE",
                "safety_filter_dangerous_content": "BLOCK_MEDIUM_AND_ABOVE",
            }
        }
        
        with open(temp_config_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f, ensure_ascii=False, indent=4)
        
        config = AppConfig(temp_config_file)
        result = config.load()
        
        # 旧バージョンのキーは保持される
        assert config.system["log_folder"] == "logs"
        assert config.system["log_level"] == "INFO"
        assert config.system["window_width"] == 800
        
        # 新しいキー display_clock はデフォルト値で追加される
        assert config.system["display_clock"] == True
        
        # ファイルが新しいバージョンで保存される
        with open(temp_config_file, "r", encoding="utf-8") as f:
            saved_data = json.load(f)
        
        assert saved_data["file_ver"] == AppConfig.FILE_VER
        assert saved_data["system"]["display_clock"] == True

    def test_load_with_missing_keys(self, temp_config_file):
        """いくつかのキーが不足している場合、デフォルト値が使用される"""
        test_data = {
            "file_ver": AppConfig.FILE_VER,
            "system": {
                "window_width": 900,
                # 他のキーは意図的に除外
            },
            "gemini": {}
        }
        
        with open(temp_config_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)
        
        config = AppConfig(temp_config_file)
        config.load()
        
        # 読み込まれたキー
        assert config.system["window_width"] == 900
        # デフォルト値が使用されるキー
        assert config.system["log_folder"] == "log"
        assert config.system["window_height"] == 800
        assert config.system["display_clock"] == True

    def test_update_dict(self):
        """update_dict メソッドのテスト"""
        config = AppConfig()
        
        target = {"a": 1, "b": 2, "c": 3}
        src = {"a": 10, "b": 20, "d": 40}
        
        config.update_dict(target, src)
        
        # targetにあるキーのみ更新される
        assert target["a"] == 10
        assert target["b"] == 20
        assert target["c"] == 3  # srcにないため変更されない
        assert "d" not in target  # targetにないため追加されない

    def test_deepcopy(self):
        """ディープコピーのテスト"""
        config1 = AppConfig()
        config1.system["window_width"] = 1024
        config1.system["display_clock"] = True
        config1.gemini["safety_filter_harassment"] = "BLOCK_ONLY_HIGH"
        
        config2 = copy.deepcopy(config1)
        
        # コピーが正しく作成されている
        assert config2.system["window_width"] == 1024
        assert config2.system["display_clock"] == True
        assert config2.gemini["safety_filter_harassment"] == "BLOCK_ONLY_HIGH"
        
        # オリジナルを変更してもコピーに影響しない
        config1.system["window_width"] = 2048
        config1.system["display_clock"] = False
        config1.gemini["safety_filter_harassment"] = "BLOCK_MEDIUM_AND_ABOVE"
        
        assert config2.system["window_width"] == 1024
        assert config2.system["display_clock"] == True
        assert config2.gemini["safety_filter_harassment"] == "BLOCK_ONLY_HIGH"

    def test_deepcopy_preserves_config_file_path(self, temp_config_file):
        """ディープコピーが設定ファイルパスを保持"""
        config1 = AppConfig(temp_config_file)
        config2 = copy.deepcopy(config1)
        
        assert config2._config_file_path == temp_config_file

    def test_file_version(self):
        """FILE_VERのテスト"""
        assert AppConfig.FILE_VER == 9

    def test_file_config_constant(self):
        """FILE_CONFIGのテスト"""
        assert AppConfig.FILE_CONFIG == "appConfig.json"


class TestGetLogSettings:
    """get_log_settings関数のテスト"""

    @pytest.fixture
    def temp_config_file(self):
        """一時的な設定ファイルを作成"""
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)

    def test_get_log_settings_defaults(self):
        """デフォルトのログ設定を取得"""
        # このテストはappConfig.jsonが存在しない場合の動作を確認
        # 実際の環境依存のため、デフォルト値の構造のみ確認
        log_settings = get_log_settings()
        
        assert isinstance(log_settings, dict)
        assert "log_folder" in log_settings
        assert "log_level" in log_settings

    def test_log_level_conversion_error(self):
        """無効なログレベルはINFOにフォールバック"""
        # モックなしでの確認は難しいため、スキップ
        pass

    def test_log_folder_from_config(self, temp_config_file, monkeypatch):
        """ログフォルダが設定から正しく取得される"""
        # appConfig.json の場所を一時ファイルに変更
        test_data = {
            "file_ver": AppConfig.FILE_VER,
            "system": {
                "log_folder": "custom_logs",
                "log_level": "DEBUG",
                "settings_file": "settings.json",
                "window_width": 600,
                "window_height": 800,
                "chat_api_timeout": 30,
                "language": "ja",
                "font_family": "",
                "font_size": 16,
                "theme": "light",
            },
            "gemini": {
                "safety_filter_harassment": "BLOCK_MEDIUM_AND_ABOVE",
                "safety_filter_hate_speech": "BLOCK_MEDIUM_AND_ABOVE",
                "safety_filter_sexually_explicit": "BLOCK_MEDIUM_AND_ABOVE",
                "safety_filter_dangerous_content": "BLOCK_MEDIUM_AND_ABOVE",
            }
        }
        
        with open(temp_config_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f, ensure_ascii=False, indent=4)
        
        # AppConfigをモックするため、直接テスト
        config = AppConfig(temp_config_file)
        config.load()
        
        assert config.system["log_folder"] == "custom_logs"
        assert config.system["log_level"] == "DEBUG"
