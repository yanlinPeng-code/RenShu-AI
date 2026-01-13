"""
日志配置管理 - 阿里巴巴标准格式

提供统一的日志记录功能，支持结构化日志、异常追踪和性能监控。
"""

import logging
import logging.config
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional, Union
from pathlib import Path
import traceback
import uuid


class AliStandardFormatter(logging.Formatter):
    """阿里巴巴标准日志格式化器"""
    
    def __init__(self, use_json_format=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._request_id = None
        self._trace_id = None
        self.use_json_format = use_json_format
    
    def set_request_context(self, request_id: str = None, trace_id: str = None):
        """设置请求上下文"""
        self._request_id = request_id
        self._trace_id = trace_id
    
    def format(self, record):
        """格式化日志记录"""
        # 如果使用JSON格式，则使用原来的格式化方式
        if self.use_json_format:
            # 基础日志信息
            log_data = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
                "thread": record.thread,
                "process": record.process
            }
            
            # 添加请求上下文
            if self._request_id:
                log_data["request_id"] = self._request_id
            if self._trace_id:
                log_data["trace_id"] = self._trace_id
            
            # 添加异常信息
            if record.exc_info:
                log_data["exception"] = {
                    "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                    "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                    "traceback": traceback.format_exception(*record.exc_info)
                }
            
            # 添加额外字段
            if hasattr(record, 'extra_data'):
                log_data["extra"] = record.extra_data
            
            # 添加性能指标
            if hasattr(record, 'duration'):
                log_data["duration_ms"] = record.duration
            
            # 添加业务信息
            if hasattr(record, 'business_data'):
                log_data["business"] = record.business_data
            
            return json.dumps(log_data, ensure_ascii=False, indent=2)
        else:
            # 使用简单的字符串格式
            timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
            log_message = f"[{timestamp}] {record.levelname} [{record.name}] {record.getMessage()}"
            
            # 添加请求上下文（如果存在）
            context_parts = []
            if self._request_id:
                context_parts.append(f"request_id={self._request_id}")
            if self._trace_id:
                context_parts.append(f"trace_id={self._trace_id}")
            
            if context_parts:
                log_message += " [" + ", ".join(context_parts) + "]"
            
            # 添加额外字段（如果存在）
            if hasattr(record, 'extra_data'):
                extra_str = ", ".join([f"{k}={v}" for k, v in record.extra_data.items()])
                log_message += f" Extra: {extra_str}"
            
            # 添加业务信息（如果存在）
            if hasattr(record, 'business_data'):
                business_str = ", ".join([f"{k}={v}" for k, v in record.business_data.items()])
                log_message += f" Business: {business_str}"
            
            # 添加性能指标（如果存在）
            if hasattr(record, 'duration'):
                log_message += f" Duration: {record.duration}ms"
            
            return log_message


class RequestContextFilter(logging.Filter):
    """请求上下文过滤器"""
    
    def __init__(self):
        super().__init__()
        self._request_id = None
        self._trace_id = None
    
    def set_request_context(self, request_id: str = None, trace_id: str = None):
        """设置请求上下文"""
        self._request_id = request_id
        self._trace_id = trace_id
    
    def filter(self, record):
        """过滤日志记录"""
        record.request_id = self._request_id
        record.trace_id = self._trace_id
        return True


class LoggerManager:
    """日志管理器"""
    
    def __init__(self, create_logs_dir: bool = True, use_json_format: bool = None):
        self._loggers: Dict[str, logging.Logger] = {}
        self._formatters: Dict[str, AliStandardFormatter] = {}
        self._request_context = RequestContextFilter()
        
        # 如果没有明确指定use_json_format，则根据环境变量判断
        if use_json_format is None:
            use_json_format = os.getenv("USE_JSON_LOG_FORMAT", "false").lower() == "true"
        
        self._setup_default_config(create_logs_dir, use_json_format)
    
    def _setup_default_config(self, create_logs_dir: bool = True, use_json_format: bool = False):
        """设置默认日志配置"""
        # 创建日志目录（仅在需要时）
        # 使用项目根目录下的logs文件夹
        project_root = Path(__file__).parent.parent.parent.parent  # 从当前文件定位到项目根目录
        log_dir = project_root / "logs"
        if create_logs_dir:
            log_dir.mkdir(exist_ok=True)
        
        # 配置日志格式
        self._formatters['standard'] = AliStandardFormatter(use_json_format=use_json_format)
        self._formatters['detailed'] = AliStandardFormatter(use_json_format=use_json_format)
        
        # 配置根日志器
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # 清除现有处理器
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self._formatters['standard'])
        console_handler.addFilter(self._request_context)
        root_logger.addHandler(console_handler)
        
        # 文件处理器 - 所有日志（仅在需要时添加）
        if create_logs_dir:
            file_handler = logging.FileHandler(
                log_dir / "app.log",
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(self._formatters['detailed'])
            file_handler.addFilter(self._request_context)
            root_logger.addHandler(file_handler)
            
            # 错误日志文件
            error_handler = logging.FileHandler(
                log_dir / "error.log",
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(self._formatters['detailed'])
            error_handler.addFilter(self._request_context)
            root_logger.addHandler(error_handler)
            
            # 业务日志文件
            business_handler = logging.FileHandler(
                log_dir / "business.log",
                encoding='utf-8'
            )
            business_handler.setLevel(logging.INFO)
            business_handler.setFormatter(self._formatters['detailed'])
            business_handler.addFilter(self._request_context)
            root_logger.addHandler(business_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """获取日志器"""
        if name not in self._loggers:
            logger = logging.getLogger(name)
            self._loggers[name] = logger
        return self._loggers[name]
    
    def set_request_context(self, request_id: str = None, trace_id: str = None):
        """设置请求上下文"""
        self._request_context.set_request_context(request_id, trace_id)
        for formatter in self._formatters.values():
            formatter.set_request_context(request_id, trace_id)
    
    def clear_request_context(self):
        """清除请求上下文"""
        self.set_request_context(None, None)


# 全局日志管理器实例
logger_manager = LoggerManager(
    create_logs_dir=os.getenv("CREATE_LOGS_DIR", "true").lower() == "true",
    use_json_format=os.getenv("USE_JSON_LOG_FORMAT", "false").lower() == "true"
)


class Logger:
    """日志记录器包装类"""
    
    def __init__(self, name: str):
        self._logger = logger_manager.get_logger(name)
        self._request_id = None
        self._trace_id = None
    
    def set_request_context(self, request_id: str = None, trace_id: str = None):
        """设置请求上下文"""
        self._request_id = request_id
        self._trace_id = trace_id
        logger_manager.set_request_context(request_id, trace_id)
    
    def _log_with_context(self, level: int, message: str, extra_data: Dict[str, Any] = None, 
                          business_data: Dict[str, Any] = None, duration: float = None):
        """带上下文的日志记录"""
        extra = {}
        if extra_data:
            extra['extra_data'] = extra_data
        if business_data:
            extra['business_data'] = business_data
        if duration is not None:
            extra['duration'] = duration
        
        self._logger.log(level, message, extra=extra if extra else None)
    
    def debug(self, message: str, extra_data: Dict[str, Any] = None, 
              business_data: Dict[str, Any] = None, duration: float = None):
        """调试日志"""
        self._log_with_context(logging.DEBUG, message, extra_data, business_data, duration)
    
    def info(self, message: str, extra_data: Dict[str, Any] = None, 
             business_data: Dict[str, Any] = None, duration: float = None):
        """信息日志"""
        self._log_with_context(logging.INFO, message, extra_data, business_data, duration)
    
    def warning(self, message: str, extra_data: Dict[str, Any] = None, 
                business_data: Dict[str, Any] = None, duration: float = None):
        """警告日志"""
        self._log_with_context(logging.WARNING, message, extra_data, business_data, duration)
    
    def error(self, message: str, extra_data: Dict[str, Any] = None, 
              business_data: Dict[str, Any] = None, duration: float = None, 
              exc_info: bool = True):
        """错误日志"""
        self._log_with_context(logging.ERROR, message, extra_data, business_data, duration)
        if exc_info:
            self._logger.exception(message)
    
    def critical(self, message: str, extra_data: Dict[str, Any] = None, 
                 business_data: Dict[str, Any] = None, duration: float = None, 
                 exc_info: bool = True):
        """严重错误日志"""
        self._log_with_context(logging.CRITICAL, message, extra_data, business_data, duration)
        if exc_info:
            self._logger.exception(message)
    
    def log_api_request(self, method: str, path: str, params: Dict[str, Any] = None, 
                       headers: Dict[str, str] = None, body: Any = None):
        """记录API请求"""
        business_data = {
            "type": "api_request",
            "method": method,
            "path": path,
            "params": params,
            "headers": headers,
            "body": body
        }
        self.info(f"API请求: {method} {path}", business_data=business_data)
    
    def log_api_response(self, status_code: int, response_data: Any = None, 
                        duration: float = None):
        """记录API响应"""
        business_data = {
            "type": "api_response",
            "status_code": status_code,
            "response_data": response_data
        }
        self.info(f"API响应: {status_code}", business_data=business_data, duration=duration)
    
    def log_business_operation(self, operation: str, entity_type: str, 
                              entity_id: str = None, details: Dict[str, Any] = None):
        """记录业务操作"""
        business_data = {
            "type": "business_operation",
            "operation": operation,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "details": details
        }
        self.info(f"业务操作: {operation} {entity_type}", business_data=business_data)
    
    def log_exception(self, exception: Exception, context: Dict[str, Any] = None):
        """记录异常"""
        extra_data = {
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "context": context
        }
        self.error(f"异常发生: {type(exception).__name__}: {str(exception)}", 
                  extra_data=extra_data)
    
    def log_performance(self, operation: str, duration: float, 
                       details: Dict[str, Any] = None):
        """记录性能指标"""
        business_data = {
            "type": "performance",
            "operation": operation,
            "details": details
        }
        self.info(f"性能监控: {operation}", business_data=business_data, duration=duration)


def get_logger(name: str) -> Logger:
    """获取日志记录器"""
    return Logger(name)


# 预定义的日志记录器
app_logger = get_logger("app")
api_logger = get_logger("api")
business_logger = get_logger("business")
error_logger = get_logger("error")
performance_logger = get_logger("performance")


class LogContext:
    """日志上下文管理器"""
    
    def __init__(self, logger: Logger, operation: str, **context):
        self.logger = logger
        self.operation = operation
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"开始执行: {self.operation}", extra_data=self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds() * 1000
        
        if exc_type:
            self.logger.error(f"执行失败: {self.operation}", 
                            extra_data=self.context, duration=duration)
        else:
            self.logger.info(f"执行完成: {self.operation}", 
                           extra_data=self.context, duration=duration)


def log_context(operation: str, logger: Logger = None, **context):
    """日志上下文装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            log = logger or get_logger(func.__module__)
            with LogContext(log, operation, **context):
                return func(*args, **kwargs)
        return wrapper
    return decorator