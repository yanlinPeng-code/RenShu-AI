from uuid import UUID

from fastapi import APIRouter, Request, BackgroundTasks

from app.src.dependencies.dependency import UserServiceDep
from app.src.model import User
from app.src.response.response_models import BaseResponse
from app.src.schema.user_schema import UserCreate, AuthResponse, UserLogin, RefreshResponse, RefreshRequest
from app.src.response.utils import success_200
from app.src.utils import get_logger
router = APIRouter(prefix="/api/v1/users", tags=["用户管理"])
logger = get_logger("user_controller")


@router.post("/register", summary="用户注册", response_model=BaseResponse[UUID])
async def register(request: Request,
                   user_data: UserCreate,
                   user_service: UserServiceDep,

                   ):
    """用户注册"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id
    logger.info(f"开始注册用户, IP: {client_ip}")
    resp = await user_service.create_user(user_data, client_ip)
    logger.info(f"用户注册成功, IP: {client_ip}")
    return success_200(data=resp, message="用户注册成功", request_id=request_id, host_id=client_ip)


@router.post("/login", summary="用户登录", response_model=BaseResponse[AuthResponse])
async def login(request: Request, login_data: UserLogin, user_service: UserServiceDep):
    """用户登录"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id
    logger.info(f"开始用户登录, IP: {client_ip}")
    resp = await user_service.authenticate_user(login_data.email, login_data.password, client_ip)
    logger.info(f"用户登录成功, IP: {client_ip}")
    return success_200(data=resp, message="登录成功", request_id=request_id, host_id=client_ip)


@router.post("/refresh", summary="刷新令牌", response_model=BaseResponse[RefreshResponse])
async def refresh(request: Request, refresh_data: RefreshRequest, user_service: UserServiceDep):
    """刷新令牌"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id
    logger.info("开始刷新令牌")
    response = await user_service.refresh_token(refresh_data.refresh_token, client_ip)
    logger.info("令牌刷新成功")
    return success_200(data=response, message="token刷新成功", request_id=request_id, host_id=client_ip)


@router.get("/me", summary="获取当前用户信息", response_model=BaseResponse[User])
async def get_current_user(request: Request, user_service: UserServiceDep):
    """获取当前用户信息"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id
    user = await user_service.get_me()
    return success_200(data=user, message="获取用户信息成功", request_id=request_id, host_id=client_ip)


@router.post("/logout", summary="用户登出", response_model=BaseResponse[None])
async def logout(request: Request, user_service: UserServiceDep):
    """用户登出"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id
    logger.info("开始用户登出")
    await user_service.logout_me(client_ip)
    logger.info("用户登出成功")
    return success_200(data=None, message="用户登出成功", request_id=request_id, host_id=client_ip)
