"""
管理员控制器
"""

from uuid import UUID

from fastapi import APIRouter, Request

from app.src.dependencies.dependency import UserServiceDep
from app.src.response.response_models import BaseResponse
from app.src.schema.user_schema import AdminCreate, AdminLogin, AdminAuthResponse, AdminResponse
from app.src.response.utils import success_200
from app.src.utils import get_logger

router = APIRouter(prefix="/api/v1/admin", tags=["管理员"])
logger = get_logger("admin_controller")


@router.post("/register", summary="管理员注册", response_model=BaseResponse[UUID])
async def register(request: Request, admin_data: AdminCreate, user_service: UserServiceDep):
    """管理员注册"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id
    logger.info(f"开始注册管理员, IP: {client_ip}")
    resp = await user_service.create_admin(admin_data, client_ip)
    logger.info(f"管理员注册成功, IP: {client_ip}")
    return success_200(data=resp, message="管理员注册成功", request_id=request_id, host_id=client_ip)


@router.post("/login", summary="管理员登录", response_model=BaseResponse[AdminAuthResponse])
async def login(request: Request, login_data: AdminLogin, user_service: UserServiceDep):
    """管理员登录"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id
    logger.info(f"开始管理员登录, IP: {client_ip}")
    resp = await user_service.authenticate_admin(login_data.username, login_data.password, client_ip)
    logger.info(f"管理员登录成功, IP: {client_ip}")
    return success_200(data=resp, message="登录成功", request_id=request_id, host_id=client_ip)


@router.get("/me", summary="获取当前管理员信息", response_model=BaseResponse[AdminResponse])
async def get_current_admin(request: Request, user_service: UserServiceDep):
    """获取当前管理员信息"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id
    admin = await user_service.get_admin_me()
    response = AdminResponse(
        id=admin.id,
        username=admin.username,
        role=admin.role,
        avatar_url=admin.avatar_url,
        is_active=admin.is_active,
        created_at=admin.created_at
    )
    return success_200(data=response, message="获取管理员信息成功", request_id=request_id, host_id=client_ip)


@router.post("/logout", summary="管理员登出", response_model=BaseResponse[None])
async def logout(request: Request, user_service: UserServiceDep):
    """管理员登出"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id
    logger.info("开始管理员登出")
    await user_service.admin_logout(client_ip)
    logger.info("管理员登出成功")
    return success_200(data=None, message="管理员登出成功", request_id=request_id, host_id=client_ip)
