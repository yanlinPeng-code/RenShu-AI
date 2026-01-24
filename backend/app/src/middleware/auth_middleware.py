"""
认证中间件
自动解析JWT并设置用户上下文
使用纯 ASGI 中间件实现，避免 BaseHTTPMiddleware 的事务问题
"""

from starlette.types import ASGIApp, Receive, Send, Scope
from sqlmodel import select
from app.src.common.context.request_context import UserContext, set_current_context
from app.src.utils.auth_utils import verify_token
from app.src.common.config.prosgresql_config import async_db_manager
from app.src.model.account_model import Account
from app.src.utils import get_logger

logger = get_logger("AuthMiddleware")

# 角色对应的权限映射
ROLE_PERMISSIONS = {
    "patient": [
        "chat:read",
        "chat:write",
        "user:profile:read",
        "user:profile:write",
    ],
    "doctor": [
        "chat:read",
        "chat:write",
        "user:profile:read",
        "user:profile:write",
        "patient:read",
        "prescription:read",
        "prescription:write",
    ],
    "admin": [
        "chat:read",
        "chat:write",
        "user:profile:read",
        "user:profile:write",
        "patient:read",
        "patient:write",
        "prescription:read",
        "prescription:write",
        "user:manage",
        "system:config",
    ],
    "super_admin": [
        "*",  # 超级管理员拥有所有权限
    ],
}


class AuthContextMiddleware:
    """
    认证上下文中间件（纯 ASGI 实现）

    功能：
    1. 自动解析请求中的JWT token
    2. 将用户信息设置到请求上下文中
    3. 从数据库加载用户角色和权限
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # 只处理 HTTP 请求
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 初始化默认上下文（未认证）
        context = UserContext()

        # 跳过 OPTIONS 请求
        method = scope.get("method", "")
        if method != "OPTIONS":
            # 从 headers 中获取 Authorization
            headers = dict(scope.get("headers", []))
            auth_header = headers.get(b"authorization", b"").decode("utf-8")

            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

                try:
                    # 验证 token
                    token_data = verify_token(token)
                    user_id = token_data["user_id"]

                    # 从数据库加载用户角色
                    roles = await self._load_user_roles(user_id)

                    # 根据角色计算权限
                    permissions = self._calculate_permissions(roles)

                    # 创建已认证的上下文
                    context = UserContext(
                        user_id=user_id,
                        is_authenticated=True,
                        roles=roles,
                        permissions=permissions,
                    )

                    logger.debug(f"用户认证成功: {user_id}, 角色: {roles}")

                except Exception as e:
                    # Token无效，保持未认证状态
                    logger.debug(f"Token验证失败: {e}")

        # 设置上下文（无论是否认证成功）
        set_current_context(context)

        # 继续处理请求
        await self.app(scope, receive, send)

    async def _load_user_roles(self, user_id: str) -> list[str]:
        """
        从数据库加载用户角色（使用Account表）
        使用 async_db_manager.get_session() 获取数据库会话
        """
        try:
            # 检查数据库是否已初始化
            if async_db_manager.async_session_factory is None:
                logger.warning("数据库尚未初始化，返回默认角色")
                return ["patient"]

            # 使用 async_db_manager 获取会话
            async with async_db_manager.get_session() as session:
                stmt = select(Account.account_type).where(Account.id == user_id)
                result = await session.exec(stmt)
                account_type = result.one_or_none()

                if account_type:
                    return [account_type]

                logger.warning(f"未找到账户 {user_id} 的角色信息")
                return ["patient"]  # 默认角色

        except Exception as e:
            logger.error(f"加载用户角色失败: {e}")
            return ["patient"]  # 出错时返回默认角色

    def _calculate_permissions(self, roles: list[str]) -> list[str]:
        """
        根据角色计算权限
        """
        permissions = set()

        for role in roles:
            role_perms = ROLE_PERMISSIONS.get(role, [])

            # 如果有通配符权限，返回所有权限
            if "*" in role_perms:
                all_perms = set()
                for perms in ROLE_PERMISSIONS.values():
                    if "*" not in perms:
                        all_perms.update(perms)
                all_perms.add("*")
                return list(all_perms)

            permissions.update(role_perms)

        return list(permissions)
