"""
请求上下文管理
使用contextvars实现请求级别的用户信息存储
"""

from contextvars import ContextVar
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class UserContext:
    """用户上下文信息"""
    user_id: Optional[str] = None
    is_authenticated: bool = False
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)


# 创建请求级别的上下文变量
_request_context: ContextVar[UserContext] = ContextVar(
    'request_context',
    default=UserContext()
)


def get_current_context() -> UserContext:
    """获取当前请求的用户上下文"""
    return _request_context.get()


def set_current_context(context: UserContext) -> None:
    """设置当前请求的用户上下文"""
    _request_context.set(context)


def get_current_user_id() -> Optional[str]:
    """获取当前登录用户的ID"""
    ctx = get_current_context()
    return ctx.user_id if ctx.is_authenticated else None


def is_authenticated() -> bool:
    """检查当前用户是否已认证"""
    return get_current_context().is_authenticated


def get_user_roles() -> list[str]:
    """获取当前用户的角色列表"""
    return get_current_context().roles


def get_user_permissions() -> list[str]:
    """获取当前用户的权限列表"""
    return get_current_context().permissions
