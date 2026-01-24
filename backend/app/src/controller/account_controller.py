"""
账户控制器 - 统一的三端账户管理

处理患者、医生、管理员的注册、登录、登出
"""

from uuid import UUID
from fastapi import APIRouter, Request, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.src.service.account_service import AccountService
from app.src.schema.user_schema import (
    UserCreate, UserLogin, AdminCreate, AdminLogin, AdminResponse,
    AuthResponse, RefreshRequest
)
from app.src.response.response_models import BaseResponse
from app.src.response.utils import success_200
from app.src.utils import get_logger
from app.src.common.config.prosgresql_config import get_db

router = APIRouter(tags=["账户管理"])
logger = get_logger("account_controller")


def get_account_service(session: AsyncSession = Depends(get_db)) -> AccountService:
    """获取账户服务依赖"""
    return AccountService(session)


# ==================== 患者端接口 ====================

@router.post("/api/v1/users/register", summary="患者注册", response_model=BaseResponse[UUID])
async def register_patient(
    request: Request,
    user_data: UserCreate,
    account_service: AccountService = Depends(get_account_service)
):
    """患者注册"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id

    logger.info(f"开始患者注册, email: {user_data.email}, IP: {client_ip}")

    account_id, patient_id = await account_service.register_patient(
        email=user_data.email,
        password=user_data.password,
        username=user_data.username,
        real_name=user_data.real_name,
        phone=user_data.phone,
        gender=user_data.gender,
        birth_date=user_data.birth_date,
        constitution_type=user_data.constitution_type,
        client_ip=client_ip
    )

    logger.info(f"患者注册成功, account_id: {account_id}")

    return success_200(
        data=account_id,
        message="用户注册成功",
        request_id=request_id,
        host_id=client_ip
    )


@router.post("/api/v1/users/login", summary="患者登录", response_model=BaseResponse[AuthResponse])
async def login_patient(
    request: Request,
    login_data: UserLogin,
    account_service: AccountService = Depends(get_account_service)
):
    """患者登录"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id

    logger.info(f"开始患者登录, email: {login_data.email}, IP: {client_ip}")

    auth_response = await account_service.login_patient(
        email=login_data.email,
        password=login_data.password,
        client_ip=client_ip
    )

    logger.info(f"患者登录成功, account_id: {auth_response.user_id}")

    return success_200(
        data=auth_response,
        message="登录成功",
        request_id=request_id,
        host_id=client_ip
    )


@router.get("/api/v1/users/me", summary="获取当前患者信息", response_model=BaseResponse[dict])
async def get_current_patient(
    request: Request,
    account_service: AccountService = Depends(get_account_service)
):
    """获取当前患者信息"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id

    account = await account_service.get_current_account()
    profile = await account_service.get_profile(account.id, account.account_type)

    return success_200(
        data={
            "id": account.id,
            "email": account.email,
            "username": profile.username if profile else None,
            "real_name": profile.real_name if profile else None,
            "phone": profile.phone if profile else None,
            "gender": profile.gender if profile else None,
            "birth_date": profile.birth_date.isoformat() if profile and profile.birth_date else None,
            "constitution_type": profile.constitution_type if profile else None,
            "avatar_url": profile.avatar_url if profile else None,
            "is_active": account.is_active,
            "created_at": account.created_at.isoformat()
        },
        message="获取用户信息成功",
        request_id=request_id,
        host_id=client_ip
    )


@router.post("/api/v1/users/logout", summary="患者登出", response_model=BaseResponse[None])
async def logout_patient(
    request: Request,
    account_service: AccountService = Depends(get_account_service)
):
    """患者登出"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id

    logger.info("开始患者登出")
    await account_service.logout(client_ip)
    logger.info("患者登出成功")

    return success_200(
        data=None,
        message="用户登出成功",
        request_id=request_id,
        host_id=client_ip
    )


# ==================== 医生端接口 ====================

@router.post("/api/v1/professional/register", summary="医生注册", response_model=BaseResponse[UUID])
async def register_doctor(
    request: Request,
    user_data: UserCreate,
    account_service: AccountService = Depends(get_account_service)
):
    """医生注册"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id

    logger.info(f"开始医生注册, email: {user_data.email}, IP: {client_ip}")

    account_id, doctor_id = await account_service.register_doctor(
        email=user_data.email,
        password=user_data.password,
        username=user_data.username,
        real_name=user_data.real_name,
        phone=user_data.phone,
        gender=user_data.gender,
        client_ip=client_ip
    )

    logger.info(f"医生注册成功, account_id: {account_id}")

    return success_200(
        data=account_id,
        message="医生注册成功",
        request_id=request_id,
        host_id=client_ip
    )


@router.post("/api/v1/professional/login", summary="医生登录", response_model=BaseResponse[AuthResponse])
async def login_doctor(
    request: Request,
    login_data: UserLogin,
    account_service: AccountService = Depends(get_account_service)
):
    """医生登录"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id

    logger.info(f"开始医生登录, email: {login_data.email}, IP: {client_ip}")

    auth_response = await account_service.login_doctor(
        email=login_data.email,
        password=login_data.password,
        client_ip=client_ip
    )

    logger.info(f"医生登录成功, account_id: {auth_response.user_id}")

    return success_200(
        data=auth_response,
        message="登录成功",
        request_id=request_id,
        host_id=client_ip
    )


@router.get("/api/v1/professional/me", summary="获取当前医生信息", response_model=BaseResponse[dict])
async def get_current_doctor(
    request: Request,
    account_service: AccountService = Depends(get_account_service)
):
    """获取当前医生信息"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id

    account = await account_service.get_current_account()
    profile = await account_service.get_profile(account.id, account.account_type)

    return success_200(
        data={
            "id": account.id,
            "email": account.email,
            "username": profile.username if profile else None,
            "real_name": profile.real_name if profile else None,
            "phone": profile.phone if profile else None,
            "gender": profile.gender if profile else None,
            "avatar_url": profile.avatar_url if profile else None,
            "license_no": profile.license_no if profile else None,
            "department": profile.department if profile else None,
            "hospital": profile.hospital if profile else None,
            "specialty": profile.specialty if profile else None,
            "title": profile.title if profile else None,
            "is_active": account.is_active,
            "created_at": account.created_at.isoformat()
        },
        message="获取医生信息成功",
        request_id=request_id,
        host_id=client_ip
    )


@router.post("/api/v1/professional/logout", summary="医生登出", response_model=BaseResponse[None])
async def logout_doctor(
    request: Request,
    account_service: AccountService = Depends(get_account_service)
):
    """医生登出"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id

    logger.info("开始医生登出")
    await account_service.logout(client_ip)
    logger.info("医生登出成功")

    return success_200(
        data=None,
        message="医生登出成功",
        request_id=request_id,
        host_id=client_ip
    )


# ==================== 管理员端接口 ====================

@router.post("/api/v1/admin/register", summary="管理员注册", response_model=BaseResponse[UUID])
async def register_admin(
    request: Request,
    admin_data: AdminCreate,
    account_service: AccountService = Depends(get_account_service)
):
    """管理员注册"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id

    logger.info(f"开始管理员注册, username: {admin_data.username}, IP: {client_ip}")

    account_id, admin_id = await account_service.register_admin(
        username=admin_data.username,
        password=admin_data.password,
        client_ip=client_ip
    )

    logger.info(f"管理员注册成功, account_id: {account_id}")

    return success_200(
        data=account_id,
        message="管理员注册成功",
        request_id=request_id,
        host_id=client_ip
    )


@router.post("/api/v1/admin/login", summary="管理员登录", response_model=BaseResponse[AuthResponse])
async def login_admin(
    request: Request,
    login_data: AdminLogin,
    account_service: AccountService = Depends(get_account_service)
):
    """管理员登录"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id

    logger.info(f"开始管理员登录, username: {login_data.username}, IP: {client_ip}")

    auth_response = await account_service.login_admin(
        username=login_data.username,
        password=login_data.password,
        client_ip=client_ip
    )

    logger.info(f"管理员登录成功, account_id: {auth_response.user_id}")

    return success_200(
        data=auth_response,
        message="登录成功",
        request_id=request_id,
        host_id=client_ip
    )


@router.get("/api/v1/admin/me", summary="获取当前管理员信息", response_model=BaseResponse[AdminResponse])
async def get_current_admin(
    request: Request,
    account_service: AccountService = Depends(get_account_service)
):
    """获取当前管理员信息"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id

    account = await account_service.get_current_admin()
    profile = await account_service.get_profile(account.id, account.account_type)

    response = AdminResponse(
        id=account.id,
        username=profile.username if profile else "admin",
        role=account.account_type,
        avatar_url=profile.avatar_url if profile else None,
        is_active=account.is_active,
        created_at=account.created_at
    )

    return success_200(
        data=response,
        message="获取管理员信息成功",
        request_id=request_id,
        host_id=client_ip
    )


@router.post("/api/v1/admin/logout", summary="管理员登出", response_model=BaseResponse[None])
async def logout_admin(
    request: Request,
    account_service: AccountService = Depends(get_account_service)
):
    """管理员登出"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id

    logger.info("开始管理员登出")
    await account_service.logout(client_ip)
    logger.info("管理员登出成功")

    return success_200(
        data=None,
        message="管理员登出成功",
        request_id=request_id,
        host_id=client_ip
    )


# ==================== 通用接口 ====================

@router.post("/api/v1/users/refresh", summary="刷新令牌", response_model=BaseResponse[AuthResponse])
async def refresh_token(
    request: Request,
    refresh_data: RefreshRequest,
    account_service: AccountService = Depends(get_account_service)
):
    """刷新访问令牌"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id

    logger.info("开始刷新令牌")

    auth_response = await account_service.refresh_token(
        refresh_token=refresh_data.refresh_token,
        client_ip=client_ip
    )

    logger.info("令牌刷新成功")

    return success_200(
        data=auth_response,
        message="token刷新成功",
        request_id=request_id,
        host_id=client_ip
    )
