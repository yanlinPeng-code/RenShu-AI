"""
模型配置数据模型

管理员层：配置供应商和内置模型（无api_key）
用户层：选择供应商、配置api_key和自定义参数
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

from sqlalchemy import Column, JSON, Text
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


# ==================== 管理员层：模型供应商 ====================

class ModelProvider(SQLModel, table=True):
    """
    模型供应商表（管理员管理）

    - 管理员可以增删改查供应商
    - 配置供应商的图标、描述、默认base_url等
    - 不存储 api_key
    """
    __tablename__ = "model_providers"

    id: UUID = Field(default_factory=uuid4, primary_key=True, description="供应商ID")
    name: str = Field(max_length=50, unique=True, description="供应商标识，如 openai")
    label: str = Field(max_length=100, description="显示名称，如 OpenAI")
    description: Optional[str] = Field(default=None, description="供应商描述")

    # 图标可以是 URL 或 Base64
    icon: Optional[str] = Field(
        sa_column=Column(Text, nullable=True),
        description="图标（URL或Base64）"
    )
    icon_background: Optional[str] = Field(
        default="#FFFFFF",
        max_length=20,
        description="图标背景色"
    )

    # 默认 API 地址（用户可覆盖）
    default_base_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="默认API地址"
    )

    # 支持的模型类型
    supported_model_types: List[str] = Field(
        sa_column=Column(JSON, default=["chat"]),
        description="支持的模型类型"
    )

    # 帮助链接
    help_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="获取API Key的帮助链接"
    )

    is_builtin: bool = Field(default=False, description="是否为内置供应商（不可删除）")
    is_enabled: bool = Field(default=True, description="是否启用（对用户可见）")
    position: int = Field(default=0, description="排序位置")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # 关联内置模型配置
    models: List["ModelConfig"] = Relationship(back_populates="provider")

    __table_args__ = (
        Index("idx_providers_name", "name"),
        Index("idx_providers_enabled", "is_enabled"),
        Index("idx_providers_position", "position"),
    )

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
        populate_by_name=True
    )


class ModelConfig(SQLModel, table=True):
    """
    模型配置表（管理员管理的内置模型列表）

    - 管理员配置每个供应商支持的模型
    - 包含模型的默认参数（温度、最大长度等）
    - 不存储 api_key
    """
    __tablename__ = "model_configs"

    id: UUID = Field(default_factory=uuid4, primary_key=True, description="模型配置ID")
    provider_id: UUID = Field(foreign_key="model_providers.id", description="供应商ID")

    # 模型基本信息
    model_name: str = Field(max_length=100, description="模型名称，如 gpt-4o")
    label: str = Field(max_length=100, description="显示名称")
    description: Optional[str] = Field(default=None, description="模型描述/介绍")
    model_type: str = Field(default="chat", max_length=20, description="模型类型")

    # 模型特性
    features: List[str] = Field(
        sa_column=Column(JSON, default=[]),
        description="模型特性列表"
    )

    # 模型能力参数
    context_window: int = Field(default=4096, description="上下文窗口大小")
    max_output_tokens: int = Field(default=4096, description="最大输出token数")

    # 默认参数配置（用户可覆盖）
    default_temperature: float = Field(default=0.7, description="默认温度")
    default_top_p: float = Field(default=1.0, description="默认Top P")
    default_max_tokens: int = Field(default=4096, description="默认最大输出token")

    # 额外的默认参数（JSON格式，灵活扩展）
    default_parameters: Dict[str, Any] = Field(
        sa_column=Column(JSON, default={}),
        description="其他默认参数"
    )

    # 模型属性（传给LangChain的固定参数）
    attributes: Dict[str, Any] = Field(
        sa_column=Column(JSON, default={}),
        description="模型固定属性"
    )

    # 定价信息（可选）
    pricing: Optional[Dict[str, Any]] = Field(
        sa_column=Column(JSON, nullable=True),
        description="定价信息"
    )

    is_enabled: bool = Field(default=True, description="是否启用")
    position: int = Field(default=0, description="排序位置")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # 关联供应商
    provider: Optional[ModelProvider] = Relationship(back_populates="models")

    __table_args__ = (
        Index("idx_models_provider_id", "provider_id"),
        Index("idx_models_name", "model_name"),
        Index("idx_models_enabled", "is_enabled"),
    )

    @field_validator('model_type')
    def validate_model_type(cls, v):
        allowed_types = ['chat', 'completion', 'embedding', 'vision']
        if v not in allowed_types:
            raise ValueError(f'模型类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
        populate_by_name=True
    )


# ==================== 用户层：用户模型配置 ====================

class UserModelConfig(SQLModel, table=True):
    """
    用户模型配置表

    - 用户选择管理员开放的供应商
    - 用户必须填写 api_key
    - 用户可以选择内置模型或自定义模型名称
    - 用户可以覆盖 base_url 和默认参数
    """
    __tablename__ = "user_model_configs"

    id: UUID = Field(default_factory=uuid4, primary_key=True, description="配置ID")
    user_id: UUID = Field(foreign_key="users.id", description="用户ID")

    # 必须选择一个系统供应商
    provider_id: UUID = Field(
        foreign_key="model_providers.id",
        description="供应商ID"
    )

    # 模型选择：可以选择内置模型，也可以自定义
    model_config_id: Optional[UUID] = Field(
        default=None,
        foreign_key="model_configs.id",
        description="内置模型配置ID（选择内置模型时使用）"
    )
    custom_model_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="自定义模型名称（不使用内置模型时填写）"
    )

    # 用户必填的 API Key
    api_key: str = Field(
        sa_column=Column(Text, nullable=False),
        description="API密钥（加密存储）"
    )

    # 用户可覆盖的 base_url
    base_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="自定义API地址（覆盖供应商默认值）"
    )

    # 用户自定义参数（覆盖默认值）
    custom_temperature: Optional[float] = Field(default=None, description="自定义温度")
    custom_top_p: Optional[float] = Field(default=None, description="自定义Top P")
    custom_max_tokens: Optional[int] = Field(default=None, description="自定义最大输出token")

    # 其他自定义参数
    custom_parameters: Dict[str, Any] = Field(
        sa_column=Column(JSON, default={}),
        description="其他自定义参数"
    )

    # 配置别名（用户自定义的显示名称）
    alias: Optional[str] = Field(
        default=None,
        max_length=100,
        description="配置别名"
    )

    is_default: bool = Field(default=False, description="是否为默认配置")
    is_enabled: bool = Field(default=True, description="是否启用")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # 关联
    provider: Optional[ModelProvider] = Relationship()

    __table_args__ = (
        Index("idx_user_models_user_id", "user_id"),
        Index("idx_user_models_default", "user_id", "is_default"),
        Index("idx_user_models_provider", "provider_id"),
    )

    @property
    def effective_model_name(self) -> str:
        """获取实际使用的模型名称"""
        return self.custom_model_name or ""

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
        populate_by_name=True
    )


