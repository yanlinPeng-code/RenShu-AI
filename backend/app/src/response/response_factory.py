"""
响应工厂 - 阿里巴巴标准格式

提供统一的响应创建接口，支持多种响应类型和策略模式，符合阿里巴巴API标准。
"""

from typing import TypeVar, Dict, Any, List, Union
from abc import ABC, abstractmethod
from .response_models import (
    BaseResponse, SuccessResponse, ErrorResponse,
    ValidationErrorResponse, ValidationErrorDetail, PaginatedResponse
)
from .response_codes import ResponseCode
from app.src.response.exception.exceptions import APIException


T = TypeVar('T')


class ResponseStrategy(ABC):
    """响应策略接口"""
    
    @abstractmethod
    def create_response(self, **kwargs) -> BaseResponse:
        """创建响应"""
        pass


class SuccessResponseStrategy(ResponseStrategy):
    """成功响应策略 - 阿里巴巴标准格式"""
    
    def create_response(self, data: T = None, code: str = "Success", 
                       message: str = "请求成功", request_id: str = None, 
                       host_id: str = None) -> SuccessResponse[T]:
        """创建成功响应"""
        return SuccessResponse.create(
            data=data,
            code=code,
            message=message,
            request_id=request_id,
            host_id=host_id
        )


class ErrorResponseStrategy(ResponseStrategy):
    """错误响应策略 - 阿里巴巴标准格式"""
    
    def create_response(self, code: str, message: str, error_code: str = None,
                       details: Dict[str, Any] = None, retryable: bool = False, 
                       request_id: str = None, host_id: str = None) -> ErrorResponse:
        """创建错误响应"""
        # 确保 code 是字符串类型
        if not isinstance(code, str):
            code = str(code)
            
        return ErrorResponse.create(
            code=code,
            message=message,
            error_code=error_code,
            details=details,
            retryable=retryable,
            request_id=request_id,
            host_id=host_id
        )


class PaginatedResponseStrategy(ResponseStrategy):
    """分页响应策略 - 阿里巴巴标准格式"""

    def create_response(self, items: List[T], page: int, page_size: int, total: int,
                       message: str = "查询成功", request_id: str = None,
                       host_id: str = None) -> PaginatedResponse[T]:
        """创建分页响应"""
        return PaginatedResponse.create(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            message=message,
            request_id=request_id,
            host_id=host_id
        )


class ValidationErrorResponseStrategy(ResponseStrategy):
    """验证错误响应策略 - 阿里巴巴标准格式"""
    
    def create_response(self, validation_errors: List[ValidationErrorDetail],
                       message: str = "参数验证失败", request_id: str = None, 
                       host_id: str = None) -> ValidationErrorResponse:
        """创建验证错误响应"""
        return ValidationErrorResponse.create(
            validation_errors=validation_errors,
            message=message,
            request_id=request_id,
            host_id=host_id
        )


class ResponseFactory:
    """响应工厂"""
    
    def __init__(self):
        self._strategies = {
            'success': SuccessResponseStrategy(),
            'error': ErrorResponseStrategy(),
            'paginated': PaginatedResponseStrategy(),
            'validation_error': ValidationErrorResponseStrategy()
        }
    
    def success(self, data: T = None, code: str = "Success", message: str = "请求成功",
                request_id: str = None, host_id: str = None) -> SuccessResponse[T]:
        """创建成功响应"""
        # 确保 code 是字符串类型
        if not isinstance(code, str):
            code = str(code)
            
        return self._strategies['success'].create_response(
            data=data, code=code, message=message,
            request_id=request_id, host_id=host_id
        )
    
    def error(self, code: str, message: str, error_code: str = None,
              details: Dict[str, Any] = None, retryable: bool = False, 
              request_id: str = None, host_id: str = None) -> ErrorResponse:
        """创建错误响应"""
        # 确保 code 是字符串类型
        if not isinstance(code, str):
            code = str(code)
            
        return self._strategies['error'].create_response(
            code=code, message=message, error_code=error_code, 
            details=details, retryable=retryable,
            request_id=request_id, host_id=host_id
        )
    
    def paginated(self, items: List[T], page: int, page_size: int, total: int,
                  message: str = "查询成功", request_id: str = None, 
                  host_id: str = None) -> PaginatedResponse[T]:
        """创建分页响应"""
        return self._strategies['paginated'].create_response(
            items=items, page=page, page_size=page_size, total=total,
            message=message, request_id=request_id, host_id=host_id
        )
    
    def validation_error(self, validation_errors: List[ValidationErrorDetail],
                        message: str = "参数验证失败", request_id: str = None, 
                        host_id: str = None) -> ValidationErrorResponse:
        """创建验证错误响应"""
        return self._strategies['validation_error'].create_response(
            validation_errors=validation_errors,
            message=message, request_id=request_id, host_id=host_id
        )
    
    def from_exception(self, exception: APIException, request_id: str = None,
                      host_id: str = None) -> ErrorResponse:
        """从异常创建错误响应"""
        return self.error(
            code=exception.code,
            message=exception.message,
            error_code=exception.error_code,
            details=exception.details,
            retryable=exception.retryable,
            request_id=request_id,
            host_id=host_id
        )
    
    def from_response_code(self, response_code: ResponseCode, data: T = None,message: str = "请求成功",
                          details: Dict[str, Any] = None, request_id: str = None,
                          host_id: str = None) -> Union[SuccessResponse[T], ErrorResponse]:
        """从响应码创建响应"""
        code_info = response_code._code_info

        if response_code.http_status < 400:
            return self.success(
                data=data if data is not None else details,
                code=code_info.code,
                message=message,
                request_id=request_id,
                host_id=host_id
            )
        else:
            return self.error(
                code=code_info.code,
                message=message,
                details=details,
                retryable=code_info.retryable,
                request_id=request_id,
                host_id=host_id
            )


# 全局响应工厂实例
response_factory = ResponseFactory()
