"""
简化的日志模块
"""

import logging
import sys
import os
from pathlib import Path
from datetime import datetime


class SimpleFormatter(logging.Formatter):
    """简单日志格式化器"""

    def format(self, record):
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        return f"[{timestamp}] {record.levelname} [{record.name}] {record.getMessage()}"


class LoggerManager:
    """日志管理器"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if LoggerManager._initialized:
            return
        LoggerManager._initialized = True

        self._loggers = {}
        self._setup()

    def _setup(self):
        """设置日志配置"""
        # 日志目录: logger.py -> logs -> utils -> src -> app -> backend
        project_root = Path(__file__).parent.parent.parent.parent.parent
        log_dir = project_root / "logs"

        create_logs = os.getenv("CREATE_LOGS_DIR", "true").lower() == "true"
        if create_logs:
            log_dir.mkdir(exist_ok=True)

        # 配置根日志器
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)

        # 清除现有处理器
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        formatter = SimpleFormatter()

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # 文件处理器
        if create_logs:
            file_handler = logging.FileHandler(log_dir / "app.log", encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

            error_handler = logging.FileHandler(log_dir / "error.log", encoding='utf-8')
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            root_logger.addHandler(error_handler)

    def get_logger(self, name: str) -> logging.Logger:
        """获取日志器"""
        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)
        return self._loggers[name]


# 全局日志管理器
_manager = LoggerManager()


def get_logger(name: str) -> logging.Logger:
    """获取日志记录器"""
    return _manager.get_logger(name)
