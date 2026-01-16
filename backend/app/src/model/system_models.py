"""
系统数据模型

定义系统相关的数据结构和验证规则。
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from uuid import uuid4
from uuid import UUID
from sqlmodel import SQLModel, Field, Index
from pydantic import field_validator, ConfigDict


class SystemConfig(SQLModel, table=True):
    """系统配置模型"""
    __tablename__ = "system_configs"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, description="配置ID")
    config_key: str = Field(max_length=100, unique=True, description="配置键")
    config_value: Optional[str] = Field(default=None, description="配置值")
    config_type: str = Field(default="string", max_length=20, description="配置类型")
    description: Optional[str] = Field(default=None, description="配置描述")
    is_active: bool = Field(default=True, description="是否启用")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    # Table indexes
    __table_args__ = (
        Index("idx_system_configs_config_key", "config_key"),
        Index("idx_system_configs_is_active", "is_active"),
        {"extend_existing": True}
    )
    
    @field_validator('config_type')
    def validate_config_type(cls, v):
        """验证配置类型"""
        allowed_types = ['string', 'number', 'boolean', 'json']
        if v not in allowed_types:
            raise ValueError(f'配置类型必须是以下之一: {", ".join(allowed_types)}')
        return v
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        },
        populate_by_name=True
    )


class SystemStats(SQLModel):
    """系统统计模型"""
    
    total_users: int = Field(description="总用户数")
    active_users: int = Field(description="活跃用户数")
    total_conversations: int = Field(description="总对话数")
    active_conversations: int = Field(description="活跃对话数")
    total_cases: int = Field(description="总病例数")
    completed_cases: int = Field(description="已完成病例数")
    total_herbs: int = Field(description="总药材数")
    total_prescriptions: int = Field(description="总方剂数")
    system_uptime: str = Field(description="系统运行时间")
    last_updated: datetime = Field(description="最后更新时间")
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        },
        populate_by_name=True
    )


class DatabaseStats(SQLModel):
    """数据库统计模型"""
    
    total_tables: int = Field(description="总表数")
    total_records: int = Field(description="总记录数")
    database_size: str = Field(description="数据库大小")
    last_backup: Optional[datetime] = Field(default=None, description="最后备份时间")
    connection_count: int = Field(description="连接数")
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        },
        populate_by_name=True
    )


class HealthCheck(SQLModel):
    """健康检查模型"""
    
    status: str = Field(description="系统状态")
    version: str = Field(description="系统版本")
    uptime: str = Field(description="运行时间")
    database_status: str = Field(description="数据库状态")
    redis_status: Optional[str] = Field(default=None, description="Redis状态")
    disk_usage: str = Field(description="磁盘使用率")
    memory_usage: str = Field(description="内存使用率")
    cpu_usage: str = Field(description="CPU使用率")
    last_check: datetime = Field(description="最后检查时间")
    
    @field_validator('status')
    def validate_status(cls, v):
        """验证系统状态"""
        allowed_statuses = ['healthy', 'warning', 'critical', 'maintenance']
        if v not in allowed_statuses:
            raise ValueError(f'系统状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        },
        populate_by_name=True
    )


class LogEntry(SQLModel):
    """日志条目模型"""
    
    id: Optional[UUID] = Field(default_factory=uuid4, description="日志ID")
    level: str = Field(description="日志级别")
    message: str = Field(description="日志消息")
    module: Optional[str] = Field(default=None, description="模块名")
    function: Optional[str] = Field(default=None, description="函数名")
    line_number: Optional[int] = Field(default=None, description="行号")
    user_id: Optional[int] = Field(default=None, description="用户ID")
    request_id: Optional[str] = Field(default=None, description="请求ID")
    trace_id: Optional[str] = Field(default=None, description="追踪ID")
    extra_data: Optional[Dict[str, Any]] = Field(default=None, description="额外数据")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")
    
    @field_validator('level')
    def validate_level(cls, v):
        """验证日志级别"""
        allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v not in allowed_levels:
            raise ValueError(f'日志级别必须是以下之一: {", ".join(allowed_levels)}')
        return v
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        },
        populate_by_name=True
    )


class AuditLog(SQLModel):
    """审计日志模型"""
    
    id: Optional[UUID] = Field(default_factory=uuid4, description="审计日志ID")
    user_id: Optional[UUID] = Field(default_factory=uuid4, description="用户ID")
    action: str = Field(description="操作")
    resource_type: str = Field(description="资源类型")
    resource_id: Optional[str] = Field(default=None, description="资源ID")
    old_values: Optional[Dict[str, Any]] = Field(default=None, description="旧值")
    new_values: Optional[Dict[str, Any]] = Field(default=None, description="新值")
    ip_address: Optional[str] = Field(default=None, description="IP地址")
    user_agent: Optional[str] = Field(default=None, description="用户代理")
    request_id: Optional[str] = Field(default=None, description="请求ID")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        },
        populate_by_name=True
    )


class BackupInfo(SQLModel):
    """备份信息模型"""
    
    id: Optional[UUID] = Field(default_factory=uuid4, description="备份ID")
    backup_name: str = Field(description="备份名称")
    backup_type: str = Field(description="备份类型")
    file_path: str = Field(description="文件路径")
    file_size: int = Field(description="文件大小（字节）")
    status: str = Field(description="备份状态")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    
    @field_validator('backup_type')
    def validate_backup_type(cls, v):
        """验证备份类型"""
        allowed_types = ['full', 'incremental', 'differential']
        if v not in allowed_types:
            raise ValueError(f'备份类型必须是以下之一: {", ".join(allowed_types)}')
        return v
    
    @field_validator('status')
    def validate_status(cls, v):
        """验证备份状态"""
        allowed_statuses = ['pending', 'running', 'completed', 'failed', 'cancelled']
        if v not in allowed_statuses:
            raise ValueError(f'备份状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        },
        populate_by_name=True
    )


class SystemInfo(SQLModel):
    """系统信息模型"""
    
    system_name: str = Field(description="系统名称")
    version: str = Field(description="版本号")
    build_date: str = Field(description="构建日期")
    python_version: str = Field(description="Python版本")
    fastapi_version: str = Field(description="FastAPI版本")
    database_version: str = Field(description="数据库版本")
    environment: str = Field(description="运行环境")
    debug_mode: bool = Field(description="调试模式")
    timezone: str = Field(description="时区")
    language: str = Field(description="语言")
    
    model_config = ConfigDict(populate_by_name=True)


