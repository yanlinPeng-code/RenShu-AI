from faulthandler import is_enabled
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship, Index
from pydantic import field_validator, ConfigDict, Field,BaseModel

# ==================== DTO / Schema ====================

# --- 管理员：供应商管理 ---

class ModelProviderCreate(SQLModel):
    """创建供应商"""
    name: str = Field(max_length=50, description="供应商标识")
    label: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    icon_background: str = "#FFFFFF"
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    supported_model_types: List[str] = Field(default=["chat"])
    position: int = 0
        






class ModelProviderUpdate(SQLModel):
    """更新供应商"""
    provider_id: UUID = Field(description="供应商ID")
    label: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    icon_background: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    supported_model_types: Optional[List[str]] = None
    help_url: Optional[str] = None
    is_enabled: Optional[bool] = None
    position: Optional[int] = None

class ModelProviderDelete(BaseModel):
    provider_id: UUID = Field(description="供应商ID")
# --- 管理员：模型配置管理 ---

class ModelConfigCreate(SQLModel):
    """创建模型配置"""
    provider_id: UUID
    model_name: str = Field(max_length=100)
    label: str = Field(default="")
    description: Optional[str] = None
    model_type: str = "llm"
    features: List[str] = Field(default=[])
    context_window: int = 4096
    default_temperature: float = 0.7
    default_top_p: float = 1.0
    default_max_tokens: int = 4096
    default_parameters: Dict[str, Any] = Field(default={})
    position: int = 0

    @field_validator('model_type', mode="before")
    def validate_model_type(cls, v):
        allowed_types = ["llm", "multimodal", "embedding", "rerank", "image", "audio", "video", "code"]
        if v not in allowed_types:
            raise ValueError(f'模型类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    @field_validator('features', mode='before')
    def set_default_features_for_model_type(cls, v, info):
        """根据model_type设置默认的features特性"""
        if v is None:
            v = []

        model_type = "llm"
        if hasattr(info, 'data') and info.data:
            model_type = info.data.get('model_type', 'llm')

        if model_type == "llm":
            if "structured_output" not in v:
                v.append("structured_output")
            if "tool_call" not in v:
                v.append("tool_call")
        elif model_type == "embedding":
            if "embedding" not in v:
                v.append("embedding")
        elif model_type == "rerank":
            if "rerank" not in v:
                v.append("rerank")
        elif model_type == "image":
            if "image-generate" not in v:
                v.append("imagegenerate")
            if "image-input" not in v:
                v.append("image-input")
        elif model_type == "code":
            if "coding" not in v:
                v.append("coding")

        return v

    @field_validator('label', mode='before')
    def set_default_label(cls, v, info):
        """当label未提供时，默认与model_name相同"""
        if v is None or v == "":
            if info.data and 'model_name' in info.data:
                model_name_value = info.data['model_name']
                if model_name_value:
                    return model_name_value
        return v


class ModelConfigUpdate(SQLModel):
    """更新模型配置（管理员）"""
    model_config_id: UUID = Field(description="模型配置ID")
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
    
    @field_validator('features', mode='before')
    def set_default_features_for_chat_update(cls, v, info):
        """当model_type为llm时，默认添加structured_output和tool_call特性"""
        # 如果features未提供或为None，使用空列表
        if v is None:
            v = []
        
        # 获取model_type的值
        model_type = None
        if hasattr(info, 'data') and info.data:
            model_type = info.data.get('model_type')
      
        if not model_type or model_type not in ["llm"]:
            return v
            
        # 将features转换为列表（如果它不是的话）
        if not isinstance(v, list):
            v = list(v) if v else []
        
        # 确保structured_output和tool_call在列表中
        # 修复拼写错误: struct_output -> structured_output
        if "structured_output" not in v:
            v.append("structured_output")
        if "tool_call" not in v:
            v.append("tool_call")
        
        return v


class ModelConfigDelete(BaseModel):
    model_config_id: UUID = Field(description="模型配置ID")

class ProviderApiKeyVerify(BaseModel):
    """验证供应商API Key"""
    provider_id: UUID = Field(description="供应商ID")
    api_key: str = Field(description="API密钥")
    base_url: Optional[str] = Field(default=None, description="自定义API地址")
    model_name: Optional[str] = Field(default=None, description="测试用的模型名称")


# # --- 用户：模型配置管理 ---

# class UserModelConfigCreate(SQLModel):
#     """创建用户模型配置"""
#     provider_id: UUID = Field(description="供应商ID")
#     model_config_id: Optional[UUID] = Field(default=None, description="内置模型ID（二选一）")
#     custom_model_name: Optional[str] = Field(default=None, description="自定义模型名称（二选一）")
#     api_key: str = Field(description="API密钥（必填）")
#     base_url: Optional[str] = Field(default=None, description="自定义API地址")
#     custom_temperature: Optional[float] = None
#     custom_top_p: Optional[float] = None
#     custom_max_tokens: Optional[int] = None
#     custom_parameters: Dict[str, Any] = Field(default={})
#     alias: Optional[str] = None
#     is_default: bool = False


# class UserModelConfigUpdate(SQLModel):
#     """更新用户模型配置"""
#     model_config_id: Optional[UUID] = None
#     custom_model_name: Optional[str] = None
#     api_key: Optional[str] = None
#     base_url: Optional[str] = None
#     custom_temperature: Optional[float] = None
#     custom_top_p: Optional[float] = None
#     custom_max_tokens: Optional[int] = None
#     custom_parameters: Optional[Dict[str, Any]] = None
#     alias: Optional[str] = None
#     is_default: Optional[bool] = None
#     is_enabled: Optional[bool] = None


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

    @field_validator('id', mode='after')
    def serialize_id(cls, v):
        return str(v)


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

    @field_validator('id', mode='after')
    def serialize_id(cls, v):
        return str(v)


# class UserModelConfigResponse(SQLModel):
#     """用户模型配置响应"""
#     id: UUID
#     provider_id: UUID
#     provider_name: Optional[str] = None
#     provider_label: Optional[str] = None
#     model_config_id: Optional[UUID]
#     model_name: Optional[str] = None
#     model_label: Optional[str] = None
#     custom_model_name: Optional[str]
#     has_api_key: bool = True  # 不返回实际key，只返回是否已配置
#     base_url: Optional[str]
#     alias: Optional[str]
#     is_default: bool
#     is_enabled: bool
