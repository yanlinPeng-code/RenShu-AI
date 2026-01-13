"""
权限装饰器
用于在service层方法上进行鉴权
"""

from functools import wraps
from typing import Callable, Any, TypeVar, Optional
from fastapi import HTTPException

from app.src.core.context.request_context import (
    get_current_context,
    get_current_user_id,
    is_authenticated,
    get_user_roles,
    get_user_permissions,
)
from app.src.utils import get_logger

logger = get_logger("AuthDecorators")

F = TypeVar('F', bound=Callable[..., Any])


def require_login(func: F) -> F:
    """
    要求用户已登录的装饰器

    使用示例:
        class ChatService:
            @require_login
            async def generate(self, chat_request: ChatRequest):
                user_id = get_current_user_id()  # 直接获取用户ID
                ...
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        if not is_authenticated():
            logger.warning(f"未授权访问: {func.__name__}")
            raise HTTPException(
                status_code=401,
                detail="请先登录",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return await func(*args, **kwargs)

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        if not is_authenticated():
            logger.warning(f"未授权访问: {func.__name__}")
            raise HTTPException(
                status_code=401,
                detail="请先登录",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return func(*args, **kwargs)

    # 判断是否为异步函数
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper  # type: ignore
    return sync_wrapper  # type: ignore


def require_roles(*required_roles: str):
    """
    要求用户具有指定角色的装饰器

    使用示例:
        @require_roles("admin", "manager")
        async def delete_user(self, user_id: str):
            ...
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not is_authenticated():
                raise HTTPException(
                    status_code=401,
                    detail="请先登录",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            user_roles = set(get_user_roles())
            if not user_roles.intersection(set(required_roles)):
                logger.warning(
                    f"角色权限不足: {func.__name__}, 需要: {required_roles}, 拥有: {user_roles}"
                )
                raise HTTPException(
                    status_code=403,
                    detail=f"需要以下角色之一: {', '.join(required_roles)}"
                )
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not is_authenticated():
                raise HTTPException(
                    status_code=401,
                    detail="请先登录",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            user_roles = set(get_user_roles())
            if not user_roles.intersection(set(required_roles)):
                logger.warning(
                    f"角色权限不足: {func.__name__}, 需要: {required_roles}, 拥有: {user_roles}"
                )
                raise HTTPException(
                    status_code=403,
                    detail=f"需要以下角色之一: {', '.join(required_roles)}"
                )
            return func(*args, **kwargs)

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    return decorator


def require_permissions(*required_permissions: str):
    """
    要求用户具有指定权限的装饰器

    使用示例:
        @require_permissions("chat:write", "chat:read")
        async def send_message(self, message: str):
            ...
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not is_authenticated():
                raise HTTPException(
                    status_code=401,
                    detail="请先登录",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            user_perms = set(get_user_permissions())
            missing_perms = set(required_permissions) - user_perms

            if missing_perms:
                logger.warning(
                    f"权限不足: {func.__name__}, 缺少: {missing_perms}"
                )
                raise HTTPException(
                    status_code=403,
                    detail=f"缺少权限: {', '.join(missing_perms)}"
                )
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not is_authenticated():
                raise HTTPException(
                    status_code=401,
                    detail="请先登录",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            user_perms = set(get_user_permissions())
            missing_perms = set(required_permissions) - user_perms

            if missing_perms:
                logger.warning(
                    f"权限不足: {func.__name__}, 缺少: {missing_perms}"
                )
                raise HTTPException(
                    status_code=403,
                    detail=f"缺少权限: {', '.join(missing_perms)}"
                )
            return func(*args, **kwargs)

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    return decorator


def require_owner(get_owner_id: Callable[..., Optional[str]]):
    """
    要求用户是资源所有者的装饰器

    使用示例:
        @require_owner(lambda self, resource_id: self.get_resource_owner(resource_id))
        async def update_resource(self, resource_id: str, data: dict):
            ...
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not is_authenticated():
                raise HTTPException(
                    status_code=401,
                    detail="请先登录",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            current_user_id = get_current_user_id()

            # 调用获取所有者的函数
            owner_id = get_owner_id(*args, **kwargs)
            if asyncio.iscoroutine(owner_id):
                owner_id = await owner_id

            if owner_id != current_user_id:
                # 检查是否为管理员（管理员可以访问所有资源）
                if "admin" not in get_user_roles():
                    logger.warning(
                        f"非资源所有者访问: {func.__name__}, "
                        f"owner: {owner_id}, current: {current_user_id}"
                    )
                    raise HTTPException(
                        status_code=403,
                        detail="没有权限访问此资源"
                    )

            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not is_authenticated():
                raise HTTPException(
                    status_code=401,
                    detail="请先登录",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            current_user_id = get_current_user_id()
            owner_id = get_owner_id(*args, **kwargs)

            if owner_id != current_user_id:
                if "admin" not in get_user_roles():
                    logger.warning(
                        f"非资源所有者访问: {func.__name__}, "
                        f"owner: {owner_id}, current: {current_user_id}"
                    )
                    raise HTTPException(
                        status_code=403,
                        detail="没有权限访问此资源"
                    )

            return func(*args, **kwargs)

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    return decorator
