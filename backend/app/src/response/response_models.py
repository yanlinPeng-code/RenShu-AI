"""
响应数据模型 - 阿里巴巴标准格式

提供符合阿里巴巴API标准的响应数据结构，支持泛型和分页。
"""

from typing import TypeVar, Generic, Optional, Union, List, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field

from app.src.utils.paginator.models import PaginatedData, PaginationInfo

T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """基础响应模型 - 阿里巴巴标准格式"""

    RequestId: str = Field(description="请求唯一标识符")
    Code: str = Field(description="业务状态码")
    Message: str = Field(description="状态码描述")
    HostId: Optional[str] = Field(default=None, description="请求访问的站点ID")
    Data: Optional[T] = Field(default=None, description="返回的数据内容")
    Success: Optional[bool] = Field(default=None, description="是否成功（兼容字段）")

    # Pydantic V2 配置（替换原有的 Config 类）
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        },
        # 移除 fields 配置（V2 已废弃，且你的字段名与JSON输出一致，无需别名）
        "from_attributes": True,  # 支持从ORM对象/普通类实例创建模型
        "populate_by_name": True  # 允许通过字段别名赋值
    }


class SuccessResponse(BaseResponse[T]):
    """成功响应模型 - 阿里巴巴标准格式"""

    Success: bool = Field(default=True, description="是否成功")
    Code: str = Field(default="Success", description="业务状态码")

    @classmethod
    def create(cls, data: T = None, code: str = "Success", message: str = "请求成功",
               request_id: str = None, host_id: str = None) -> 'SuccessResponse[T]':
        """创建成功响应"""
        return cls(
            RequestId=request_id or "",
            Code=code,
            Message=message,
            HostId=host_id,
            Data=data,
            Success=True
        )


class ErrorResponse(BaseResponse[None]):
    """错误响应模型 - 阿里巴巴标准格式"""

    Success: bool = Field(default=False, description="是否成功")
    Code: str = Field(description="业务状态码")
    ErrorCode: Optional[str] = Field(default=None, description="错误代码")
    Details: Optional[Dict[str, Any]] = Field(default=None, description="错误详情")
    Retryable: bool = Field(default=False, description="是否可重试")

    @classmethod
    def create(cls, code: str, message: str, error_code: str = None,
               details: Dict[str, Any] = None, retryable: bool = False,
               request_id: str = None, host_id: str = None) -> 'ErrorResponse':
        """创建错误响应"""
        return cls(
            RequestId=request_id or "",
            Code=code,
            Message=message,
            HostId=host_id,
            Data=None,
            Success=False,
            ErrorCode=error_code,
            Details=details,
            Retryable=retryable
        )


class PaginatedResponse(BaseResponse[PaginatedData[T]]):
    """分页响应模型 - 阿里巴巴标准格式"""

    Success: bool = Field(default=True, description="是否成功")
    Code: str = Field(default="Success", description="业务状态码")

    @classmethod
    def create(cls, items: List[T], page: int, page_size: int, total: int,
               message: str = "查询成功", request_id: str = None,
               host_id: str = None) -> 'PaginatedResponse[T]':
        """创建分页响应"""
        pagination = PaginationInfo(
            page=page,
            page_size=page_size,
            total=total
        )

        paginated_data = PaginatedData(
            items=items,
            pagination=pagination
        )

        return cls(
            RequestId=request_id or "",
            Code="Success",
            Message=message,
            HostId=host_id,
            Data=paginated_data,
            Success=True
        )


class ValidationErrorDetail(BaseModel):
    """验证错误详情"""

    field: str = Field(description="字段名")
    message: str = Field(description="错误消息")
    value: Any = Field(description="错误值")

    # 确保value能被正确序列化
    model_config = {
        "arbitrary_types_allowed": True
    }


class ValidationErrorResponse(ErrorResponse):
    """验证错误响应 - 阿里巴巴标准格式"""

    ValidationErrors: List[ValidationErrorDetail] = Field(description="验证错误详情")

    @classmethod
    def create(cls, validation_errors: List[ValidationErrorDetail],
               message: str = "参数验证失败", request_id: str = None,
               host_id: str = None) -> 'ValidationErrorResponse':
        """创建验证错误响应"""
        return cls(
            RequestId=request_id or "",
            Code="ValidationError",
            Message=message,
            HostId=host_id,
            Data=None,
            Success=False,
            ValidationErrors=validation_errors
        )
