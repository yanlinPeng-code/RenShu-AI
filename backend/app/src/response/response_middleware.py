"""
响应中间件

提供统一的响应处理中间件，支持请求ID生成、链路追踪等功能。
"""

import uuid
import time
from typing import Callable, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from .response_factory import response_factory
from app.src.response.exception.exceptions import APIException
from .response_models import BaseResponse


class ResponseMiddleware(BaseHTTPMiddleware):
    """响应处理中间件"""

    def __init__(self, app, enable_tracing: bool = True, enable_request_id: bool = True):
        super().__init__(app)
        self.enable_tracing = enable_tracing
        self.enable_request_id = enable_request_id

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求和响应"""
        # 生成请求ID
        request_id = self._generate_request_id() if self.enable_request_id else None

        # 获取客户端IP地址
        client_ip = self._get_client_ip(request)

        # 记录请求开始时间
        start_time = time.time()

        # 将ID添加到请求状态中
        request.state.request_id = request_id
        request.state.client_ip = client_ip

        try:
            # 处理请求
            response = await call_next(request)

            # 处理响应
            if isinstance(response, JSONResponse):
                # 明确的JSONResponse
                response = await self._process_json_response(response, request_id, client_ip)
            else:
                print("Response is not JSONResponse")
                # 对于非JSON响应，我们也确保添加必要的头部信息
                response = await self._process_general_response(response, request_id, client_ip)

            return response

        except APIException as e:
            # 处理API异常
            error_response = response_factory.from_exception(e, request_id, client_ip)
            return JSONResponse(
                status_code=e.code,
                content=error_response.dict()
            )
        except Exception as e:
            # 处理其他异常
            error_response = response_factory.error(
                code=500,
                message="服务器内部错误",
                error_code="INTERNAL_ERROR",
                details={"exception": str(e)},
                retryable=False,
                request_id=request_id,
                host_id=client_ip
            )
            return JSONResponse(
                status_code=500,
                content=error_response.dict()
            )
        finally:
            # 记录处理时间
            process_time = time.time() - start_time
            if hasattr(request.state, 'request_id'):
                print(f"Request {request.state.request_id} processed in {process_time:.3f}s")

    def _generate_request_id(self) -> str:
        """生成请求ID"""
        return str(uuid.uuid4())

    def _get_client_ip(self, request: Request) -> Optional[str]:
        """获取客户端IP地址"""
        # 尝试从不同的头部获取IP地址
        if request.client and request.client.host:
            return request.client.host

        # 如果没有request.client，尝试从头部获取
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return None

    async def _process_json_response(self, response: Response,
                                   request_id: Optional[str],
                                   client_ip: Optional[str]) -> Response:
        """处理JSON响应"""
        try:
            # 获取响应体内容
            if hasattr(response, 'body') and response.body:
                content = response.body.decode('utf-8')
            else:
                # 如果没有body属性，可能需要特殊处理
                return response

            import json
            data = json.loads(content)

            # 确保所有响应都包含RequestId和HostId
            if isinstance(data, dict):
                # 更新或添加RequestId字段
                # 如果当前RequestId为空或不存在，则使用生成的request_id
                if not data.get('RequestId'):
                    data['RequestId'] = request_id or ""

                # 更新或添加HostId字段
                # 如果当前HostId为null或不存在，则使用client_ip
                if 'HostId' not in data or data['HostId'] is None:
                    data['HostId'] = client_ip

                # 重新编码响应
                response.body = json.dumps(data, ensure_ascii=False).encode('utf-8')
                # 更新Content-Length头部
                response.headers["content-length"] = str(len(response.body))

        except (json.JSONDecodeError, UnicodeDecodeError):
            # 如果解析失败，保持原响应不变
            pass

        return response

    async def _process_general_response(self, response: Response,
                                      request_id: Optional[str],
                                      client_ip: Optional[str]) -> Response:
        """处理通用响应"""
        # 为所有响应添加自定义头部
        if request_id:
            response.headers['X-Request-ID'] = request_id
        if client_ip:
            response.headers['X-Client-IP'] = client_ip

        return response


class RequestContextMiddleware:
    """请求上下文中间件"""

    def __init__(self):
        self._context = {}

    def set_request_id(self, request_id: str):
        """设置请求ID"""
        self._context['request_id'] = request_id

    def get_request_id(self) -> Optional[str]:
        """获取请求ID"""
        return self._context.get('request_id')

    def set_client_ip(self, client_ip: str):
        """设置客户端IP"""
        self._context['client_ip'] = client_ip

    def get_client_ip(self) -> Optional[str]:
        """获取客户端IP"""
        return self._context.get('client_ip')

    def clear(self):
        """清除上下文"""
        self._context.clear()


# 全局请求上下文实例
request_context = RequestContextMiddleware()