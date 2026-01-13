"""
响应码定义和注册系统 - 阿里巴巴标准格式

支持动态注册响应码，提供符合阿里巴巴API标准的响应码管理。
"""

from enum import Enum
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class ResponseCodeInfo:
    """响应码信息 - 阿里巴巴标准格式"""
    code: str  # 字符串类型的业务状态码
    message: str
    description: Optional[str] = None
    category: Optional[str] = None
    retryable: bool = False
    http_status: int = 200  # 对应的HTTP状态码


class ResponseCode(Enum):
    """标准响应码枚举 - 阿里巴巴标准格式"""
    
    # 成功类
    SUCCESS = ResponseCodeInfo("Success", "请求成功", "操作成功", "success", False, 200)
    CREATED = ResponseCodeInfo("Created", "创建成功", "资源创建成功", "success", False, 201)
    ACCEPTED = ResponseCodeInfo("Accepted", "已接受", "请求已接受", "success", False, 202)
    NO_CONTENT = ResponseCodeInfo("NoContent", "无内容", "操作成功但无返回内容", "success", False, 204)
    
    # 客户端错误类
    BAD_REQUEST = ResponseCodeInfo("BadRequest", "请求错误", "请求参数错误", "client_error", False, 400)
    UNAUTHORIZED = ResponseCodeInfo("Unauthorized", "未授权", "需要身份验证", "client_error", False, 401)
    FORBIDDEN = ResponseCodeInfo("Forbidden", "禁止访问", "没有权限访问", "client_error", False, 403)
    NOT_FOUND = ResponseCodeInfo("NotFound", "未找到", "资源不存在", "client_error", False, 404)
    METHOD_NOT_ALLOWED = ResponseCodeInfo("MethodNotAllowed", "方法不允许", "HTTP方法不被允许", "client_error", False, 405)
    CONFLICT = ResponseCodeInfo("Conflict", "冲突", "资源冲突", "client_error", False, 409)
    VALIDATION_ERROR = ResponseCodeInfo("ValidationError", "参数验证错误", "请求参数验证失败", "client_error", False, 422)
    TOO_MANY_REQUESTS = ResponseCodeInfo("TooManyRequests", "请求过多", "请求频率过高", "client_error", True, 429)
    
    # 服务器错误类
    INTERNAL_ERROR = ResponseCodeInfo("InternalError", "服务器内部错误", "服务器内部错误", "server_error", True, 500)
    BAD_GATEWAY = ResponseCodeInfo("BadGateway", "网关错误", "网关错误", "server_error", True, 502)
    SERVICE_UNAVAILABLE = ResponseCodeInfo("ServiceUnavailable", "服务不可用", "服务暂时不可用", "server_error", True, 503)
    GATEWAY_TIMEOUT = ResponseCodeInfo("GatewayTimeout", "网关超时", "网关超时", "server_error", True, 504)
    
    # 业务错误类
    BUSINESS_ERROR = ResponseCodeInfo("BusinessError", "业务错误", "业务逻辑错误", "business_error", False, 400)
    DATA_NOT_FOUND = ResponseCodeInfo("DataNotFound", "数据不存在", "请求的数据不存在", "business_error", False, 404)
    OPERATION_FAILED = ResponseCodeInfo("OperationFailed", "操作失败", "操作执行失败", "business_error", False, 400)
    INSUFFICIENT_PERMISSIONS = ResponseCodeInfo("InsufficientPermissions", "权限不足", "权限不足", "business_error", False, 403)
    
    # 阿里云常见错误码
    INVALID_PARAMETER = ResponseCodeInfo("InvalidParameter", "参数无效", "请求参数无效", "client_error", False, 400)
    INVALID_ACCESS_KEY_ID = ResponseCodeInfo("InvalidAccessKeyId", "AccessKeyId无效", "访问密钥ID无效", "client_error", False, 403)
    SIGNATURE_DOES_NOT_MATCH = ResponseCodeInfo("SignatureDoesNotMatch", "签名不匹配", "请求签名不匹配", "client_error", False, 403)
    INVALID_SECURITY_TOKEN = ResponseCodeInfo("InvalidSecurityToken", "安全令牌无效", "安全令牌无效", "client_error", False, 403)
    ACCESS_DENIED = ResponseCodeInfo("AccessDenied", "访问被拒绝", "访问被拒绝", "client_error", False, 403)
    RESOURCE_NOT_FOUND = ResponseCodeInfo("ResourceNotFound", "资源不存在", "指定的资源不存在", "client_error", False, 404)
    RESOURCE_ALREADY_EXISTS = ResponseCodeInfo("ResourceAlreadyExists", "资源已存在", "指定的资源已存在", "client_error", False, 409)
    QUOTA_EXCEEDED = ResponseCodeInfo("QuotaExceeded", "配额超限", "请求超出配额限制", "client_error", False, 429)
    RATE_LIMIT_EXCEEDED = ResponseCodeInfo("RateLimitExceeded", "请求频率超限", "请求频率超出限制", "client_error", True, 429)
    INTERNAL_ERROR_ALI = ResponseCodeInfo("InternalError", "内部错误", "服务器内部错误", "server_error", True, 500)
    SERVICE_UNAVAILABLE_ALI = ResponseCodeInfo("ServiceUnavailable", "服务不可用", "服务暂时不可用", "server_error", True, 503)
    THROTTLING = ResponseCodeInfo("Throttling", "请求被限流", "请求被限流", "client_error", True, 429)
    
    def __init__(self, code_info: ResponseCodeInfo):
        self._code_info = code_info
    
    @property
    def code(self) -> str:
        """获取响应码"""
        return self._code_info.code
    
    @property
    def message(self) -> str:
        """获取响应消息"""
        return self._code_info.message
    
    @property
    def description(self) -> Optional[str]:
        """获取描述"""
        return self._code_info.description
    
    @property
    def category(self) -> Optional[str]:
        """获取分类"""
        return self._code_info.category
    
    @property
    def retryable(self) -> bool:
        """是否可重试"""
        return self._code_info.retryable
    
    @property
    def http_status(self) -> int:
        """获取HTTP状态码"""
        return self._code_info.http_status


class ResponseCodeRegistry:
    """响应码注册表 - 阿里巴巴标准格式"""
    
    def __init__(self):
        self._codes: Dict[str, ResponseCodeInfo] = {}
        self._register_default_codes()
    
    def _register_default_codes(self):
        """注册默认响应码"""
        for code in ResponseCode:
            self._codes[code.code] = code._code_info
    
    def register(self, code: str, message: str, description: Optional[str] = None, 
                 category: Optional[str] = None, retryable: bool = False,
                 http_status: int = 200) -> None:
        """注册自定义响应码"""
        if code in self._codes:
            raise ValueError(f"响应码 {code} 已存在")
        
        self._codes[code] = ResponseCodeInfo(
            code=code,
            message=message,
            description=description,
            category=category,
            retryable=retryable,
            http_status=http_status
        )
    
    def get(self, code: str) -> Optional[ResponseCodeInfo]:
        """获取响应码信息"""
        return self._codes.get(code)
    
    def get_all(self) -> Dict[str, ResponseCodeInfo]:
        """获取所有响应码"""
        return self._codes.copy()
    
    def get_by_category(self, category: str) -> Dict[str, ResponseCodeInfo]:
        """根据分类获取响应码"""
        return {code: info for code, info in self._codes.items() 
                if info.category == category}


# 全局响应码注册表实例
response_code_registry = ResponseCodeRegistry()
