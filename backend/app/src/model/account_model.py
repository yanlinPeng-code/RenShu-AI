"""
账户数据模型

三端分离设计：
- accounts: 基础认证表（存储登录凭证）
- patients: 患者信息表
- doctors: 医生信息表
- admins: 管理员信息表
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date, timezone
from uuid import UUID, uuid4
from enum import Enum

from sqlalchemy import Column, JSON, UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship, Index
from pydantic import field_validator, ConfigDict

class UserState(SQLModel, table=True):
    """用户状态模型"""
    __tablename__ = "user_states"

    app_name: str = Field(max_length=128, primary_key=True, description="应用名称")
    user_id: UUID = Field(primary_key=True, description="用户ID")
    state: Optional[Dict[str, Any]] = Field(sa_column=Column(JSON, nullable=True,default= {}), description="状态数据")
    update_time: datetime = Field(default_factory=datetime.now, description="更新时间")

    # Table indexes
    __table_args__ = (
        # Index("idx_user_states_app_name", "app_name"),
        # Index("idx_user_states_app_user", "app_name", "user_id"),
        # Index("idx_user_states_update_time", "update_time"),
        # Index("idx_user_states_user_id", "user_id"),
        {"extend_existing": True}
    )

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        },
        populate_by_name=True
    )
class AccountType(str, Enum):
    """账户类型枚举"""
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"


class Account(SQLModel, table=True):
    """
    账户基础表 - 存储所有账户的认证信息

    特点：
    - 同一邮箱可以注册不同端的账号
    - 认证逻辑统一
    """
    __tablename__ = "accounts"

    id: UUID = Field(default_factory=uuid4, primary_key=True, description="账户ID")
    email: str = Field(max_length=100, description="邮箱地址")
    password_hash: str = Field(max_length=255, description="密码哈希")
    account_type: str = Field(description="账户类型: patient/doctor/admin")
    is_active: bool = Field(default=True, description="是否激活")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # Relationships
    patient: Optional["Patient"] = Relationship(back_populates="account")
    doctor: Optional["Doctor"] = Relationship(back_populates="account")
    admin: Optional["Admin"] = Relationship(back_populates="account")
    refresh_tokens: List["AccountRefreshToken"] = Relationship(back_populates="account")

    __table_args__ = (
        # 同一邮箱 + 账户类型 组合唯一（允许同一邮箱注册不同端）
        UniqueConstraint("email", "account_type", name="uq_accounts_email_type"),
        Index("idx_accounts_email", "email"),
        Index("idx_accounts_type", "account_type"),
        {"extend_existing": True}
    )

    @field_validator('account_type')
    def validate_account_type(cls, v):
        allowed_types = ['patient', 'doctor', 'admin']
        if v not in allowed_types:
            raise ValueError(f'账户类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
        populate_by_name=True
    )


class Patient(SQLModel, table=True):
    """
    患者信息表

    存储患者端特有的信息
    """
    __tablename__ = "patients"

    id: UUID = Field(default_factory=uuid4, primary_key=True, description="患者ID")
    account_id: UUID = Field(foreign_key="accounts.id", unique=True, description="关联账户ID")
    username: str = Field(max_length=50, unique=True, description="用户名")
    real_name: Optional[str] = Field(default=None, max_length=50, description="真实姓名")
    phone: Optional[str] = Field(default=None, max_length=20, description="手机号")
    gender: Optional[str] = Field(default=None, max_length=10, description="性别")
    birth_date: Optional[date] = Field(default=None, description="出生日期")
    constitution_type: Optional[str] = Field(default=None, max_length=50, description="体质类型")
    avatar_url: Optional[str] = Field(default=None, max_length=255, description="头像URL")

    # 患者特有字段
    medical_history: Optional[str] = Field(default=None, description="既往病史")
    family_history: Optional[str] = Field(default=None, description="家族病史")
    allergy_info: Optional[str] = Field(default=None, description="过敏信息")
    current_medications: Optional[str] = Field(default=None, description="当前用药情况")
    emergency_contact_name: Optional[str] = Field(default=None, max_length=50, description="紧急联系人姓名")
    emergency_contact_phone: Optional[str] = Field(default=None, max_length=20, description="紧急联系人电话")

    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # Relationships
    account: "Account" = Relationship(back_populates="patient")

    __table_args__ = (
        Index("idx_patients_username", "username"),
        Index("idx_patients_account_id", "account_id"),
        {"extend_existing": True}
    )

    @field_validator('gender')
    def validate_gender(cls, v):
        if v is not None:
            allowed_genders = ['male', 'female', 'other']
            if v not in allowed_genders:
                raise ValueError(f'性别必须是以下之一: {", ".join(allowed_genders)}')
        return v

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        },
        populate_by_name=True
    )


class Doctor(SQLModel, table=True):
    """
    医生信息表

    存储医生端特有的信息
    """
    __tablename__ = "doctors"

    id: UUID = Field(default_factory=uuid4, primary_key=True, description="医生ID")
    account_id: UUID = Field(foreign_key="accounts.id", unique=True, description="关联账户ID")
    username: str = Field(max_length=50, unique=True, description="用户名")
    real_name: Optional[str] = Field(default=None, max_length=50, description="真实姓名")
    phone: Optional[str] = Field(default=None, max_length=20, description="手机号")
    gender: Optional[str] = Field(default=None, max_length=10, description="性别")
    avatar_url: Optional[str] = Field(default=None, max_length=255, description="头像URL")

    # 医生特有字段
    license_no: Optional[str] = Field(default=None, max_length=50, description="执业证号")
    department: Optional[str] = Field(default=None, max_length=50, description="科室")
    hospital: Optional[str] = Field(default=None, max_length=100, description="所属医院")
    specialty: Optional[str] = Field(default=None, max_length=100, description="专业特长")
    title: Optional[str] = Field(default=None, max_length=50, description="职称")
    introduction: Optional[str] = Field(default=None, description="个人简介")

    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # Relationships
    account: "Account" = Relationship(back_populates="doctor")

    __table_args__ = (
        Index("idx_doctors_username", "username"),
        Index("idx_doctors_account_id", "account_id"),
        Index("idx_doctors_license_no", "license_no"),
        {"extend_existing": True}
    )

    @field_validator('gender')
    def validate_gender(cls, v):
        if v is not None:
            allowed_genders = ['male', 'female', 'other']
            if v not in allowed_genders:
                raise ValueError(f'性别必须是以下之一: {", ".join(allowed_genders)}')
        return v

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
        populate_by_name=True
    )


class Admin(SQLModel, table=True):
    """
    管理员信息表

    存储管理员端特有的信息
    """
    __tablename__ = "admins"

    id: UUID = Field(default_factory=uuid4, primary_key=True, description="管理员ID")
    account_id: UUID = Field(foreign_key="accounts.id", unique=True, description="关联账户ID")
    username: str = Field(max_length=50, unique=True, description="用户名")
    avatar_url: Optional[str] = Field(default=None, max_length=255, description="头像URL")

    # 管理员特有字段
    admin_level: str = Field(default="admin", description="管理员级别: admin/super_admin")
    permissions: Optional[Dict[str, Any]] = Field(
        sa_column=Column(JSON, nullable=True, default={}),
        description="权限配置"
    )

    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # Relationships
    account: "Account" = Relationship(back_populates="admin")

    __table_args__ = (
        Index("idx_admins_username", "username"),
        Index("idx_admins_account_id", "account_id"),
        {"extend_existing": True}
    )

    @field_validator('admin_level')
    def validate_admin_level(cls, v):
        allowed_levels = ['admin', 'super_admin']
        if v not in allowed_levels:
            raise ValueError(f'管理员级别必须是以下之一: {", ".join(allowed_levels)}')
        return v

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
        populate_by_name=True
    )


class AccountRefreshToken(SQLModel, table=True):
    """账户刷新令牌模型"""
    __tablename__ = "account_refresh_tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True, description="主键ID")
    account_id: UUID = Field(foreign_key="accounts.id", description="账户ID")
    token_hash: str = Field(max_length=255, unique=True, description="令牌哈希值")
    expires_at: datetime = Field(description="过期时间")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    is_revoked: bool = Field(default=False, description="是否已撤销")

    # Relationships
    account: "Account" = Relationship(back_populates="refresh_tokens")

    __table_args__ = (
        Index("idx_account_refresh_tokens_account_id", "account_id"),
        Index("idx_account_refresh_tokens_token_hash", "token_hash"),
        Index("idx_account_refresh_tokens_expires_at", "expires_at"),
        {"extend_existing": True}
    )

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        },
        populate_by_name=True
    )


class AccountActivity(SQLModel, table=True):
    """账户活动记录模型"""
    __tablename__ = "account_activities"

    id: UUID = Field(default_factory=uuid4, primary_key=True, description="活动ID")
    account_id: UUID = Field(foreign_key="accounts.id", description="账户ID")
    activity_type: str = Field(description="活动类型: login/logout/register/password_change")
    ip_address: Optional[str] = Field(default=None, description="IP地址")
    user_agent: Optional[str] = Field(default=None, description="用户代理")
    activity_data: Optional[Dict[str, Any]] = Field(
        sa_column=Column(JSON, nullable=True, default={}),
        description="活动数据"
    )
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")

    __table_args__ = (
        Index("idx_account_activities_account_id", "account_id"),
        Index("idx_account_activities_type", "activity_type"),
        Index("idx_account_activities_created_at", "created_at"),
        {"extend_existing": True}
    )

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        },
        populate_by_name=True
    )

