from typing import List, Optional, Dict, Any
from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class UserCreate(BaseModel):
    """用户创建模型"""
    
    username: str = Field(description="用户名", min_length=3, max_length=50)
    email: str = Field(description="邮箱地址")
    password: str = Field(description="密码", min_length=6)
    real_name: Optional[str] = Field(default=None, description="真实姓名")
    phone: Optional[str] = Field(default=None, description="手机号")
    gender: Optional[str] = Field(default=None, description="性别")
    birth_date: Optional[date] = Field(default=None, description="出生日期")
    constitution_type: Optional[str] = Field(default=None, description="体质类型")
    
    @field_validator('gender')
    def validate_gender(cls, v):
        """验证性别"""
        if v is not None:
            allowed_genders = ['male', 'female', 'other']
            if v not in allowed_genders:
                raise ValueError(f'性别必须是以下之一: {", ".join(allowed_genders)}')
        return v
    
    model_config = ConfigDict(
        json_encoders={
            date: lambda v: v.isoformat()
        },
        populate_by_name=True
    )


class UserUpdate(BaseModel):
    """用户更新模型"""
    
    real_name: Optional[str] = Field(default=None, description="真实姓名")
    phone: Optional[str] = Field(default=None, description="手机号")
    gender: Optional[str] = Field(default=None, description="性别")
    birth_date: Optional[date] = Field(default=None, description="出生日期")
    constitution_type: Optional[str] = Field(default=None, description="体质类型")
    avatar_url: Optional[str] = Field(default=None, description="头像URL")
    is_active: Optional[bool] = Field(default=None, description="是否激活")
    
    @field_validator('gender')
    def validate_gender(cls, v):
        """验证性别"""
        if v is not None:
            allowed_genders = ['male', 'female', 'other']
            if v not in allowed_genders:
                raise ValueError(f'性别必须是以下之一: {", ".join(allowed_genders)}')
        return v
    
    model_config = ConfigDict(
        json_encoders={
            date: lambda v: v.isoformat()
        },
        populate_by_name=True
    )


class PatientCreate(BaseModel):
    """患者创建模型"""
    
    user_id: int = Field(description="关联用户ID")
    patient_code: str = Field(description="患者编号")
    medical_history: Optional[str] = Field(default=None, description="既往病史")
    family_history: Optional[str] = Field(default=None, description="家族病史")
    allergy_info: Optional[str] = Field(default=None, description="过敏信息")
    current_medications: Optional[str] = Field(default=None, description="当前用药情况")
    emergency_contact_name: Optional[str] = Field(default=None, description="紧急联系人姓名")
    emergency_contact_phone: Optional[str] = Field(default=None, description="紧急联系人电话")
    
    model_config = ConfigDict(populate_by_name=True)


class PatientUpdate(BaseModel):
    """患者更新模型"""
    
    medical_history: Optional[str] = Field(default=None, description="既往病史")
    family_history: Optional[str] = Field(default=None, description="家族病史")
    allergy_info: Optional[str] = Field(default=None, description="过敏信息")
    current_medications: Optional[str] = Field(default=None, description="当前用药情况")
    emergency_contact_name: Optional[str] = Field(default=None, description="紧急联系人姓名")
    emergency_contact_phone: Optional[str] = Field(default=None, description="紧急联系人电话")
    
    model_config = ConfigDict(populate_by_name=True)


class AuthResponse(BaseModel):
    """认证响应模型"""
    access_token: str = Field(description="访问令牌")
    refresh_token: str= Field(description="刷新令牌")
    expires_in: int = Field(description="令牌有效期")  # 秒数
    user_id: UUID = Field(description="用户ID")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        },
        populate_by_name=True
    )
    #将UUID转换为字符串
    @field_validator('user_id')
    def convert_user_id_to_str(cls, v):
        """将UUID转换为字符串"""
        return str(v)


class RefreshResponse(BaseModel):
    access_token: str= Field(description="访问令牌")
    refresh_token: str= Field(description="刷新令牌")
    expires_in: int= Field(description="令牌有效期")
class RefreshRequest(BaseModel):
    refresh_token: str

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


class UserSessionCreate(BaseModel):
    """用户会话创建模型"""
    user_id: int = Field(description="用户ID")
    session_token: str = Field(description="会话令牌")
    access_token: Optional[str] = Field(default=None, description="访问令牌")
    refresh_token: Optional[str] = Field(default=None, description="刷新令牌")
    device_id: Optional[str] = Field(default=None, description="设备ID")
    device_type: Optional[DeviceType] = Field(default=None, description="设备类型")
    user_agent: Optional[str] = Field(default=None, description="用户代理")
    ip_address: Optional[str] = Field(default=None, description="IP地址")
    location: Optional[Dict[str, Any]] = Field(default=None, description="位置信息")
    expires_at: datetime = Field(description="过期时间")
    is_active: bool = Field(default=True, description="是否激活")


class UserSessionUpdate(BaseModel):
    """用户会话更新模型"""
    access_token: Optional[str] = Field(default=None, description="访问令牌")
    refresh_token: Optional[str] = Field(default=None, description="刷新令牌")
    device_id: Optional[str] = Field(default=None, description="设备ID")
    device_type: Optional[DeviceType] = Field(default=None, description="设备类型")
    user_agent: Optional[str] = Field(default=None, description="用户代理")
    ip_address: Optional[str] = Field(default=None, description="IP地址")
    location: Optional[Dict[str, Any]] = Field(default=None, description="位置信息")
    expires_at: Optional[datetime] = Field(default=None, description="过期时间")
    last_activity_at: Optional[datetime] = Field(default=None, description="最后活动时间")
    is_active: Optional[bool] = Field(default=None, description="是否激活")


class UserStateCreate(BaseModel):
    """用户状态创建模型"""
    app_name: str = Field(description="应用名称")
    user_id: str = Field(description="用户ID")
    state: Dict[str, Any] = Field(description="状态数据")
    update_time: datetime = Field(description="更新时间")


class UserStateUpdate(BaseModel):
    """用户状态更新模型"""
    state: Optional[Dict[str, Any]] = Field(default=None, description="状态数据")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")


class UserActivityCreate(BaseModel):
    """用户活动创建模型"""
    user_id: int = Field(description="用户ID")
    session_id: Optional[UUID] = Field(default=None, description="会话ID")
    activity_type: ActivityType = Field(description="活动类型")
    activity_data: Optional[Dict[str, Any]] = Field(default=None, description="活动数据")
    ip_address: Optional[str] = Field(default=None, description="IP地址")
    user_agent: Optional[str] = Field(default=None, description="用户代理")
    resource: Optional[str] = Field(default=None, description="资源")


class UserActivityUpdate(BaseModel):
    """用户活动更新模型"""
    activity_data: Optional[Dict[str, Any]] = Field(default=None, description="活动数据")
    resource: Optional[str] = Field(default=None, description="资源")



class UserLogin(BaseModel):
    """用户登录模型"""
    email: str = Field(description="邮箱")
    password: str = Field(description="密码")


# ==================== 管理员相关 Schema ====================

class AdminCreate(BaseModel):
    """管理员注册模型（仅需账号密码）"""
    username: str = Field(description="用户名", min_length=3, max_length=50)
    password: str = Field(description="密码", min_length=6)


class AdminLogin(BaseModel):
    """管理员登录模型（仅需账号密码）"""
    username: str = Field(description="用户名")
    password: str = Field(description="密码")


class AdminAuthResponse(BaseModel):
    """管理员认证响应模型"""
    access_token: str = Field(description="访问令牌")
    refresh_token: str = Field(description="刷新令牌")
    expires_in: int = Field(description="令牌有效期（秒）")
    user_id: UUID = Field(description="用户ID")
    role: str = Field(description="用户角色")

    @field_validator('user_id')
    def convert_user_id_to_str(cls, v):
        return str(v)

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
        populate_by_name=True
    )


class AdminResponse(BaseModel):
    """管理员信息响应（不含敏感信息）"""
    id: UUID
    username: str
    role: str
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
        populate_by_name=True
    )


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(description="旧密码")
    new_password: str = Field(description="新密码", min_length=6)