"""
API异常定义 - 阿里巴巴标准格式

提供标准化的异常处理机制，符合阿里巴巴API标准。
"""

from typing import Optional, Dict, Any


class APIException(Exception):
    """API基础异常 - 阿里巴巴标准格式"""
    
    def __init__(self, code: str, message: str, error_code: str = None, 
                 details: Dict[str, Any] = None, retryable: bool = False):
        self.code = code
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.retryable = retryable
        super().__init__(message)


class ValidationException(APIException):
    """参数验证异常"""
    
    def __init__(self, message: str = "参数验证失败", error_code: str = "ValidationError", 
                 details: Dict[str, Any] = None):
        super().__init__(
            code="ValidationError",
            message=message,
            error_code=error_code,
            details=details,
            retryable=False
        )


class BusinessException(APIException):
    """业务逻辑异常"""
    
    def __init__(self, message: str, error_code: str = None,
                 details: Dict[str, Any] = None, retryable: bool = False):
        super().__init__(
            code="BusinessError",
            message=message,
            error_code=error_code,
            details=details,
            retryable=retryable
        )


class AuthenticationException(APIException):
    """认证异常"""
    
    def __init__(self, message: str = "认证失败", error_code: str = "Unauthorized",
                 details: Dict[str, Any] = None):
        super().__init__(
            code="Unauthorized",
            message=message,
            error_code=error_code,
            details=details,
            retryable=False
        )


class AuthorizationException(APIException):
    """授权异常"""
    
    def __init__(self, message: str = "权限不足", error_code: str = "Forbidden",
                 details: Dict[str, Any] = None):
        super().__init__(
            code="Forbidden",
            message=message,
            error_code=error_code,
            details=details,
            retryable=False
        )


class ResourceNotFoundException(APIException):
    """资源不存在异常"""
    
    def __init__(self, message: str = "资源不存在", error_code: str = "NotFound",
                 details: Dict[str, Any] = None):
        super().__init__(
            code="NotFound",
            message=message,
            error_code=error_code,
            details=details,
            retryable=False
        )


class InternalServerException(APIException):
    """服务器内部异常"""
    
    def __init__(self, message: str = "服务器内部错误", error_code: str = "InternalError",
                 details: Dict[str, Any] = None, retryable: bool = True):
        super().__init__(
            code="InternalError",
            message=message,
            error_code=error_code,
            details=details,
            retryable=retryable
        )


class ExternalServiceException(APIException):
    """外部服务异常"""
    
    def __init__(self, message: str = "外部服务错误", error_code: str = "BadGateway",
                 details: Dict[str, Any] = None, retryable: bool = True):
        super().__init__(
            code="BadGateway",
            message=message,
            error_code=error_code,
            details=details,
            retryable=retryable
        )


class RateLimitException(APIException):
    """限流异常"""
    
    def __init__(self, message: str = "请求过于频繁", error_code: str = "TooManyRequests",
                 details: Dict[str, Any] = None, retry_after: int = 60):
        details = details or {}
        details['retry_after'] = retry_after
        super().__init__(
            code="TooManyRequests",
            message=message,
            error_code=error_code,
            details=details,
            retryable=True
        )
