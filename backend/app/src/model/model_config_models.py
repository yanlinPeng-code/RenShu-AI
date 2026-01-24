"""
模型配置数据模型

架构设计：
1. 静态元数据层 (System Layer)：仅管理员可维护，全局共享
   - SystemModelProvider: 供应商定义 (OpenAI, Google)
   - SystemModelDefinition: 模型定义 (gpt-4o, gemini-pro)

2. 用户配置层 (User Layer)：用户个性化配置
   - UserProviderConfig: 用户的 API Key、Base URL 等敏感信息
   - UserModelPreference: 用户的模型偏好（如隐藏某个模型、默认参数覆盖）
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

from sqlalchemy import Column, JSON, Text, UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship, Index
from pydantic import field_validator, ConfigDict


class ModelType(str, Enum):
    """模型类型"""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    VISION = "vision"


class ModelFeature(str, Enum):
    """模型特性"""
    TOOL_CALL = "tool_call"
    AGENT_THOUGHT = "agent_thought"
    IMAGE_INPUT = "image_input"
    CODE_INTERPRETER = "code_interpreter"
    WEB_SEARCH = "web_search"
    THINKING = "thinking"
    STRUCTURED_OUTPUT = "structured_output"


# ==================== 系统元数据层 ====================

class SystemModelProvider(SQLModel, table=True):
    """
    [系统层] 模型供应商定义
    全局共享的只读元数据
    """
    __tablename__ = "system_model_providers"

    id: UUID = Field(default_factory=uuid4, primary_key=True, description="供应商ID")
    name: str = Field(max_length=50, unique=True, description="供应商标识，如 openai")
    label: str = Field(max_length=100, description="显示名称，如 OpenAI")
    description: Optional[str] = Field(default=None)
    
    # 元数据
    icon: Optional[str] = Field(sa_column=Column(Text, nullable=True), description="图标")
    icon_background: Optional[str] = Field(default="#FFFFFF", max_length=20, description="背景色")
    default_base_url: Optional[str] = Field(default=None, max_length=500, description="默认API地址")
    supported_model_types: List[str] = Field(
        sa_column=Column(JSON, default=["chat"]),
        description="支持的模型类型"
    )
    help_url: Optional[str] = Field(default=None, max_length=500, description="帮助链接")
    
    # 系统控制
    position: int = Field(default=0, description="排序位置")
    owner_id: Optional[UUID] = Field(default=None, description="所有者ID（NULL=系统内置，有值=用户私有自定义）")
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # 关联
    models: List["SystemModelDefinition"] = Relationship(back_populates="provider")
    user_configs: List["UserProviderConfig"] = Relationship(back_populates="provider")

    __table_args__ = (
        Index("idx_sys_providers_name", "name"),
        Index("idx_sys_providers_position", "position"),
    )

    @field_validator('help_url', mode='before')
    def set_default_help_url(cls, v, info):
        # ... (保留原有逻辑，简化) ...
        return v

    @field_validator('id', mode='after')
    def serialize_id(cls, v):
        return str(v)
    @field_validator('owner_id', mode='after')
    def validate_owner_id(cls,v):
        return str(v)
    
    model_config = ConfigDict(extra="ignore")


class SystemModelDefinition(SQLModel, table=True):
    """
    [系统层] 模型定义
    全局共享的只读元数据
    """
    __tablename__ = "system_model_definitions"

    id: UUID = Field(default_factory=uuid4, primary_key=True, description="模型定义ID")
    provider_id: UUID = Field(foreign_key="system_model_providers.id", description="所属供应商")
    
    # 模型信息
    model_name: str = Field(max_length=100, description="模型标识，如 gpt-4o")
    label: str = Field(max_length=100, description="显示名称")
    description: Optional[str] = Field(default=None)
    model_type: str = Field(default="llm", max_length=20)
    
    # 能力参数
    features: List[str] = Field(sa_column=Column(JSON, default=[]))
    context_window: int = Field(default=4096)
    default_max_tokens: int = Field(default=4096)
    
    # 默认参数
    default_parameters: Dict[str, Any] = Field(sa_column=Column(JSON, default={}))
    pricing: Optional[Dict[str, Any]] = Field(sa_column=Column(JSON, default=None), description="价格信息")

    position: int = Field(default=0)
    is_enabled: bool = Field(default=True, description="系统级开关")
    owner_id: Optional[UUID] = Field(default=None, description="所有者ID（NULL=系统内置，有值=用户私有自定义）")
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # 关联
    provider: SystemModelProvider = Relationship(back_populates="models")

    __table_args__ = (
        Index("idx_sys_models_provider", "provider_id"),
        UniqueConstraint("provider_id", "model_name", name="uq_sys_model_provider_name"),
    )

    @field_validator('id', mode='after')
    def serialize_id(cls, v):
        return str(v)
    @field_validator('provider_id', mode='after')
    def serialize_provider_id(cls, v):
        return str(v)
    @field_validator('owner_id', mode='after')
    def validate_owner_id(cls,v):
        return str(v)
    
    model_config = ConfigDict(extra="ignore")


# ==================== 用户配置层 ====================

class UserProviderConfig(SQLModel, table=True):
    """
    [用户层] 用户对供应商的配置 (Credentials)
    存储 API Key 和 Base URL 覆盖
    """
    __tablename__ = "user_provider_configs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="accounts.id", description="用户ID")
    provider_id: UUID = Field(foreign_key="system_model_providers.id", description="供应商ID")
    
    # 敏感配置
    api_key: Optional[str] = Field(default=None, max_length=1000, description="加密存储的API Key")
    base_url_override: Optional[str] = Field(default=None, max_length=500, description="覆盖默认API地址")
    
    is_enabled: bool = Field(default=True, description="用户是否启用该供应商")
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # 关联
    provider: SystemModelProvider = Relationship(back_populates="user_configs")

    __table_args__ = (
        UniqueConstraint("user_id", "provider_id", name="uq_user_provider_config"),
        Index("idx_user_provider_cfg_user", "user_id"),
    )

    @field_validator('id', mode='after')
    def serialize_id(cls, v):
        return str(v)
    @field_validator('user_id', mode='after')
    def serialize_user_id(cls, v):
        return str(v)
    @field_validator('provider_id', mode='after')
    def serialize_provider_id(cls, v):
        return str(v)

class UserModelPreference(SQLModel, table=True):
    """
    [用户层] 用户对特定模型的偏好 (可选)
    例如：隐藏某个模型，或为某个模型设置特定的 temperature
    """
    __tablename__ = "user_model_preferences"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="accounts.id", description="用户ID")
    model_def_id: UUID = Field(foreign_key="system_model_definitions.id", description="模型定义ID")
    
    is_enabled: bool = Field(default=True, description="用户是否启用/显示该模型")
    
    # 参数覆盖 (可选)
    custom_parameters: Optional[Dict[str, Any]] = Field(sa_column=Column(JSON, nullable=True))
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    __table_args__ = (
        UniqueConstraint("user_id", "model_def_id", name="uq_user_model_pref"),
        Index("idx_user_model_pref_user", "user_id"),
    )

    @field_validator('id', mode='after')
    def serialize_id(cls, v):
        return str(v)
    @field_validator('user_id', mode='after')
    def serialize_user_id(cls, v):
        return str(v)   

    @field_validator('model_def_id', mode='after')
    def serialize_model_def_id(cls, v):
        return str(v)
