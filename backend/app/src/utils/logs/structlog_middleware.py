"""
Structlog 中间件 - 阿里巴巴标准格式

基于 structlog 的 FastAPI 中间件，提供请求日志记录、性能监控和异常追踪。
"""

import time
import uuid
from typing import Callable, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from .structlog_config import get_struct_logger, set_request_context, clear_request_context


class StructlogMiddleware(BaseHTTPMiddleware):
    """Structlog 请求日志中间件"""
    
    def __init__(self, app, enable_request_logging: bool = True, 
                 enable_performance_logging: bool = True,
                 enable_response_logging: bool = True):
        super().__init__(app)
        self.enable_request_logging = enable_request_logging
        self.enable_performance_logging = enable_performance_logging
        self.enable_response_logging = enable_response_logging
        self.logger = get_struct_logger("api")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求和响应"""
        # 生成请求ID和追踪ID
        request_id = str(uuid.uuid4())
        trace_id = str(uuid.uuid4())
        
        # 设置请求上下文
        set_request_context(request_id=request_id, trace_id=trace_id)
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 记录请求信息
        if self.enable_request_logging:
            await self._log_request(request, request_id, trace_id)
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = (time.time() - start_time) * 1000  # 转换为毫秒
            
            # 记录响应信息
            if self.enable_response_logging:
                await self._log_response(request, response, process_time, request_id, trace_id)
            
            # 记录性能指标
            if self.enable_performance_logging:
                await self._log_performance(request, response, process_time, request_id, trace_id)
            
            return response
            
        except Exception as e:
            # 计算处理时间
            process_time = (time.time() - start_time) * 1000
            
            # 记录异常
            await self._log_exception(request, e, process_time, request_id, trace_id)
            
            # 重新抛出异常
            raise
        
        finally:
            # 清除请求上下文
            clear_request_context()
    
    async def _log_request(self, request: Request, request_id: str, trace_id: str):
        """记录请求信息"""
        # 获取请求头
        headers = dict(request.headers)
        
        # 获取查询参数
        query_params = dict(request.query_params)
        
        # 获取请求体（如果是POST/PUT请求）
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    body = body.decode('utf-8')
            except Exception:
                body = "无法读取请求体"
        
        # 记录请求日志
        self.logger.log_api_request(
            method=request.method,
            path=str(request.url.path),
            params=query_params,
            headers=headers,
            body=body,
            request_id=request_id,
            trace_id=trace_id
        )
    
    async def _log_response(self, request: Request, response: Response, 
                           process_time: float, request_id: str, trace_id: str):
        """记录响应信息"""
        # 获取响应头
        response_headers = dict(response.headers)
        
        # 获取响应体（如果是JSON响应）
        response_body = None
        if hasattr(response, 'body') and response.body:
            try:
                response_body = response.body.decode('utf-8')
            except Exception:
                response_body = "无法读取响应体"
        
        # 记录响应日志
        self.logger.log_api_response(
            status_code=response.status_code,
            response_data=response_body,
            duration=process_time,
            request_id=request_id,
            trace_id=trace_id
        )
    
    async def _log_performance(self, request: Request, response: Response, 
                              process_time: float, request_id: str, trace_id: str):
        """记录性能指标"""
        performance_data = {
            "method": request.method,
            "path": str(request.url.path),
            "status_code": response.status_code,
            "process_time_ms": process_time,
            "request_id": request_id,
            "trace_id": trace_id
        }
        
        # 记录性能日志
        self.logger.log_performance(
            operation=f"{request.method} {request.url.path}",
            duration=process_time,
            **performance_data
        )
    
    async def _log_exception(self, request: Request, exception: Exception, 
                            process_time: float, request_id: str, trace_id: str):
        """记录异常信息"""
        exception_data = {
            "method": request.method,
            "path": str(request.url.path),
            "query_params": dict(request.query_params),
            "process_time_ms": process_time,
            "request_id": request_id,
            "trace_id": trace_id
        }
        
        # 记录异常日志
        self.logger.log_exception(exception, **exception_data)


class BusinessLoggingMiddleware(BaseHTTPMiddleware):
    """业务日志中间件"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = get_struct_logger("business")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理业务日志"""
        # 记录业务操作开始
        self.logger.log_business_operation(
            operation="api_request",
            entity_type="http_request",
            entity_id=str(uuid.uuid4()),
            method=request.method,
            path=str(request.url.path),
            client_ip=request.client.host if request.client else None
        )
        
        try:
            response = await call_next(request)
            
            # 记录业务操作完成
            self.logger.log_business_operation(
                operation="api_response",
                entity_type="http_response",
                entity_id=str(uuid.uuid4()),
                status_code=response.status_code,
                method=request.method,
                path=str(request.url.path)
            )
            
            return response
            
        except Exception as e:
            # 记录业务操作失败
            self.logger.log_business_operation(
                operation="api_error",
                entity_type="http_error",
                entity_id=str(uuid.uuid4()),
                error=str(e),
                method=request.method,
                path=str(request.url.path)
            )
            raise


class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    """性能监控中间件"""
    
    def __init__(self, app, slow_request_threshold: float = 1000.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold  # 毫秒
        self.logger = get_struct_logger("performance")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理性能监控"""
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # 计算处理时间
            process_time = (time.time() - start_time) * 1000
            
            # 记录慢请求
            if process_time > self.slow_request_threshold:
                self.logger.warning(
                    f"慢请求检测: {request.method} {request.url.path}",
                    business_data={
                        "type": "slow_request",
                        "method": request.method,
                        "path": str(request.url.path),
                        "process_time_ms": process_time,
                        "threshold_ms": self.slow_request_threshold
                    },
                    duration=process_time
                )
            
            return response
            
        except Exception as e:
            # 计算处理时间
            process_time = (time.time() - start_time) * 1000
            
            # 记录异常性能
            self.logger.error(
                f"请求异常: {request.method} {request.url.path}",
                business_data={
                    "type": "request_exception",
                    "method": request.method,
                    "path": str(request.url.path),
                    "process_time_ms": process_time,
                    "error": str(e)
                },
                duration=process_time
            )
            raise


class SecurityLoggingMiddleware(BaseHTTPMiddleware):
    """安全日志中间件"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = get_struct_logger("security")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理安全日志"""
        # 检查可疑请求
        await self._check_suspicious_request(request)
        
        try:
            response = await call_next(request)
            
            # 记录安全事件
            await self._log_security_event(request, response)
            
            return response
            
        except Exception as e:
            # 记录安全异常
            await self._log_security_exception(request, e)
            raise
    
    async def _check_suspicious_request(self, request: Request):
        """检查可疑请求"""
        suspicious_indicators = []
        
        # 检查请求头
        user_agent = request.headers.get("user-agent", "")
        if not user_agent or len(user_agent) < 10:
            suspicious_indicators.append("可疑的User-Agent")
        
        # 检查请求路径
        path = str(request.url.path)
        if any(pattern in path.lower() for pattern in ["../", "..\\", "admin", "config"]):
            suspicious_indicators.append("可疑的请求路径")
        
        # 检查查询参数
        query_params = dict(request.query_params)
        if any(key.lower() in ["password", "token", "key"] for key in query_params.keys()):
            suspicious_indicators.append("敏感信息在URL中")
        
        # 记录可疑请求
        if suspicious_indicators:
            self.logger.warning(
                f"可疑请求检测: {request.method} {request.url.path}",
                business_data={
                    "type": "suspicious_request",
                    "method": request.method,
                    "path": path,
                    "indicators": suspicious_indicators,
                    "client_ip": request.client.host if request.client else None,
                    "user_agent": user_agent
                }
            )
    
    async def _log_security_event(self, request: Request, response: Response):
        """记录安全事件"""
        # 记录认证失败
        if response.status_code == 401:
            self.logger.warning(
                f"认证失败: {request.method} {request.url.path}",
                business_data={
                    "type": "authentication_failure",
                    "method": request.method,
                    "path": str(request.url.path),
                    "status_code": response.status_code,
                    "client_ip": request.client.host if request.client else None
                }
            )
        
        # 记录权限拒绝
        if response.status_code == 403:
            self.logger.warning(
                f"权限拒绝: {request.method} {request.url.path}",
                business_data={
                    "type": "authorization_failure",
                    "method": request.method,
                    "path": str(request.url.path),
                    "status_code": response.status_code,
                    "client_ip": request.client.host if request.client else None
                }
            )
    
    async def _log_security_exception(self, request: Request, exception: Exception):
        """记录安全异常"""
        self.logger.error(
            f"安全异常: {request.method} {request.url.path}",
            business_data={
                "type": "security_exception",
                "method": request.method,
                "path": str(request.url.path),
                "error": str(exception),
                "client_ip": request.client.host if request.client else None
            }
        )
