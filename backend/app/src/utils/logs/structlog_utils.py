"""
Structlog 工具函数 - 阿里巴巴标准格式

提供便捷的日志记录工具函数和装饰器。
"""

import time
import functools
from typing import Any, Dict, Optional, Callable, TypeVar, Union
from .structlog_config import get_struct_logger, LogContext, log_context

T = TypeVar('T')


def log_function_call(logger_name: str = None, log_args: bool = True, log_result: bool = True):
    """函数调用日志装饰器"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            logger = get_struct_logger(logger_name or func.__module__)
            
            # 记录函数调用开始
            call_info = {
                "function": func.__name__,
                "module": func.__module__,
            }
            
            if log_args:
                call_info.update({
                    "args": args,
                    "kwargs": kwargs
                })
            
            logger.info(f"调用函数: {func.__name__}", **call_info)
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # 记录函数调用成功
                duration = (time.time() - start_time) * 1000
                success_info = {
                    "function": func.__name__,
                    "duration_ms": duration,
                    "status": "success"
                }
                
                if log_result:
                    success_info["result"] = result
                
                logger.info(f"函数调用成功: {func.__name__}", **success_info)
                
                return result
                
            except Exception as e:
                # 记录函数调用失败
                duration = (time.time() - start_time) * 1000
                error_info = {
                    "function": func.__name__,
                    "duration_ms": duration,
                    "status": "error",
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                
                logger.error(f"函数调用失败: {func.__name__}", **error_info)
                raise
        
        return wrapper
    return decorator


def log_async_function_call(logger_name: str = None, log_args: bool = True, log_result: bool = True):
    """异步函数调用日志装饰器"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            logger = get_struct_logger(logger_name or func.__module__)
            
            # 记录函数调用开始
            call_info = {
                "function": func.__name__,
                "module": func.__module__,
            }
            
            if log_args:
                call_info.update({
                    "args": args,
                    "kwargs": kwargs
                })
            
            logger.info(f"调用异步函数: {func.__name__}", **call_info)
            
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # 记录函数调用成功
                duration = (time.time() - start_time) * 1000
                success_info = {
                    "function": func.__name__,
                    "duration_ms": duration,
                    "status": "success"
                }
                
                if log_result:
                    success_info["result"] = result
                
                logger.info(f"异步函数调用成功: {func.__name__}", **success_info)
                
                return result
                
            except Exception as e:
                # 记录函数调用失败
                duration = (time.time() - start_time) * 1000
                error_info = {
                    "function": func.__name__,
                    "duration_ms": duration,
                    "status": "error",
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                
                logger.error(f"异步函数调用失败: {func.__name__}", **error_info)
                raise
        
        return wrapper
    return decorator


def log_database_operation(operation: str, table: str = None):
    """数据库操作日志装饰器"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            logger = get_struct_logger("database")
            
            # 记录数据库操作开始
            db_info = {
                "operation": operation,
                "table": table,
                "function": func.__name__
            }
            
            logger.info(f"数据库操作开始: {operation}", **db_info)
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # 记录数据库操作成功
                duration = (time.time() - start_time) * 1000
                success_info = {
                    "operation": operation,
                    "table": table,
                    "duration_ms": duration,
                    "status": "success"
                }
                
                logger.info(f"数据库操作成功: {operation}", **success_info)
                
                return result
                
            except Exception as e:
                # 记录数据库操作失败
                duration = (time.time() - start_time) * 1000
                error_info = {
                    "operation": operation,
                    "table": table,
                    "duration_ms": duration,
                    "status": "error",
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                
                logger.error(f"数据库操作失败: {operation}", **error_info)
                raise
        
        return wrapper
    return decorator


def log_api_endpoint(endpoint_name: str = None):
    """API端点日志装饰器"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            logger = get_struct_logger("api")
            endpoint = endpoint_name or func.__name__
            
            # 记录API端点调用开始
            api_info = {
                "endpoint": endpoint,
                "function": func.__name__,
                "module": func.__module__
            }
            
            logger.info(f"API端点调用开始: {endpoint}", **api_info)
            
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # 记录API端点调用成功
                duration = (time.time() - start_time) * 1000
                success_info = {
                    "endpoint": endpoint,
                    "duration_ms": duration,
                    "status": "success"
                }
                
                logger.info(f"API端点调用成功: {endpoint}", **success_info)
                
                return result
                
            except Exception as e:
                # 记录API端点调用失败
                duration = (time.time() - start_time) * 1000
                error_info = {
                    "endpoint": endpoint,
                    "duration_ms": duration,
                    "status": "error",
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                
                logger.error(f"API端点调用失败: {endpoint}", **error_info)
                raise
        
        return wrapper
    return decorator


def log_business_operation(operation: str, entity_type: str = None):
    """业务操作日志装饰器"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            logger = get_struct_logger("business")
            entity = entity_type or "unknown"
            
            # 记录业务操作开始
            business_info = {
                "operation": operation,
                "entity_type": entity,
                "function": func.__name__
            }
            
            logger.log_business_operation(operation, entity, **business_info)
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # 记录业务操作成功
                duration = (time.time() - start_time) * 1000
                success_info = {
                    "operation": operation,
                    "entity_type": entity,
                    "duration_ms": duration,
                    "status": "success"
                }
                
                logger.info(f"业务操作成功: {operation}", **success_info)
                
                return result
                
            except Exception as e:
                # 记录业务操作失败
                duration = (time.time() - start_time) * 1000
                error_info = {
                    "operation": operation,
                    "entity_type": entity,
                    "duration_ms": duration,
                    "status": "error",
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                
                logger.error(f"业务操作失败: {operation}", **error_info)
                raise
        
        return wrapper
    return decorator


def log_performance_metric(metric_name: str, threshold_ms: float = None):
    """性能指标日志装饰器"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            logger = get_struct_logger("performance")
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # 计算执行时间
                duration = (time.time() - start_time) * 1000
                
                # 记录性能指标
                performance_info = {
                    "metric_name": metric_name,
                    "function": func.__name__,
                    "duration_ms": duration
                }
                
                # 检查是否超过阈值
                if threshold_ms and duration > threshold_ms:
                    logger.warning(
                        f"性能指标超阈值: {metric_name}",
                        **performance_info,
                        threshold_ms=threshold_ms
                    )
                else:
                    logger.log_performance(metric_name, duration, **performance_info)
                
                return result
                
            except Exception as e:
                # 记录异常性能
                duration = (time.time() - start_time) * 1000
                error_info = {
                    "metric_name": metric_name,
                    "function": func.__name__,
                    "duration_ms": duration,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                
                logger.error(f"性能指标异常: {metric_name}", **error_info)
                raise
        
        return wrapper
    return decorator


def log_exception_handler(exception_type: type, logger_name: str = None):
    """异常处理日志装饰器"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            logger = get_struct_logger(logger_name or func.__module__)
            
            try:
                return func(*args, **kwargs)
            except exception_type as e:
                # 记录特定类型的异常
                logger.log_exception(e, {
                    "function": func.__name__,
                    "exception_type": exception_type.__name__,
                    "args": args,
                    "kwargs": kwargs
                })
                raise
        
        return wrapper
    return decorator


def create_logger_context(operation: str, **context):
    """创建日志上下文"""
    logger = get_struct_logger("context")
    return LogContext(logger, operation, **context)


def log_with_context(operation: str, logger_name: str = None, **context):
    """带上下文的日志装饰器"""
    return log_context(operation, get_struct_logger(logger_name or "context"), **context)
