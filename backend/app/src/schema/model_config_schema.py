from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

from sqlalchemy import Column, JSON, Text
from sqlmodel import SQLModel, Field, Relationship, Index
from pydantic import field_validator, ConfigDict

# ==================== DTO / Schema ====================

# --- 管理员：供应商管理 ---

class ModelProviderCreate(SQLModel):
    """创建供应商（管理员）"""
    name: str = Field(max_length=50, description="供应商标识")
    label: str = Field(max_length=100, description="显示名称")
    description: Optional[str] = None
    icon: Optional[str] = None
    icon_background: Optional[str] = "#FFFFFF"
    default_base_url: Optional[str] = None
    supported_model_types: List[str] = Field(default=["chat"])
    help_url: Optional[str] = None
    position: int = 0


class ModelProviderUpdate(SQLModel):
    """更新供应商（管理员）"""
    label: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    icon_background: Optional[str] = None
    default_base_url: Optional[str] = None
    supported_model_types: Optional[List[str]] = None
    help_url: Optional[str] = None
    is_enabled: Optional[bool] = None
    position: Optional[int] = None


# --- 管理员：模型配置管理 ---

class ModelConfigCreate(SQLModel):
    """创建模型配置（管理员）"""
    provider_id: UUID
    model_name: str = Field(max_length=100)
    label: str = Field(max_length=100)
    description: Optional[str] = None
    model_type: str = "chat"
    features: List[str] = Field(default=[])
    context_window: int = 4096
    max_output_tokens: int = 4096
    default_temperature: float = 0.7
    default_top_p: float = 1.0
    default_max_tokens: int = 4096
    default_parameters: Dict[str, Any] = Field(default={})
    attributes: Dict[str, Any] = Field(default={})
    pricing: Optional[Dict[str, Any]] = None
    position: int = 0


class ModelConfigUpdate(SQLModel):
    """更新模型配置（管理员）"""
    label: Optional[str] = None
    description: Optional[str] = None
    model_type: Optional[str] = None
    features: Optional[List[str]] = None
    context_window: Optional[int] = None
    max_output_tokens: Optional[int] = None
    default_temperature: Optional[float] = None
    default_top_p: Optional[float] = None
    default_max_tokens: Optional[int] = None
    default_parameters: Optional[Dict[str, Any]] = None
    attributes: Optional[Dict[str, Any]] = None
    pricing: Optional[Dict[str, Any]] = None
    is_enabled: Optional[bool] = None
    position: Optional[int] = None


# --- 用户：模型配置管理 ---

class UserModelConfigCreate(SQLModel):
    """创建用户模型配置"""
    provider_id: UUID = Field(description="供应商ID")
    model_config_id: Optional[UUID] = Field(default=None, description="内置模型ID（二选一）")
    custom_model_name: Optional[str] = Field(default=None, description="自定义模型名称（二选一）")
    api_key: str = Field(description="API密钥（必填）")
    base_url: Optional[str] = Field(default=None, description="自定义API地址")
    custom_temperature: Optional[float] = None
    custom_top_p: Optional[float] = None
    custom_max_tokens: Optional[int] = None
    custom_parameters: Dict[str, Any] = Field(default={})
    alias: Optional[str] = None
    is_default: bool = False


class UserModelConfigUpdate(SQLModel):
    """更新用户模型配置"""
    model_config_id: Optional[UUID] = None
    custom_model_name: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    custom_temperature: Optional[float] = None
    custom_top_p: Optional[float] = None
    custom_max_tokens: Optional[int] = None
    custom_parameters: Optional[Dict[str, Any]] = None
    alias: Optional[str] = None
    is_default: Optional[bool] = None
    is_enabled: Optional[bool] = None


# --- 响应模型 ---

class ModelProviderResponse(SQLModel):
    """供应商响应（给用户看的，不含敏感信息）"""
    id: UUID
    name: str
    label: str
    description: Optional[str]
    icon: Optional[str]
    icon_background: Optional[str]
    default_base_url: Optional[str]
    supported_model_types: List[str]
    help_url: Optional[str]
    is_builtin: bool


class ModelConfigResponse(SQLModel):
    """模型配置响应"""
    id: UUID
    model_name: str
    label: str
    description: Optional[str]
    model_type: str
    features: List[str]
    context_window: int
    max_output_tokens: int
    default_temperature: float
    default_top_p: float
    default_max_tokens: int
    pricing: Optional[Dict[str, Any]]


class UserModelConfigResponse(SQLModel):
    """用户模型配置响应"""
    id: UUID
    provider_id: UUID
    provider_name: Optional[str] = None
    provider_label: Optional[str] = None
    model_config_id: Optional[UUID]
    model_name: Optional[str] = None
    model_label: Optional[str] = None
    custom_model_name: Optional[str]
    has_api_key: bool = True  # 不返回实际key，只返回是否已配置
    base_url: Optional[str]
    alias: Optional[str]
    is_default: bool
    is_enabled: bool
