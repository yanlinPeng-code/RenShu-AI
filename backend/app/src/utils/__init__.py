
"""
工具模块 - Structlog 版本

基于 structlog 的现代化日志管理工具。
"""
from app.src.utils.logs.logger import get_logger
from app.src.utils.logs.structlog_config import (
    setup_structlog, StructlogLogger, LogContext, log_context,
    set_request_context, clear_request_context, get_request_context,
    app_logger, api_logger, business_logger, error_logger, performance_logger, get_struct_logger
)
from app.src.utils.logs.structlog_middleware import (
    StructlogMiddleware, BusinessLoggingMiddleware,
    PerformanceLoggingMiddleware, SecurityLoggingMiddleware
)
from app.src.utils.logs.structlog_utils import (
    log_function_call, log_async_function_call, log_database_operation,
    log_api_endpoint, log_business_operation, log_performance_metric,
    log_exception_handler, create_logger_context, log_with_context
)

__all__ = [
    # 核心日志功能
    "setup_structlog",
    "get_struct_logger",
    "get_logger",
    "StructlogLogger",
    "LogContext",
    "log_context",
    
    # 请求上下文管理
    "set_request_context",
    "clear_request_context",
    "get_request_context",
    
    # 预定义日志记录器
    "app_logger",
    "api_logger",
    "business_logger",
    "error_logger",
    "performance_logger",
    
    # 中间件
    "StructlogMiddleware",
    "BusinessLoggingMiddleware",
    "PerformanceLoggingMiddleware",
    "SecurityLoggingMiddleware",
    
    # 工具装饰器
    "log_function_call",
    "log_async_function_call",
    "log_database_operation",
    "log_api_endpoint",
    "log_business_operation",
    "log_performance_metric",
    "log_exception_handler",
    "create_logger_context",
    "log_with_context"
]