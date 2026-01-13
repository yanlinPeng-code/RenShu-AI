"""
日志配置管理 - 配置文件

提供灵活的日志配置管理，支持不同环境和级别的日志配置。
"""

import logging.config
import os
from pathlib import Path
from typing import Dict, Any, Optional


class LoggingConfig:
    """日志配置管理器"""
    
    def __init__(self):
        self.log_dir = Path("")
        self.log_dir.mkdir(exist_ok=True)
        self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认日志配置"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                },
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                },
                "json": {
                    "()": "app.src.utils.logger.AliStandardFormatter",
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            },
            "filters": {
                "request_context": {
                    "()": "app.src.utils.logger.RequestContextFilter"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",
                    "formatter": "standard",
                    "stream": "ext://sys.stdout",
                    "filters": ["request_context"]
                },
                "file_all": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "detailed",
                    "filename": str(self.log_dir / "app.log"),
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                    "encoding": "utf-8",
                    "filters": ["request_context"]
                },
                "file_error": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "ERROR",
                    "formatter": "detailed",
                    "filename": str(self.log_dir / "error.log"),
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                    "encoding": "utf-8",
                    "filters": ["request_context"]
                },
                "file_business": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "INFO",
                    "formatter": "json",
                    "filename": str(self.log_dir / "business.log"),
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                    "encoding": "utf-8",
                    "filters": ["request_context"]
                },
                "file_api": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "INFO",
                    "formatter": "json",
                    "filename": str(self.log_dir / "api.log"),
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                    "encoding": "utf-8",
                    "filters": ["request_context"]
                },
                "file_performance": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "INFO",
                    "formatter": "json",
                    "filename": str(self.log_dir / "performance.log"),
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                    "encoding": "utf-8",
                    "filters": ["request_context"]
                }
            },
            "loggers": {
                "app": {
                    "level": "DEBUG",
                    "handlers": ["console", "file_all"],
                    "propagate": False
                },
                "api": {
                    "level": "INFO",
                    "handlers": ["console", "file_api"],
                    "propagate": False
                },
                "business": {
                    "level": "INFO",
                    "handlers": ["console", "file_business"],
                    "propagate": False
                },
                "error": {
                    "level": "ERROR",
                    "handlers": ["console", "file_error"],
                    "propagate": False
                },
                "performance": {
                    "level": "INFO",
                    "handlers": ["file_performance"],
                    "propagate": False
                },
                "uvicorn": {
                    "level": "INFO",
                    "handlers": ["console", "file_all"],
                    "propagate": False
                },
                "uvicorn.access": {
                    "level": "INFO",
                    "handlers": ["console", "file_api"],
                    "propagate": False
                }
            },
            "root": {
                "level": "INFO",
                "handlers": ["console", "file_all"]
            }
        }
    
    def get_development_config(self) -> Dict[str, Any]:
        """获取开发环境配置"""
        config = self._get_default_config()
        # 开发环境：更详细的日志，控制台输出
        config["loggers"]["app"]["level"] = "DEBUG"
        config["loggers"]["api"]["level"] = "DEBUG"
        config["handlers"]["console"]["level"] = "DEBUG"
        return config
    
    def get_production_config(self) -> Dict[str, Any]:
        """获取生产环境配置"""
        config = self._get_default_config()
        # 生产环境：减少控制台输出，增加文件日志
        config["handlers"]["console"]["level"] = "WARNING"
        config["loggers"]["app"]["level"] = "INFO"
        config["loggers"]["api"]["level"] = "INFO"
        
        # 添加邮件处理器（可选）
        config["handlers"]["email"] = {
            "class": "logging.handlers.SMTPHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "mailhost": os.getenv("SMTP_HOST", "localhost"),
            "fromaddr": os.getenv("SMTP_FROM", "noreply@example.com"),
            "toaddrs": os.getenv("SMTP_TO", "admin@example.com").split(","),
            "subject": "应用错误日志"
        }
        
        config["loggers"]["error"]["handlers"].append("email")
        return config
    
    def get_test_config(self) -> Dict[str, Any]:
        """获取测试环境配置"""
        config = self._get_default_config()
        # 测试环境：只输出到控制台，减少文件日志
        config["loggers"]["app"]["handlers"] = ["console"]
        config["loggers"]["api"]["handlers"] = ["console"]
        config["loggers"]["business"]["handlers"] = ["console"]
        config["loggers"]["error"]["handlers"] = ["console"]
        config["loggers"]["performance"]["handlers"] = ["console"]
        return config
    
    def configure_logging(self, environment: str = None):
        """配置日志系统"""
        env = environment or os.getenv("ENVIRONMENT", "development")
        
        if env == "development":
            config = self.get_development_config()
        elif env == "production":
            config = self.get_production_config()
        elif env == "test":
            config = self.get_test_config()
        else:
            config = self._get_default_config()
        
        logging.config.dictConfig(config)
        return config
    
    def add_custom_handler(self, name: str, handler_config: Dict[str, Any]):
        """添加自定义处理器"""
        self._config["handlers"][name] = handler_config
    
    def add_custom_logger(self, name: str, logger_config: Dict[str, Any]):
        """添加自定义日志器"""
        self._config["loggers"][name] = logger_config
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return self._config.copy()


# 全局配置实例
logging_config = LoggingConfig()


def setup_logging(environment: str = None):
    """设置日志系统"""
    return logging_config.configure_logging(environment)


def get_logging_config(environment: str = None) -> Dict[str, Any]:
    """获取日志配置"""
    env = environment or os.getenv("ENVIRONMENT", "development")
    
    if env == "development":
        return logging_config.get_development_config()
    elif env == "production":
        return logging_config.get_production_config()
    elif env == "test":
        return logging_config.get_test_config()
    else:
        return logging_config.get_config()