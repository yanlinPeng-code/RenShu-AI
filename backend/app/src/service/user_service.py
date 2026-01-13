"""
用户服务层 - 阿里巴巴标准异常处理

展示如何在Service层抛出异常，由Controller层捕获并转换为标准响应，集成日志功能。
"""

from typing import Optional
from datetime import datetime
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.src.schema.user_schema import UserCreate, AuthResponse, AdminCreate, AdminAuthResponse
from app.src.utils.auth_utils import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, verify_token, hash_refresh_token,
    get_refresh_token_expire_time
)
from .base_service import BaseService
from app.src.utils import get_logger
from sqlmodel import insert, select, update, delete
from app.src.model import User, ActivityType
from app.src.core.decorators import require_login, require_roles
from app.src.core.context import get_current_user_id
from ..entity.app_entity import DEFAULT_APP_NAME
from ..model.user_model import RefreshToken, UserState
from ..response.exception.exceptions import (
    ValidationException, BusinessException, InternalServerException,
    ResourceNotFoundException, AuthorizationException
)

security = HTTPBearer(auto_error=False)

class UserService(BaseService[User]):
    """用户服务类"""
    
    def __init__(self,
                 session,
                ):
        self.logger=get_logger("UserService")
        super().__init__(User, session)

    async def create_user(self, user_data: UserCreate, client_ip: str = None) -> UUID:
        """
        创建用户
        返回新创建的用户ID
        """
        validata=UserCreate.model_validate(user_data)
        #验证是否填写用户名
        if not validata.username:
            raise ValidationException("用户名不能为空")
        if not validata.email:
            raise ValidationException("邮箱不能为空")
        if not validata.password:
            raise ValidationException("密码不能为空")

        #验证邮箱格式
        if not await self._is_valid_email(validata.email):
            raise ValidationException("邮箱格式错误")
        #判断邮箱是否已存在
        if await self._email_exists(validata.email):
            raise BusinessException(
                message="邮箱已存在",
                error_code="EMAIL_ALREADY_EXISTS",
                details={"email": validata.email}
            )
        #加密密码
        validata.password=hash_password(validata.password)
        self.logger.debug("密码已加密", password=validata.password)

        #创建新用户
        new_user=User(
            username=validata.username,
            email=validata.email,
            password_hash=validata.password,
            is_active=True,
        )
        user=await self.create(new_user)


        await self._record_user_activity(user.id, "register", client_ip)
        #TODO: 创建用户会话

        
        self.logger.info(f"User registered: {validata.email}", client_ip=client_ip)
        
        return user.id


    async def authenticate_user(self, email: str, password: str, client_ip: str = None) -> AuthResponse:
        """
        验证用户身份并返回认证信息
        """
        # 验证输入
        if not email:
            raise ValidationException("邮箱不能为空")
        if not password:
            raise ValidationException("密码不能为空")

        # 查找用户
        user = await self._get_user_by_email(email)
        if not user:
            raise ResourceNotFoundException(f"用户 {email} 不存在")

        # 验证密码
        if not verify_password(password, user.password_hash):
            raise ValidationException("用户名或密码错误")

        # 检查用户是否激活
        if not user.is_active:
            raise ValidationException("用户账户已被禁用")

        # 生成访问令牌和刷新令牌
        access_token =create_access_token(str(user.id))
        refresh_token = create_refresh_token()
        
        # 存储刷新令牌
        await self._store_refresh_token(str(user.id), refresh_token)
        
        # 使用默认应用名称
        app_name = DEFAULT_APP_NAME
        
        # 更新用户状态
        await self._update_user_state(user.id, app_name, {
            'last_login': datetime.now().isoformat(),
            'login_count': 1,  # 这里应该从数据库获取实际的登录次数并加1
            'email_verified': True
        })
        
        # 记录用户登录活动
        await self._record_user_activity(user.id, "login", client_ip)
        
        self.logger.info(f"User logged in: {email}", client_ip=client_ip)
        
        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=24 * 3600,  # 24小时
            user_id=user.id
        )


    async def refresh_token(self, refresh_token: str, client_ip: str = None) -> AuthResponse:
        """刷新令牌"""
        # 对刷新令牌进行哈希处理
        token_hash = hash_refresh_token(refresh_token)

        # 查询是否存在对应的刷新令牌记录 - 修复查询语法
        stmt = select(RefreshToken.user_id).where(
            RefreshToken.token_hash == token_hash
        )
        result = await self.session.exec(stmt)
        user_id = result.one_or_none()

        if not user_id:
            raise ResourceNotFoundException("未知的token")

        # 删除旧的刷新令牌
        delete_stmt = delete(RefreshToken).where(
            RefreshToken.token_hash == token_hash  # 移除 column() 函数
        )
        await self.session.exec(delete_stmt)
        await self.session.flush() # 添加提交

        # 生成新的访问令牌和刷新令牌
        new_access_token = create_access_token(str(user_id))
        new_refresh_token =create_refresh_token()

        # 存储新的刷新令牌
        await self._store_refresh_token(user_id, new_refresh_token)

        self.logger.info("刷新令牌成功", extra={"user_id": str(user_id)})

        # 更新用户状态
        await self._record_user_activity(user_id, ActivityType.PROFILE_UPDATE, client_ip)

        return AuthResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=24 * 3600,
            user_id=user_id
        )

    async def get_current_user(
            self,
            credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> User:
        """Get current user from JWT token (兼容旧接口)"""
        user_id = await self.get_current_user_id(credentials)
        user = await self.get(user_id)
        if not user:
            raise ResourceNotFoundException("用户不存在")
        return user

    # ========== 使用装饰器的新方法 ==========

    @require_login
    async def get_me(self) -> User:
        """获取当前登录用户信息"""
        user_id = get_current_user_id()
        user = await self.get(user_id)
        if not user:
            raise ResourceNotFoundException("用户不存在")
        return user

    @require_login
    async def logout_me(self, client_ip: str = None) -> None:
        """当前用户登出"""
        user_id = get_current_user_id()
        await self._logout(user_id, client_ip)

    async def _logout(self, user_id: UUID, client_ip: str = None) -> None:
        """内部方法：执行登出逻辑"""
        # 1. 删除refresh tokens
        stmt = delete(RefreshToken).where(
            RefreshToken.user_id == user_id
        )
        await self.session.exec(stmt)
        await self.session.flush()
        # 2. 更新用户状态为 'offline'
        await self._update_user_state(user_id, DEFAULT_APP_NAME, {
            'status': 'offline',
            'logout_time': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        })
        # 3. 记录登出活动
        await self._record_user_activity(user_id, ActivityType.LOGOUT.value, client_ip)
        self.logger.info("用户登出成功", extra={"user_id": str(user_id)})


    async def logout(self, user_id: UUID, client_ip: str = None) -> None:
        """登出 (兼容旧接口)"""
        await self._logout(user_id, client_ip)


    async def _get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        stmt = select(User).where(User.email == email)
        result = await self.session.exec(stmt)
        return result.one_or_none()

    async def _is_valid_email(self, email: str) -> bool:
        """验证邮箱格式"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    async def _email_exists(self, email: str) -> bool:
        """检查邮箱是否已存在"""
        stmt=select(User).where(User.email == email)
        result = await self.session.exec(stmt)
        return result.one_or_none() is not None
    

    async def _store_refresh_token(self, user_id, refresh_token):
        """存储刷新token"""


        token_hash = hash_refresh_token(refresh_token)
        expires_at = get_refresh_token_expire_time()
        stmt=insert(RefreshToken).values(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        await self.session.exec(stmt)
        await self.session.flush()

    async def _update_user_state(self, user_id,app_name,param):
        """Update user state"""

        try:
            stmt=select(UserState).where(
                UserState.app_name == app_name,
                UserState.user_id == user_id
            )
            result = await self.session.exec(stmt)
            user_state: UserState = result.one_or_none()
            if user_state:
                #更新现有的状态
                user_state.state = param
                update_stmt=update(UserState).where(
                    UserState.user_id == user_state.user_id,
                ).values(
                    state=param,
                    update_time=datetime.now()
                )
                await self.session.exec(update_stmt)
                await self.session.flush()
                self.logger.info("用户状态已更新")
            else:
                # 创建新的状态
                stmt=insert(UserState).values(
                    user_id=user_id,
                    app_name=app_name,
                    state=param,
                    update_time=datetime.now()
                )
                await self.session.exec(stmt)
                await self.session.flush()
                self.logger.info("用户状态已更新")
        except Exception as e:
            self.logger.error(f"更新用户状态失败: {str(e)}")
            raise InternalServerException(
                message="更新用户状态失败",
                error_code="UPDATE_USER_STATE_ERROR",
                details={"original_error": str(e)}
            )

    async def _record_user_activity(self, user_id: UUID, activity_type: str, ip_address: str = None):
        """记录用户活动"""
        try:
            from app.src.model.user_model import UserActivity, ActivityType
            
            # 确保活动类型有效
            if not hasattr(ActivityType, activity_type.upper()):
                activity_type = "UNKNOWN"
            
            activity = UserActivity(
                user_id=user_id,
                activity_type=activity_type,
                ip_address=ip_address,
                created_at=datetime.now()
            )
            
            self.session.add(activity)
            await self.session.flush()
            self.logger.info(f"用户活动已记录: {activity_type}", user_id=user_id, ip_address=ip_address)
        except Exception as e:
            self.logger.error(f"记录用户活动失败: {str(e)}", user_id=user_id, ip_address=ip_address)
    async def get_current_user_id(
                self,
                credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> str:
            """Get current user ID from JWT token"""
            if not credentials:
                raise AuthorizationException("未提供授权信息")

            try:
                token_data =verify_token(credentials.credentials)
                return token_data["user_id"]
            except Exception as e:
                raise AuthorizationException(message="无效的授权信息", details={"original_error": str(e)})

    # ==================== 管理员相关方法 ====================


    async def create_admin(self, admin_data: AdminCreate, client_ip: str = None) -> UUID:
        """
        创建管理员（仅需账号密码）
        返回新创建的管理员ID
        """
        # 验证输入
        if not admin_data.username:
            raise ValidationException("用户名不能为空")
        if not admin_data.password:
            raise ValidationException("密码不能为空")

        # 判断用户名是否已存在
        if await self._username_exists(admin_data.username):
            raise BusinessException(
                message="用户名已存在",
                error_code="USERNAME_ALREADY_EXISTS",
                details={"username": admin_data.username}
            )

        # 加密密码
        password_hash =hash_password(admin_data.password)

        # 创建管理员用户（使用默认邮箱和头像）
        new_admin = User(
            username=admin_data.username,
            email=f"{admin_data.username}@admin.local",  # 管理员默认邮箱
            password_hash=password_hash,
            role="admin",
            avatar_url="/static/default_admin_avatar.png",  # 默认头像
            is_active=True,
        )
        admin = await self.create(new_admin)

        await self._record_user_activity(admin.id, "register", client_ip)
        self.logger.info(f"Admin registered: {admin_data.username}", client_ip=client_ip)

        return admin.id


    async def authenticate_admin(self, username: str, password: str, client_ip: str = None) -> AdminAuthResponse:
        """
        管理员登录验证（使用用户名）
        """
        # 验证输入
        if not username:
            raise ValidationException("用户名不能为空")
        if not password:
            raise ValidationException("密码不能为空")

        # 查找管理员
        admin = await self._get_user_by_username(username)
        if not admin:
            raise ResourceNotFoundException(f"管理员 {username} 不存在")

        # 验证是否为管理员角色
        if admin.role not in ['admin', 'super_admin']:
            raise AuthorizationException("该账号不是管理员")

        # 验证密码
        if not verify_password(password, admin.password_hash):
            raise ValidationException("用户名或密码错误")

        # 检查是否激活
        if not admin.is_active:
            raise ValidationException("管理员账户已被禁用")

        # 生成令牌
        access_token =create_access_token(str(admin.id))
        refresh_token = create_refresh_token()

        # 存储刷新令牌
        await self._store_refresh_token(str(admin.id), refresh_token)

        # 更新用户状态
        await self._update_user_state(admin.id, DEFAULT_APP_NAME, {
            'last_login': datetime.now().isoformat(),
            'login_count': 1,
        })

        # 记录登录活动
        await self._record_user_activity(admin.id, "login", client_ip)

        self.logger.info(f"Admin logged in: {username}", client_ip=client_ip)

        return AdminAuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=24 * 3600,
            user_id=admin.id,
            role=admin.role
        )

    async def require_admin(
        self,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> User:
        """
        验证当前用户是否为管理员 (兼容旧接口)
        用于需要管理员权限的接口
        """
        user = await self.get_current_user(credentials)
        if user.role not in ['admin', 'super_admin']:
            raise AuthorizationException("需要管理员权限")
        return user

    # ========== 管理员专用方法（带装饰器） ==========

    @require_roles("admin", "super_admin")
    async def get_admin_me(self) -> User:
        """获取当前管理员信息"""
        user_id = get_current_user_id()
        admin = await self.get(user_id)
        if not admin:
            raise ResourceNotFoundException("管理员不存在")
        return admin

    @require_roles("admin", "super_admin")
    async def admin_logout(self, client_ip: str = None) -> None:
        """管理员登出"""
        user_id = get_current_user_id()
        await self._logout(user_id, client_ip)

    async def _get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        stmt = select(User).where(User.username == username)
        result = await self.session.exec(stmt)
        return result.one_or_none()

    async def _username_exists(self, username: str) -> bool:
        """检查用户名是否已存在"""
        stmt = select(User).where(User.username == username)
        result = await self.session.exec(stmt)
        return result.one_or_none() is not None

