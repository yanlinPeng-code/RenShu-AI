"""
用户数据模型

定义用户相关的数据结构和验证规则。
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON,Enum
from sqlmodel import SQLModel, Field, Relationship, Index
from pydantic import field_validator, ConfigDict
from enum import Enum
import json


class User(SQLModel, table=True):
    """用户模型"""
    __tablename__ = "users"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, description="用户ID")
    username: str = Field(max_length=50, unique=True, description="用户名")
    email: str = Field(max_length=100, unique=True, description="邮箱地址")
    password_hash: str = Field(max_length=255, description="密码哈希")
    role: str = Field(default="patient", description="用户角色")
    real_name: Optional[str] = Field(default=None, max_length=50, description="真实姓名")
    phone: Optional[str] = Field(default=None, max_length=20, description="手机号")
    gender: Optional[str] = Field(default=None, max_length=10, description="性别")
    birth_date: Optional[date] = Field(default=None, description="出生日期")
    constitution_type: Optional[str] = Field(default=None, max_length=50, description="体质类型（如：阳虚质、阴虚质等）")
    avatar_url: Optional[str] = Field(default=None, max_length=255, description="头像URL")
    is_active: bool = Field(default=True, description="是否激活")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    # Relationships
    patient: Optional["Patient"] = Relationship(back_populates="user")
    
    # Table indexes
    __table_args__ = (
        Index("idx_users_username", "username"),
        Index("idx_users_email", "email"),
        Index("idx_users_role", "role"),
    )
    
    @field_validator('role')
    def validate_role(cls, v):
        """验证用户角色"""
        allowed_roles = ['patient', 'doctor', 'admin']
        if v not in allowed_roles:
            raise ValueError(f'用户角色必须是以下之一: {", ".join(allowed_roles)}')
        return v
    
    @field_validator('gender')
    def validate_gender(cls, v):
        """验证性别"""
        if v is not None:
            allowed_genders = ['male', 'female', 'other']
            if v not in allowed_genders:
                raise ValueError(f'性别必须是以下之一: {", ".join(allowed_genders)}')
        return v
    
    @field_validator('username')
    def validate_username(cls, v):
        """验证用户名"""
        if not v or not v.strip():
            raise ValueError('用户名不能为空')
        return v.strip()
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        },
        populate_by_name=True
    )


class Patient(SQLModel, table=True):
    """患者详细信息模型"""
    __tablename__ = "patients"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, description="患者ID")
    user_id: UUID = Field(foreign_key="users.id", description="关联用户ID")
    patient_code: str = Field(max_length=20, unique=True, description="患者编号")
    medical_history: Optional[str] = Field(default=None, description="既往病史")
    family_history: Optional[str] = Field(default=None, description="家族病史")
    allergy_info: Optional[str] = Field(default=None, description="过敏信息")
    current_medications: Optional[str] = Field(default=None, description="当前用药情况")
    emergency_contact_name: Optional[str] = Field(default=None, max_length=50, description="紧急联系人姓名")
    emergency_contact_phone: Optional[str] = Field(default=None, max_length=20, description="紧急联系人电话")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    # Relationships
    user: "User" = Relationship(back_populates="patient")
    
    # Table indexes
    __table_args__ = (
        Index("idx_patients_patient_code", "patient_code"),
        Index("idx_patients_user_id", "user_id"),
    )
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        },
        populate_by_name=True
    )


class DeviceType(str, Enum):
    """设备类型枚举"""
    WEB = "web"
    MOBILE = "mobile"
    DESKTOP = "desktop"
    UNKNOWN = "unknown"


class ActivityType(str, Enum):
    """活动类型枚举"""
    LOGIN = "login"
    LOGOUT = "logout"
    REGISTER = "register"
    PASSWORD_CHANGE = "password_change"
    EMAIL_VERIFY = "email_verify"
    PROFILE_UPDATE = "profile_update"
    SESSION_EXPIRE = "session_expire"


class UserSession(SQLModel, table=True):
    """用户会话模型"""
    __tablename__ = "user_sessions"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True, description="会话ID")
    user_id: UUID = Field(default_factory=uuid4,foreign_key="users.id", description="用户ID")
    session_token: str = Field(max_length=255, unique=True, description="会话令牌")
    access_token: Optional[str] = Field(default=None, max_length=500, description="访问令牌")
    refresh_token: Optional[str] = Field(default=None, max_length=500, description="刷新令牌")
    device_id: Optional[str] = Field(default=None, max_length=255, description="设备ID")
    device_type: Optional[DeviceType] = Field(default=None, description="设备类型")
    user_agent: Optional[str] = Field(default=None, description="用户代理")
    ip_address: Optional[str] = Field(default=None, description="IP地址")
    location: Optional[Dict[str, Any]] = Field(sa_column=Column(JSON, nullable=True,default= {}), description="位置信息")
    expires_at: datetime = Field(description="过期时间")
    last_activity_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), description="最后活动时间")
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), description="创建时间")
    is_active: bool = Field(default=True, description="是否激活")
    
    # Relationships
    user: "User" = Relationship()
    activities: List["UserActivity"] = Relationship(back_populates="session")
    
    # Table indexes
    __table_args__ = (
        Index("idx_sessions_active", "is_active"),
        Index("idx_sessions_device_id", "device_id"),
        Index("idx_sessions_expires_at", "expires_at"),
        Index("idx_sessions_token", "session_token"),
        Index("idx_sessions_user_id", "user_id"),
    )
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        },
        populate_by_name=True
    )


class UserState(SQLModel, table=True):
    """用户状态模型"""
    __tablename__ = "user_states"
    
    app_name: str = Field(max_length=128, primary_key=True, description="应用名称")
    user_id: UUID = Field(default_factory=uuid4, primary_key=True, description="用户ID")
    state: Optional[Dict[str, Any]] = Field(sa_column=Column(JSON, nullable=True,default= {}), description="状态数据")
    update_time: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    # Table indexes
    __table_args__ = (
        Index("idx_user_states_app_name", "app_name"),
        Index("idx_user_states_app_name_user_id", "app_name", "user_id"),
        Index("idx_user_states_app_user", "app_name", "user_id"),
        Index("idx_user_states_update_time", "update_time"),
        Index("idx_user_states_user_id", "user_id"),
    )
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        },
        populate_by_name=True
    )


class UserActivity(SQLModel, table=True):
    """用户活动模型"""
    __tablename__ = "user_activities"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True, description="活动ID")
    user_id: UUID = Field(default_factory=uuid4,foreign_key="users.id", description="用户ID")
    session_id: Optional[UUID] = Field(default=None, foreign_key="user_sessions.id", description="会话ID")
    activity_type: Optional[str] = Field(
        description="活动类型",
    )

    activity_data: Optional[Dict[str, Any]] = Field(sa_column=Column(JSON, nullable=True,default={}), description="活动数据")
    ip_address: Optional[str] = Field(default=None, description="IP地址")
    user_agent: Optional[str] = Field(default=None, description="用户代理")
    resource: Optional[str] = Field(default=None, max_length=255, description="资源")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="创建时间")
    
    # Relationships
    user: "User" = Relationship()
    session: Optional["UserSession"] = Relationship(back_populates="activities")
    
    # Table indexes
    __table_args__ = (
        Index("idx_activities_created_at", "created_at"),
        Index("idx_activities_type", "activity_type"),
        Index("idx_activities_user_id", "user_id"),
    )
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        },
        populate_by_name=True
    )


from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID


class RefreshToken(SQLModel, table=True):
    """刷新令牌模型"""
    __tablename__ = "refresh_tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True, description="主键ID")
    user_id: UUID = Field(foreign_key="users.id", description="用户ID")
    token_hash: str = Field(max_length=255, unique=True, description="令牌哈希值")
    session_id: Optional[UUID] = Field(default=None, foreign_key="user_sessions.id", description="会话ID")
    expires_at: datetime = Field(description="过期时间")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="创建时间")
    revoked_at: Optional[datetime] = Field(default=None, description="撤销时间")
    is_revoked: bool = Field(default=False, description="是否已撤销")

    # Relationships
    user: "User" = Relationship()
    session: Optional["UserSession"] = Relationship()

    # Table indexes
    __table_args__ = (
        Index("idx_refresh_tokens_expires_at", "expires_at"),
        Index("idx_refresh_tokens_revoked", "is_revoked"),
        Index("idx_refresh_tokens_token_hash", "token_hash"),
        Index("idx_refresh_tokens_user_id", "user_id"),
    )

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        },
        populate_by_name=True
    )
