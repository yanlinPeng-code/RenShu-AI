"""
响应工具函数 - 阿里巴巴标准格式

提供便捷的响应创建函数，简化API开发，符合阿里巴巴API标准。
"""

from typing import TypeVar, Dict, Any, List

from .exception.exceptions import APIException
from .response_factory import response_factory
from .response_models import ValidationErrorDetail
from .response_codes import ResponseCode


T = TypeVar('T')


def success(data: T = None, message: str = "请求成功", code: str = "Success",
            request_id: str = None, host_id: str = None):
    """创建成功响应"""
    # 确保 code 是字符串类型
    if not isinstance(code, str):
        code = str(code)
        
    return response_factory.success(
        data=data,
        message=message,
        code=code,
        request_id=request_id,
        host_id=host_id
    )


def error(code: str, message: str, error_code: str = None,
          details: Dict[str, Any] = None, retryable: bool = False,
          request_id: str = None, host_id: str = None):
    """创建错误响应"""
    # 确保 code 是字符串类型
    if not isinstance(code, str):
        code = str(code)
        
    return response_factory.error(
        code=code,
        message=message,
        error_code=error_code,
        details=details,
        retryable=retryable,
        request_id=request_id,
        host_id=host_id
    )


def paginated(items: List[T], page: int, page_size: int, total: int,
              message: str = "查询成功", request_id: str = None, 
              host_id: str = None):
    """创建分页响应"""
    return response_factory.paginated(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        message=message,
        request_id=request_id,
        host_id=host_id
    )


def validation_error(validation_errors: List[ValidationErrorDetail],
                    message: str = "参数验证失败", request_id: str = None, 
                    host_id: str = None):
    """创建验证错误响应"""
    return response_factory.validation_error(
        validation_errors=validation_errors,
        message=message, request_id=request_id, host_id=host_id
    )


def from_response_code(response_code: ResponseCode, data: T = None,message: str = "请求成功",
                      details: Dict[str, Any] = None, request_id: str = None,
                      host_id: str = None):
    """从响应码创建响应"""
    return response_factory.from_response_code(
        response_code=response_code,
        data=data,
        message=message,
        details=details,
        request_id=request_id,
        host_id=host_id
    )


def from_exception(exception: APIException, request_id: str = None,
                  host_id: str = None):
    """从异常创建响应"""
    return response_factory.from_exception(
        exception=exception,
        request_id=request_id,
        host_id=host_id
    )


# 便捷的响应码函数 - 阿里巴巴标准格式
def success_200(data: T = None, message: str = "请求成功", request_id: str = None, host_id: str = None):
    """200 成功响应"""
    return from_response_code(ResponseCode.SUCCESS, data, message=message, request_id=request_id, host_id=host_id)


def created_201(data: T = None, message: str = "创建成功", request_id: str = None, host_id: str = None):
    """201 创建成功响应"""
    return from_response_code(ResponseCode.CREATED, data, message=message, request_id=request_id, host_id=host_id)


def bad_request_400(message: str = "请求错误", details: Dict[str, Any] = None, request_id: str = None, host_id: str = None):
    """400 请求错误响应"""
    return from_response_code(ResponseCode.BAD_REQUEST, details=details, message=message, request_id=request_id, host_id=host_id)


def unauthorized_401(message: str = "未授权", details: Dict[str, Any] = None, request_id: str = None, host_id: str = None):
    """401 未授权响应"""
    return from_response_code(ResponseCode.UNAUTHORIZED, details=details, message=message, request_id=request_id, host_id=host_id)


def forbidden_403(message: str = "禁止访问", details: Dict[str, Any] = None, request_id: str = None, host_id: str = None):
    """403 禁止访问响应"""
    return from_response_code(ResponseCode.FORBIDDEN, details=details, message=message, request_id=request_id, host_id=host_id)


def not_found_404(message: str = "未找到", details: Dict[str, Any] = None, request_id: str = None, host_id: str = None):
    """404 未找到响应"""
    return from_response_code(ResponseCode.NOT_FOUND, details=details, message=message, request_id=request_id, host_id=host_id)


def validation_error_422(validation_errors: List[ValidationErrorDetail],
                        message: str = "参数验证失败", request_id: str = None, host_id: str = None):
    """422 参数验证错误响应"""
    return validation_error(validation_errors, message, request_id, host_id)


def internal_error_500(message: str = "服务器内部错误", details: Dict[str, Any] = None, request_id: str = None, host_id: str = None):
    """500 服务器内部错误响应"""
    return from_response_code(ResponseCode.INTERNAL_ERROR, details=details, message=message, request_id=request_id, host_id=host_id)
