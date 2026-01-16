"""
响应中间件

提供统一的响应处理中间件，支持请求ID生成、链路追踪等功能。
使用纯 ASGI 中间件实现，避免 BaseHTTPMiddleware 的事务问题。
"""

import uuid
import time
from typing import Optional
from starlette.types import ASGIApp, Receive, Send, Scope, Message


class ResponseMiddleware:
    """
    纯 ASGI 响应处理中间件

    优势：
    1. 不会干扰 FastAPI 依赖注入的生命周期
    2. 事务在响应完全发送后才提交
    3. 更好的性能（无额外的响应体缓冲）
    """

    def __init__(self, app: ASGIApp, enable_tracing: bool = True, enable_request_id: bool = True):
        self.app = app
        self.enable_tracing = enable_tracing
        self.enable_request_id = enable_request_id

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # 只处理 HTTP 请求
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 生成请求ID和获取客户端IP
        request_id = str(uuid.uuid4()) if self.enable_request_id else None
        client_ip = self._get_client_ip(scope)
        start_time = time.time()

        # 将信息存储到 scope 的 state 中
        if "state" not in scope:
            scope["state"] = {}
        scope["state"]["request_id"] = request_id
        scope["state"]["client_ip"] = client_ip

        async def send_wrapper(message: Message) -> None:
            """包装 send 函数，添加响应头"""
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                if request_id:
                    headers.append((b"x-request-id", request_id.encode()))
                if client_ip:
                    headers.append((b"x-client-ip", client_ip.encode()))
                message = {**message, "headers": headers}

            elif message["type"] == "http.response.body":
                # 响应体发送完成后记录处理时间
                if not message.get("more_body", False):
                    process_time = time.time() - start_time
                    print(f"Request {request_id} processed in {process_time:.3f}s")

            await send(message)

        await self.app(scope, receive, send_wrapper)

    def _get_client_ip(self, scope: Scope) -> Optional[str]:
        """从 scope 获取客户端IP"""
        # 从 client 获取
        client = scope.get("client")
        if client:
            return client[0]

        # 从 headers 获取
        headers = dict(scope.get("headers", []))
        forwarded = headers.get(b"x-forwarded-for")
        if forwarded:
            return forwarded.decode().split(",")[0].strip()

        real_ip = headers.get(b"x-real-ip")
        if real_ip:
            return real_ip.decode()

        return None


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