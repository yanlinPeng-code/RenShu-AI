
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, ConfigDict
from sqlmodel import SQLModel


# class ConversationCreate(BaseModel):
#     """对话创建模型"""
#
#     user_id: int = Field(description="用户ID")
#     session_id: str = Field(description="会话ID")
#     conversation_type: str = Field(description="对话类型")
#     title: Optional[str] = Field(default=None, description="对话标题")
#
#     @field_validator('conversation_type')
#     def validate_conversation_type(cls, v):
#         """验证对话类型"""
#         allowed_types = ['diagnosis', 'herb_consultation', 'classic_search', 'case_reference', 'image_analysis',
#                          'general_chat']
#         if v not in allowed_types:
#             raise ValueError(f'对话类型必须是以下之一: {", ".join(allowed_types)}')
#         return v
#
#     model_config = ConfigDict(populate_by_name=True)
#
#
# class ConversationUpdate(BaseModel):
#     """对话更新模型"""
#
#     title: Optional[str] = Field(default=None, description="对话标题")
#     status: Optional[str] = Field(default=None, description="对话状态")
#
#     @field_validator('status')
#     def validate_status(cls, v):
#         """验证对话状态"""
#         if v is not None:
#             allowed_statuses = ['active', 'completed', 'cancelled']
#             if v not in allowed_statuses:
#                 raise ValueError(f'对话状态必须是以下之一: {", ".join(allowed_statuses)}')
#         return v
#
#     model_config = ConfigDict(populate_by_name=True)
#
#
# class MessageCreate(BaseModel):
#     """消息创建模型"""
#
#     conversation_id: int = Field(description="对话ID")
#     role: str = Field(description="消息角色")
#     content: str = Field(description="消息内容")
#     message_type: str = Field(default="text", description="消息类型")
#     metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据（JSON格式）")
#
#     @field_validator('role')
#     def validate_role(cls, v):
#         """验证消息角色"""
#         allowed_roles = ['user', 'assistant', 'system']
#         if v not in allowed_roles:
#             raise ValueError(f'消息角色必须是以下之一: {", ".join(allowed_roles)}')
#         return v
#
#     @field_validator('message_type')
#     def validate_message_type(cls, v):
#         """验证消息类型"""
#         allowed_types = ['text', 'image', 'file', 'prescription', 'diagnosis']
#         if v not in allowed_types:
#             raise ValueError(f'消息类型必须是以下之一: {", ".join(allowed_types)}')
#         return v
#
#     model_config = ConfigDict(populate_by_name=True)
#
#
# class MessageUpdate(BaseModel):
#     """消息更新模型"""
#
#     content: Optional[str] = Field(default=None, description="消息内容")
#     message_type: Optional[str] = Field(default=None, description="消息类型")
#     metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据（JSON格式）")
#     is_deleted: Optional[bool] = Field(default=None, description="是否删除")
#
#     @field_validator('message_type')
#     def validate_message_type(cls, v):
#         """验证消息类型"""
#         if v is not None:
#             allowed_types = ['text', 'image', 'file', 'prescription', 'diagnosis']
#             if v not in allowed_types:
#                 raise ValueError(f'消息类型必须是以下之一: {", ".join(allowed_types)}')
#         return v
#
#     model_config = ConfigDict(populate_by_name=True)
#
#
# class ConversationWithMessages(BaseModel):
#     """包含消息的对话模型"""
#
#     conversation: Conversation
#     messages: List[Message]
#
#     model_config = ConfigDict(populate_by_name=True)
#
#
# class ConversationSummary(BaseModel):
#     """对话摘要模型"""
#
#     id: int = Field(description="对话ID")
#     title: Optional[str] = Field(default=None, description="对话标题")
#     conversation_type: str = Field(description="对话类型")
#     status: str = Field(description="对话状态")
#     total_messages: int = Field(description="消息总数")
#     last_message_time: Optional[datetime] = Field(default=None, description="最后消息时间")
#     created_at: datetime = Field(description="创建时间")
#
#     model_config = ConfigDict(
#         json_encoders={
#             datetime: lambda v: v.isoformat()
#         },
#         populate_by_name=True
#     )
#
#
# class MessageWithConversation(BaseModel):
#     """包含对话信息的消息模型"""
#
#     message: Message
#     conversation: Conversation
#
#     model_config = ConfigDict(populate_by_name=True)


# 创建和更新模型
class ConversationCreate(SQLModel):
    """对话创建模型"""

    user_id: int = Field(description="用户ID")
    session_id: str = Field(description="会话ID")
    conversation_type: str = Field(description="对话类型")
    title: Optional[str] = Field(default=None, description="对话标题")

    @field_validator('conversation_type')
    def validate_conversation_type(cls, v):
        """验证对话类型"""
        allowed_types = ['diagnosis', 'herb_consultation', 'classic_search', 'case_reference', 'image_analysis',
                         'general_chat']
        if v not in allowed_types:
            raise ValueError(f'对话类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    model_config = ConfigDict(populate_by_name=True)


class ConversationUpdate(SQLModel):
    """对话更新模型"""

    title: Optional[str] = Field(default=None, description="对话标题")
    status: Optional[str] = Field(default=None, description="对话状态")

    @field_validator('status')
    def validate_status(cls, v):
        """验证对话状态"""
        if v is not None:
            allowed_statuses = ['active', 'completed', 'cancelled']
            if v not in allowed_statuses:
                raise ValueError(f'对话状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v

    model_config = ConfigDict(populate_by_name=True)


class MessageCreate(SQLModel):
    """消息创建模型"""

    conversation_id: int = Field(description="对话ID")
    role: str = Field(description="消息角色")
    content: str = Field(description="消息内容")
    message_type: str = Field(default="text", description="消息类型")
    message_metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据（JSON格式）")

    @field_validator('role')
    def validate_role(cls, v):
        """验证消息角色"""
        allowed_roles = ['user', 'assistant', 'system']
        if v not in allowed_roles:
            raise ValueError(f'消息角色必须是以下之一: {", ".join(allowed_roles)}')
        return v

    @field_validator('message_type')
    def validate_message_type(cls, v):
        """验证消息类型"""
        allowed_types = ['text', 'image', 'file', 'prescription', 'diagnosis']
        if v not in allowed_types:
            raise ValueError(f'消息类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    model_config = ConfigDict(populate_by_name=True)


class MessageUpdate(SQLModel):
    """消息更新模型"""

    content: Optional[str] = Field(default=None, description="消息内容")
    is_deleted: Optional[bool] = Field(default=None, description="是否删除")

    model_config = ConfigDict(populate_by_name=True)


# 复合模型
class ConversationWithMessages(SQLModel):
    """带消息的对话模型"""

    conversation: "Conversation"
    messages: List["Message"]

    model_config = ConfigDict(populate_by_name=True)


class ConversationSummary(SQLModel):
    """对话摘要模型"""

    id: int = Field(description="对话ID")
    user_id: int = Field(description="用户ID")
    session_id: str = Field(description="会话ID")
    conversation_type: str = Field(description="对话类型")
    title: Optional[str] = Field(default=None, description="对话标题")
    status: str = Field(description="对话状态")
    total_messages: int = Field(description="消息总数")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        },
        populate_by_name=True
    )


class MessageWithConversation(SQLModel):
    """带对话的消息模型"""

    message: "Message"
    conversation: "Conversation"

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        },
        populate_by_name=True
    )