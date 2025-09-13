# ZundaGPT2 / ZundaGPT2 Lite
#
# ログ出力
#
# Copyright (c) 2024-2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import os
import logging
from logging.handlers import RotatingFileHandler

from const import APP_NAME


class AppLogger:
    """
    他のライブラリのログ出力が、自分のログファイルに出力されないようにしたロガークラス
    """
    LOG_FILENAME = "applog.txt"
    LOG_MAX_BYTES = 1024 * 1024  # 1MB
    LOG_BACKUP_COUNT = 5         # ログファイルを5個までローテート

    _logger = None

    @staticmethod
    def init_logger(log_dir: str, level: int = logging.INFO):
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, AppLogger.LOG_FILENAME)

        logger = logging.getLogger(APP_NAME)  # 名前付きloggerにしてルートロガーから切り離す
        logger.setLevel(level)  # ログレベルを設定
        logger.propagate = False  # root loggerに伝播しない

        # ハンドラが二重に追加されないように
        if not logger.handlers:
            handler = RotatingFileHandler(
                log_path,
                maxBytes=AppLogger.LOG_MAX_BYTES,
                backupCount=AppLogger.LOG_BACKUP_COUNT,
                encoding="utf-8"
            )
            formatter = logging.Formatter(
                # ログレコードの書式の定義（時間 レベル: アプリ名: メッセージ）
                "%(asctime)s %(levelname)s: %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        AppLogger._logger = logger

    @staticmethod
    def debug(message: str):
        if AppLogger._logger:
            AppLogger._logger.debug(message)

    @staticmethod
    def info(message: str):
        if AppLogger._logger:
            AppLogger._logger.info(message)

    @staticmethod
    def warning(message: str):
        if AppLogger._logger:
            AppLogger._logger.warning(message)

    @staticmethod
    def error(message: str):
        if AppLogger._logger:
            AppLogger._logger.error(message)

    @staticmethod
    def critical(message: str):
        if AppLogger._logger:
            AppLogger._logger.critical(message)
