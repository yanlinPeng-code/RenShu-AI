"""
账户服务层 - 三端分离设计

处理患者、医生、管理员的注册、登录、登出
"""

from typing import Optional, Tuple
from datetime import datetime
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.src.schema.user_schema import AuthResponse
from app.src.utils.auth_utils import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, verify_token, hash_refresh_token,
    get_refresh_token_expire_time
)
from .base_service import BaseService
from app.src.utils import get_logger
from sqlmodel import select, update, insert
from app.src.model.account_model import (
    Account, Patient, Doctor, Admin, AccountRefreshToken, AccountActivity
)

from ..common.context.request_context import get_current_user_id
from ..common.decorators.auth_decorators import require_login, require_roles
from ..entity.app_entity import DEFAULT_APP_NAME
from ..model.account_model import UserState
from ..response.exception.exceptions import (
    ValidationException, BusinessException, InternalServerException,
    ResourceNotFoundException, AuthorizationException
)

security = HTTPBearer(auto_error=False)


class AccountService(BaseService[Account]):
    """账户服务类 - 三端分离设计"""

    def __init__(self, session):
        self.logger = get_logger("AccountService")
        super().__init__(Account, session)

    # ==================== 患者注册/登录/登出 ====================

    async def register_patient(
        self,
        email: str,
        password: str,
        username: str,
        real_name: str = None,
        phone: str = None,
        gender: str = None,
        birth_date=None,
        constitution_type: str = None,
        client_ip: str = None
    ) -> Tuple[UUID, UUID]:
        """
        注册患者账户

        Returns:
            Tuple[account_id, patient_id]
        """
        if not email or not password or not username:
            raise ValidationException("邮箱、密码和用户名不能为空")

        if not await self._is_valid_email(email):
            raise ValidationException("邮箱格式错误")

        if await self._account_exists(email, "patient"):
            raise BusinessException(
                message="该邮箱已注册患者账户",
                error_code="EMAIL_ALREADY_EXISTS",
                details={"email": email, "account_type": "patient"}
            )

        if await self._username_exists_in_patients(username):
            raise BusinessException(
                message="用户名已存在",
                error_code="USERNAME_ALREADY_EXISTS",
                details={"username": username}
            )

        # 创建账户
        password_hash = hash_password(password)
        account = Account(
            email=email,
            password_hash=password_hash,
            account_type="patient",
            is_active=True
        )
        account = await self.create(account)

        # 创建患者资料
        patient = Patient(
            account_id=account.id,
            username=username,
            real_name=real_name,
            phone=phone,
            gender=gender,
            birth_date=birth_date,
            constitution_type=constitution_type
        )
        self.session.add(patient)
        await self.session.flush()
        await self.session.refresh(patient)

        await self._record_activity(account.id, "register", client_ip)

        self.logger.info(f"患者注册成功: {email}, username: {username}")
        return account.id, patient.id

    async def login_patient(
        self,
        email: str,
        password: str,
        client_ip: str = None
    ) -> AuthResponse:
        """患者登录"""
        if not email or not password:
            raise ValidationException("邮箱和密码不能为空")

        account = await self._get_account_by_email_and_type(email, "patient")
        if not account:
            raise ResourceNotFoundException(f"用户 {email} 不存在")

        if not verify_password(password, account.password_hash):
            raise ValidationException("邮箱或密码错误")

        if not account.is_active:
            raise ValidationException("账户已被禁用")

        access_token = create_access_token(str(account.id))
        refresh_token = create_refresh_token()

        await self._store_refresh_token(account.id, refresh_token)

        await self._update_user_state(account.id, DEFAULT_APP_NAME, {
            'last_login': datetime.now().isoformat(),
            'login_count': 1,
            'email_verified': True
        })

        await self._record_activity(account.id, "login", client_ip)

        self.logger.info(f"患者登录成功: {email}")

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=24 * 3600,
            user_id=account.id
        )

    # ==================== 医生注册/登录/登出 ====================

    async def register_doctor(
        self,
        email: str,
        password: str,
        username: str,
        real_name: str = None,
        phone: str = None,
        gender: str = None,
        license_no: str = None,
        department: str = None,
        hospital: str = None,
        specialty: str = None,
        title: str = None,
        client_ip: str = None
    ) -> Tuple[UUID, UUID]:
        """
        注册医生账户

        Returns:
            Tuple[account_id, doctor_id]
        """
        if not email or not password or not username:
            raise ValidationException("邮箱、密码和用户名不能为空")

        if not await self._is_valid_email(email):
            raise ValidationException("邮箱格式错误")

        if await self._account_exists(email, "doctor"):
            raise BusinessException(
                message="该邮箱已注册医生账户",
                error_code="EMAIL_ALREADY_EXISTS",
                details={"email": email, "account_type": "doctor"}
            )

        if await self._username_exists_in_doctors(username):
            raise BusinessException(
                message="用户名已存在",
                error_code="USERNAME_ALREADY_EXISTS",
                details={"username": username}
            )

        # 创建账户
        password_hash = hash_password(password)
        account = Account(
            email=email,
            password_hash=password_hash,
            account_type="doctor",
            is_active=True
        )
        account = await self.create(account)

        # 创建医生资料
        doctor = Doctor(
            account_id=account.id,
            username=username,
            real_name=real_name,
            phone=phone,
            gender=gender,
            license_no=license_no,
            department=department,
            hospital=hospital,
            specialty=specialty,
            title=title
        )
        self.session.add(doctor)
        await self.session.flush()
        await self.session.refresh(doctor)

        await self._record_activity(account.id, "register", client_ip)

        self.logger.info(f"医生注册成功: {email}, username: {username}")
        return account.id, doctor.id

    async def login_doctor(
        self,
        email: str,
        password: str,
        client_ip: str = None
    ) -> AuthResponse:
        """医生登录"""
        if not email or not password:
            raise ValidationException("邮箱和密码不能为空")

        account = await self._get_account_by_email_and_type(email, "doctor")
        if not account:
            raise ResourceNotFoundException(f"医生账户 {email} 不存在")

        if not verify_password(password, account.password_hash):
            raise ValidationException("邮箱或密码错误")

        if not account.is_active:
            raise ValidationException("账户已被禁用")

        access_token = create_access_token(str(account.id))
        refresh_token = create_refresh_token()

        await self._store_refresh_token(account.id, refresh_token)

        await self._update_user_state(account.id, DEFAULT_APP_NAME, {
            'last_login': datetime.now().isoformat(),
            'login_count': 1,
        })

        await self._record_activity(account.id, "login", client_ip)

        self.logger.info(f"医生登录成功: {email}")

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=24 * 3600,
            user_id=account.id
        )

    # ==================== 管理员注册/登录/登出 ====================

    async def register_admin(
        self,
        username: str,
        password: str,
        client_ip: str = None
    ) -> Tuple[UUID, UUID]:
        """
        注册管理员账户（使用username@admin.local作为邮箱）

        Returns:
            Tuple[account_id, admin_id]
        """
        if not username or not password:
            raise ValidationException("用户名和密码不能为空")

        email = f"{username}@admin.local"

        if await self._account_exists(email, "admin"):
            raise BusinessException(
                message="用户名已存在",
                error_code="USERNAME_ALREADY_EXISTS",
                details={"username": username}
            )

        if await self._username_exists_in_admins(username):
            raise BusinessException(
                message="用户名已存在",
                error_code="USERNAME_ALREADY_EXISTS",
                details={"username": username}
            )

        # 创建账户
        password_hash = hash_password(password)
        account = Account(
            email=email,
            password_hash=password_hash,
            account_type="admin",
            is_active=True
        )
        account = await self.create(account)

        # 创建管理员资料
        admin = Admin(
            account_id=account.id,
            username=username,
            avatar_url="/static/default_admin_avatar.png",
            admin_level="admin"
        )
        self.session.add(admin)
        await self.session.flush()
        await self.session.refresh(admin)

        await self._record_activity(account.id, "register", client_ip)

        self.logger.info(f"管理员注册成功: {username}")
        return account.id, admin.id

    async def login_admin(
        self,
        username: str,
        password: str,
        client_ip: str = None
    ) -> AuthResponse:
        """管理员登录"""
        if not username or not password:
            raise ValidationException("用户名和密码不能为空")

        email = f"{username}@admin.local"
        account = await self._get_account_by_email_and_type(email, "admin")

        if not account:
            raise ResourceNotFoundException(f"管理员 {username} 不存在")

        if not verify_password(password, account.password_hash):
            raise ValidationException("用户名或密码错误")

        if not account.is_active:
            raise ValidationException("账户已被禁用")

        access_token = create_access_token(str(account.id))
        refresh_token = create_refresh_token()

        await self._store_refresh_token(account.id, refresh_token)

        await self._update_user_state(account.id, DEFAULT_APP_NAME, {
            'last_login': datetime.now().isoformat(),
            'login_count': 1,
        })

        await self._record_activity(account.id, "login", client_ip)

        self.logger.info(f"管理员登录成功: {username}")

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=24 * 3600,
            user_id=account.id
        )

    # ==================== 通用方法 ====================

    async def refresh_token(self, refresh_token: str, client_ip: str = None) -> AuthResponse:
        """刷新令牌"""
        token_hash = hash_refresh_token(refresh_token)

        stmt = select(AccountRefreshToken).where(
            AccountRefreshToken.token_hash == token_hash,
            AccountRefreshToken.is_revoked == False
        )
        result = await self.session.exec(stmt)
        token_record = result.one_or_none()

        if not token_record:
            raise ResourceNotFoundException("无效的刷新令牌")

        if token_record.expires_at < datetime.now():
            raise ValidationException("刷新令牌已过期")

        account_id = token_record.account_id

        # 撤销旧token
        token_record.is_revoked = True
        await self.session.flush()

        # 生成新token
        new_access_token = create_access_token(str(account_id))
        new_refresh_token = create_refresh_token()

        await self._store_refresh_token(account_id, new_refresh_token)

        await self._record_activity(account_id, "token_refresh", client_ip)

        self.logger.info(f"令牌刷新成功: account_id={account_id}")

        return AuthResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=24 * 3600,
            user_id=account_id
        )

    @require_login
    async def logout(self, client_ip: str = None) -> None:
        """登出当前用户"""
        account_id = get_current_user_id()
        await self._do_logout(account_id, client_ip)

    async def _do_logout(self, account_id: UUID, client_ip: str = None) -> None:
        """执行登出逻辑"""
        stmt = select(AccountRefreshToken).where(
            AccountRefreshToken.account_id == account_id,
            AccountRefreshToken.is_revoked == False
        )
        result = await self.session.exec(stmt)
        tokens = result.all()

        for token in tokens:
            token.is_revoked = True

        await self.session.flush()

        await self._update_user_state(account_id, DEFAULT_APP_NAME, {
            'status': 'offline',
            'logout_time': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        })

        await self._record_activity(account_id, "logout", client_ip)

        self.logger.info(f"用户登出成功: account_id={account_id}")

    @require_login
    async def get_current_account(self) -> Account:
        """获取当前登录账户"""
        account_id = get_current_user_id()
        account = await self.get(account_id)
        if not account:
            raise ResourceNotFoundException("账户不存在")
        return account

    @require_roles("admin", "super_admin")
    async def get_current_admin(self) -> Account:
        """获取当前管理员账户"""
        account_id = get_current_user_id()
        account = await self.get(account_id)
        if not account:
            raise ResourceNotFoundException("管理员不存在")
        return account

    async def get_profile(self, account_id: UUID, account_type: str):
        """获取账户对应的profile"""
        if account_type == "patient":
            stmt = select(Patient).where(Patient.account_id == account_id)
            result = await self.session.exec(stmt)
            return result.one_or_none()
        elif account_type == "doctor":
            stmt = select(Doctor).where(Doctor.account_id == account_id)
            result = await self.session.exec(stmt)
            return result.one_or_none()
        elif account_type == "admin":
            stmt = select(Admin).where(Admin.account_id == account_id)
            result = await self.session.exec(stmt)
            return result.one_or_none()
        return None

    async def get_current_user_id_from_token(
        self,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> str:
        """从JWT token获取当前用户ID"""
        if not credentials:
            raise AuthorizationException("未提供授权信息")
        try:
            token_data = verify_token(credentials.credentials)
            return token_data["user_id"]
        except Exception as e:
            raise AuthorizationException(
                message="无效的授权信息",
                details={"original_error": str(e)}
            )

    # ==================== 私有辅助方法 ====================

    async def _get_account_by_email_and_type(
        self,
        email: str,
        account_type: str
    ) -> Optional[Account]:
        """根据邮箱和账户类型获取账户"""
        stmt = select(Account).where(
            Account.email == email,
            Account.account_type == account_type
        )
        result = await self.session.exec(stmt)
        return result.one_or_none()

    async def _account_exists(self, email: str, account_type: str) -> bool:
        """检查账户是否存在"""
        account = await self._get_account_by_email_and_type(email, account_type)
        return account is not None

    async def _username_exists_in_patients(self, username: str) -> bool:
        """检查患者用户名是否存在"""
        stmt = select(Patient).where(Patient.username == username)
        result = await self.session.exec(stmt)
        return result.one_or_none() is not None

    async def _username_exists_in_doctors(self, username: str) -> bool:
        """检查医生用户名是否存在"""
        stmt = select(Doctor).where(Doctor.username == username)
        result = await self.session.exec(stmt)
        return result.one_or_none() is not None

    async def _username_exists_in_admins(self, username: str) -> bool:
        """检查管理员用户名是否存在"""
        stmt = select(Admin).where(Admin.username == username)
        result = await self.session.exec(stmt)
        return result.one_or_none() is not None

    async def _is_valid_email(self, email: str) -> bool:
        """验证邮箱格式"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    async def _store_refresh_token(self, account_id: UUID, refresh_token: str):
        """存储refresh token"""
        token_hash = hash_refresh_token(refresh_token)
        expires_at = get_refresh_token_expire_time()

        token_record = AccountRefreshToken(
            account_id=account_id,
            token_hash=token_hash,
            expires_at=expires_at,
            is_revoked=False
        )
        self.session.add(token_record)
        await self.session.flush()

    async def _update_user_state(self, account_id, app_name, param):
        """更新用户状态"""
        try:
            stmt = select(UserState).where(
                UserState.app_name == app_name,
                UserState.user_id == account_id
            )
            result = await self.session.exec(stmt)
            user_state: UserState = result.one_or_none()

            if user_state:
                update_stmt = update(UserState).where(
                    UserState.user_id == user_state.user_id,
                ).values(
                    state=param,
                    update_time=datetime.now()
                )
                await self.session.exec(update_stmt)
                await self.session.flush()
            else:
                stmt = insert(UserState).values(
                    user_id=account_id,
                    app_name=app_name,
                    state=param,
                    update_time=datetime.now()
                )
                await self.session.exec(stmt)
                await self.session.flush()
        except Exception as e:
            self.logger.error(f"更新用户状态失败: {str(e)}")

    async def _record_activity(
        self,
        account_id: UUID,
        activity_type: str,
        ip_address: str = None
    ):
        """记录账户活动"""
        try:
            activity = AccountActivity(
                account_id=account_id,
                activity_type=activity_type,
                ip_address=ip_address,
                created_at=datetime.now()
            )
            self.session.add(activity)
            await self.session.flush()
            self.logger.info(f"账户活动已记录: {activity_type}, account_id={account_id}")
        except Exception as e:
            self.logger.warning(f"记录账户活动失败: {str(e)}")
