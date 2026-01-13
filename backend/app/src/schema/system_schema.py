from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from sqlmodel import SQLModel


# class SystemConfigCreate(BaseModel):
#     """系统配置创建模型"""
#
#     config_key: str = Field(description="配置键")
#     config_value: Optional[str] = Field(default=None, description="配置值")
#     config_type: str = Field(default="string", description="配置类型")
#     description: Optional[str] = Field(default=None, description="配置描述")
#
#     @field_validator('config_type')
#     def validate_config_type(cls, v):
#         """验证配置类型"""
#         allowed_types = ['string', 'number', 'boolean', 'json']
#         if v not in allowed_types:
#             raise ValueError(f'配置类型必须是以下之一: {", ".join(allowed_types)}')
#         return v
#
#     model_config = ConfigDict(populate_by_name=True)
#
#
# class SystemConfigUpdate(BaseModel):
#     """系统配置更新模型"""
#
#     config_value: Optional[str] = Field(default=None, description="配置值")
#     config_type: Optional[str] = Field(default=None, description="配置类型")
#     description: Optional[str] = Field(default=None, description="配置描述")
#     is_active: Optional[bool] = Field(default=None, description="是否启用")
#
#     @field_validator('config_type')
#     def validate_config_type(cls, v):
#         """验证配置类型"""
#         if v is not None:
#             allowed_types = ['string', 'number', 'boolean', 'json']
#             if v not in allowed_types:
#                 raise ValueError(f'配置类型必须是以下之一: {", ".join(allowed_types)}')
#         return v
#
#     model_config = ConfigDict(populate_by_name=True)

class SystemConfigCreate(SQLModel):
    """系统配置创建模型"""

    config_key: str = Field(description="配置键")
    config_value: Optional[str] = Field(default=None, description="配置值")
    config_type: str = Field(default="string", description="配置类型")
    description: Optional[str] = Field(default=None, description="配置描述")

    @field_validator('config_type')
    def validate_config_type(cls, v):
        """验证配置类型"""
        allowed_types = ['string', 'number', 'boolean', 'json']
        if v not in allowed_types:
            raise ValueError(f'配置类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    model_config = ConfigDict(populate_by_name=True)


class SystemConfigUpdate(SQLModel):
    """系统配置更新模型"""

    config_value: Optional[str] = Field(default=None, description="配置值")
    config_type: Optional[str] = Field(default=None, description="配置类型")
    description: Optional[str] = Field(default=None, description="配置描述")
    is_active: Optional[bool] = Field(default=None, description="是否启用")

    @field_validator('config_type')
    def validate_config_type(cls, v):
        """验证配置类型"""
        if v is not None:
            allowed_types = ['string', 'number', 'boolean', 'json']
            if v not in allowed_types:
                raise ValueError(f'配置类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    model_config = ConfigDict(populate_by_name=True)