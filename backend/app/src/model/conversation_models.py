# """
# 对话数据模型
#
# 定义对话相关的数据结构和验证规则。
# """
#
# from typing import List, Optional, Dict, Any
# from datetime import datetime
# from decimal import Decimal
# from uuid import UUID, uuid4
# from sqlmodel import SQLModel, Field, Relationship, Index,Column,JSON
# from pydantic import field_validator, ConfigDict
#
#
# class Conversation(SQLModel, table=True):
#     """对话记录模型"""
#     __tablename__ = "conversations"
#     id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, description="对话ID")
#     user_id: UUID = Field(foreign_key="users.id", description="用户ID")
#     session_id: str = Field(max_length=50, description="会话ID")
#     conversation_type: str = Field(max_length=30, description="对话类型")
#     title: Optional[str] = Field(default=None, max_length=200, description="对话标题")
#     status: str = Field(default="active", description="对话状态")
#     total_messages: int = Field(default=0, description="消息总数")
#     created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
#     updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
#
#     # Table indexes
#     __table_args__ = (
#         Index("idx_conversations_user_id", "user_id"),
#         Index("idx_conversations_session_id", "session_id"),
#         Index("idx_conversations_conversation_type", "conversation_type"),
#         Index("idx_conversations_status", "status"),
#         Index("idx_conversations_created_at", "created_at"),
#     )
#
#     @field_validator('conversation_type')
#     def validate_conversation_type(cls, v):
#         """验证对话类型"""
#         allowed_types = ['diagnosis', 'herb_consultation', 'classic_search', 'case_reference', 'image_analysis', 'general_chat']
#         if v not in allowed_types:
#             raise ValueError(f'对话类型必须是以下之一: {", ".join(allowed_types)}')
#         return v
#
#     @field_validator('status')
#     def validate_status(cls, v):
#         """验证对话状态"""
#         allowed_statuses = ['active', 'completed', 'cancelled']
#         if v not in allowed_statuses:
#             raise ValueError(f'对话状态必须是以下之一: {", ".join(allowed_statuses)}')
#         return v
#
#     model_config = ConfigDict(
#         json_encoders={
#             datetime: lambda v: v.isoformat()
#         },
#         populate_by_name=True
#     )
#
#
# class Message(SQLModel, table=True):
#     """消息模型"""
#     __tablename__ = "messages"
#
#     id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, description="消息ID")
#     conversation_id: UUID = Field(foreign_key="conversations.id", description="对话ID")
#     role: str = Field(max_length=20, description="消息角色")
#     content: str = Field(description="消息内容")
#     message_type: str = Field(default="text", max_length=20, description="消息类型")
#     message_metadata: Optional[Dict[str, Any]] = Field(Column(JSON, default={}, nullable=True), description="元数据（JSON格式）")
#     is_deleted: bool = Field(default=False, description="是否删除")
#     created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
#
#     # Table indexes
#     __table_args__ = (
#         Index("idx_messages_conversation_id", "conversation_id"),
#         Index("idx_messages_role", "role"),
#         Index("idx_messages_message_type", "message_type"),
#         Index("idx_messages_created_at", "created_at"),
#     )
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
#     model_config = ConfigDict(
#         json_encoders={
#             datetime: lambda v: v.isoformat()
#         },
#         populate_by_name=True
#     )
#
"""
对话数据模型

定义对话相关的数据结构和验证规则。
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship, Index, Column
from sqlalchemy import JSON
from pydantic import field_validator, ConfigDict
import json

from app.src.model import User


class Conversation(SQLModel, table=True):
    """对话记录模型"""
    __tablename__ = "conversations"
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, description="对话ID")
    user_id: UUID = Field(foreign_key="users.id", description="用户ID")
    session_id: str = Field(max_length=50, description="会话ID")
    conversation_type: str = Field(max_length=30, description="对话类型")
    title: Optional[str] = Field(default=None, max_length=200, description="对话标题")
    status: str = Field(default="active", description="对话状态")
    total_messages: int = Field(default=0, description="消息总数")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


    user: "User" =Relationship(back_populates="conversations")
    # Table indexes
    __table_args__ = (
        Index("idx_conversations_user_id", "user_id"),
        Index("idx_conversations_session_id", "session_id"),
        Index("idx_conversations_conversation_type", "conversation_type"),
        Index("idx_conversations_status", "status"),
        Index("idx_conversations_created_at", "created_at"),
    )

    @field_validator('conversation_type')
    def validate_conversation_type(cls, v):
        """验证对话类型"""
        allowed_types = ['diagnosis', 'herb_consultation', 'classic_search', 'case_reference', 'image_analysis',
                         'general_chat']
        if v not in allowed_types:
            raise ValueError(f'对话类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    @field_validator('status')
    def validate_status(cls, v):
        """验证对话状态"""
        allowed_statuses = ['active', 'completed', 'cancelled']
        if v not in allowed_statuses:
            raise ValueError(f'对话状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        },
        populate_by_name=True
    )


class Message(SQLModel, table=True):
    """消息模型"""
    __tablename__ = "messages"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, description="消息ID")
    conversation_id: UUID = Field(foreign_key="conversations.id", description="对话ID")
    role: str = Field(max_length=20, description="消息角色")
    content: str = Field(description="消息内容")
    message_type: str = Field(default="text", max_length=20, description="消息类型")
    message_metadata: Optional[str] = Field(
        sa_column=Column("message_metadata", JSON, default='{}', nullable=True),
        description="元数据（JSON格式）"
    )
    is_deleted: bool = Field(default=False, description="是否删除")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")

    conversations: Conversation = Relationship(back_populates="messages")
    # Table indexes
    __table_args__ = (
        Index("idx_messages_conversation_id", "conversation_id"),
        Index("idx_messages_role", "role"),
        Index("idx_messages_message_type", "message_type"),
        Index("idx_messages_created_at", "created_at"),
    )

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

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        },
        populate_by_name=True
    )

    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        """设置元数据"""
        if metadata:
            self.message_metadata = json.dumps(metadata, ensure_ascii=False)
        else:
            self.message_metadata = '{}'

    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """获取元数据"""
        if self.message_metadata:
            try:
                return json.loads(self.message_metadata)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}



