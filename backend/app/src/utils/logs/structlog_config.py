"""
Structlog 日志配置管理 - 阿里巴巴标准格式

基于 structlog 的现代化日志配置系统，提供高性能的结构化日志记录。
"""

import structlog
import logging
import logging.config
import sys
import os
import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union, Callable
from contextvars import ContextVar
from functools import wraps

# 请求上下文变量
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
trace_id_var: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)


class AliStandardProcessor:
    """阿里巴巴标准日志处理器"""
    
    def __init__(self):
        self._request_id = None
        self._trace_id = None
        self._user_id = None
    
    def __call__(self, logger, method_name, event_dict):
        """处理日志事件字典"""
        # 添加时间戳
        event_dict['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # 添加请求上下文
        request_id = request_id_var.get()
        trace_id = trace_id_var.get()
        user_id = user_id_var.get()
        
        if request_id:
            event_dict['request_id'] = request_id
        if trace_id:
            event_dict['trace_id'] = trace_id
        if user_id:
            event_dict['user_id'] = user_id
        
        # 添加服务信息
        event_dict['service'] = 'SmartTCM-Agent-SYSTEM'
        event_dict['version'] = '1.0.0'
        
        # 添加环境信息
        event_dict['environment'] = os.getenv('ENVIRONMENT', 'development')
        
        return event_dict


class JSONRenderer:
    """JSON 渲染器 - 阿里巴巴标准格式"""
    
    def __call__(self, logger, method_name, event_dict):
        """渲染为 JSON 格式"""
        # 确保中文字符正确显示
        return json.dumps(event_dict, ensure_ascii=False, separators=(',', ':'))


class ConsoleRenderer:
    """控制台渲染器 - 开发环境友好格式"""
    
    def __call__(self, logger, method_name, event_dict):
        """渲染为控制台友好格式"""
        # 提取关键信息
        timestamp = event_dict.get('timestamp', '')
        level = event_dict.get('level', 'INFO')
        logger_name = event_dict.get('logger', '')
        message = event_dict.get('event', '')
        
        # 构建基础日志行
        log_line = f"{timestamp} [{level}] {logger_name}: {message}"
        
        # 添加额外信息
        extra_info = []
        for key, value in event_dict.items():
            if key not in ['timestamp', 'level', 'logger', 'event']:
                if isinstance(value, dict):
                    extra_info.append(f"{key}={json.dumps(value, ensure_ascii=False)}")
                else:
                    extra_info.append(f"{key}={value}")
        
        if extra_info:
            log_line += f" | {' | '.join(extra_info)}"
        
        return log_line


class StructlogConfig:
    """Structlog 配置管理器"""
    
    def __init__(self):
        self.log_dir = Path("")
        self.log_dir.mkdir(exist_ok=True)
        self._configured = False
    
    def configure_development(self):
        """配置开发环境"""
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                AliStandardProcessor(),
                ConsoleRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # 配置标准库日志
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=logging.DEBUG,
        )
        
        self._configured = True
    
    def configure_production(self):
        """配置生产环境"""
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                AliStandardProcessor(),
                JSONRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # 配置文件日志
        self._setup_file_logging()
        self._configured = True
    
    def configure_test(self):
        """配置测试环境"""
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                AliStandardProcessor(),
                ConsoleRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # 测试环境只输出到控制台
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=logging.INFO,
        )
        
        self._configured = True
    
    def _setup_file_logging(self):
        """设置文件日志"""
        # 创建文件处理器
        file_handler = logging.FileHandler(
            self.log_dir / "app.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        
        # 错误日志处理器
        error_handler = logging.FileHandler(
            self.log_dir / "error.log",
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        
        # 业务日志处理器
        business_handler = logging.FileHandler(
            self.log_dir / "business.log",
            encoding='utf-8'
        )
        business_handler.setLevel(logging.INFO)
        
        # 配置根日志器
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(error_handler)
        root_logger.addHandler(business_handler)
    
    def configure(self, environment: str = None):
        """配置日志系统"""
        env = environment or os.getenv('ENVIRONMENT', 'development')
        
        if env == 'development':
            self.configure_development()
        elif env == 'production':
            self.configure_production()
        elif env == 'test':
            self.configure_test()
        else:
            self.configure_development()
        
        return self


# 全局配置实例
structlog_config = StructlogConfig()


def setup_structlog(environment: str = None):
    """设置 structlog 系统"""
    return structlog_config.configure(environment)


def get_structlog_logger(name: str) -> structlog.BoundLogger:
    """获取 structlog 日志记录器"""
    if not structlog_config._configured:
        setup_structlog()
    return structlog.get_logger(name)


class StructlogLogger:
    """Structlog 日志记录器包装类"""
    
    def __init__(self, name: str):
        self._logger = get_structlog_logger(name)
        self._name = name
    
    def _log_with_context(self, level: str, message: str, **kwargs):
        """带上下文的日志记录"""
        # 添加业务数据
        business_data = kwargs.pop('business_data', {})
        if business_data:
            kwargs['business'] = business_data
        
        # 添加性能数据
        duration = kwargs.pop('duration', None)
        if duration is not None:
            kwargs['duration_ms'] = duration
        
        # 记录日志
        getattr(self._logger, level)(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """调试日志"""
        self._log_with_context('debug', message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """信息日志"""
        self._log_with_context('info', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """警告日志"""
        self._log_with_context('warning', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """错误日志"""
        self._log_with_context('error', message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """严重错误日志"""
        self._log_with_context('critical', message, **kwargs)
    
    def log_api_request(self, method: str, path: str, **kwargs):
        """记录 API 请求"""
        self.info(
            f"API请求: {method} {path}",
            business_data={
                "type": "api_request",
                "method": method,
                "path": path,
                **kwargs
            }
        )
    
    def log_api_response(self, status_code: int, duration: float = None, **kwargs):
        """记录 API 响应"""
        self.info(
            f"API响应: {status_code}",
            business_data={
                "type": "api_response",
                "status_code": status_code,
                **kwargs
            },
            duration=duration
        )
    
    def log_business_operation(self, operation: str, entity_type: str, **kwargs):
        """记录业务操作"""
        self.info(
            f"业务操作: {operation} {entity_type}",
            business_data={
                "type": "business_operation",
                "operation": operation,
                "entity_type": entity_type,
                **kwargs
            }
        )
    
    def log_exception(self, exception: Exception, **kwargs):
        """记录异常"""
        self.error(
            f"异常发生: {type(exception).__name__}: {str(exception)}",
            business_data={
                "type": "exception",
                "exception_type": type(exception).__name__,
                "exception_message": str(exception),
                **kwargs
            }
        )
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """记录性能指标"""
        self.info(
            f"性能监控: {operation}",
            business_data={
                "type": "performance",
                "operation": operation,
                **kwargs
            },
            duration=duration
        )


def get_struct_logger(name: str) -> StructlogLogger:
    """获取日志记录器"""
    return StructlogLogger(name)


# 预定义的日志记录器
app_logger = get_struct_logger("app")
api_logger = get_struct_logger("api")
business_logger = get_struct_logger("business")
error_logger = get_struct_logger("error")
performance_logger = get_struct_logger("performance")


class LogContext:
    """日志上下文管理器"""
    
    def __init__(self, logger: StructlogLogger, operation: str, **context):
        self.logger = logger
        self.operation = operation
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"开始执行: {self.operation}", **self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (time.time() - self.start_time) * 1000
        
        if exc_type:
            self.logger.error(
                f"执行失败: {self.operation}",
                **self.context,
                duration=duration
            )
        else:
            self.logger.info(
                f"执行完成: {self.operation}",
                **self.context,
                duration=duration
            )


def log_context(operation: str, logger: StructlogLogger = None, **context):
    """日志上下文装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log = logger or get_struct_logger(func.__module__)
            with LogContext(log, operation, **context):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def set_request_context(request_id: str = None, trace_id: str = None, user_id: str = None):
    """设置请求上下文"""
    if request_id:
        request_id_var.set(request_id)
    if trace_id:
        trace_id_var.set(trace_id)
    if user_id:
        user_id_var.set(user_id)


def clear_request_context():
    """清除请求上下文"""
    request_id_var.set(None)
    trace_id_var.set(None)
    user_id_var.set(None)


def get_request_context() -> Dict[str, Optional[str]]:
    """获取请求上下文"""
    return {
        'request_id': request_id_var.get(),
        'trace_id': trace_id_var.get(),
        'user_id': user_id_var.get()
    }
