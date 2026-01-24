"""
模型配置控制器

管理员：管理供应商和内置模型配置
用户：配置API Key和自定义参数
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Request
from app.src.dependencies.dependency import LanguageModelServiceDep, get_model_provider_service
from app.src.response.response_models import BaseResponse
from app.src.schema.model_config_schema import (
    ModelProviderCreate, ModelProviderUpdate, ModelProviderResponse,
    ModelConfigCreate, ModelConfigUpdate, ModelConfigResponse,
    ModelProviderDelete,
    ModelConfigDelete,
    ProviderApiKeyVerify,
)
from app.src.response.utils import success_200
from app.src.utils import get_logger

from app.src.service.language_model_service import ModelProviderService

from backend.app.src.dependencies.dependency import get_model_config_service
from backend.app.src.service.language_model_service import ModelConfigService

router = APIRouter(prefix="/api/v1", tags=["模型配置"])
logger = get_logger("model_config_controller")



# ==================== 公共接口 ====================

@router.get(
    "/providers_with_models",
    summary="获取所有供应商及模型列表",
    response_model=BaseResponse[List[dict]]
)
async def get_providers_with_models(
    request: Request,
    model_service: LanguageModelServiceDep
):
    """获取所有供应商及其模型列表（公开接口）
    
    返回数据包含：
    - 系统级供应商信息 (name, label, models...)
    - 用户级配置信息 (has_api_key, is_enabled...)
    """
    client_ip = request.state.client_ip
    request_id = request.state.request_id

    # 获取当前用户信息（如果已登录）
    from app.src.common.context import get_current_user_id
    try:
        user_id = get_current_user_id()
    except:
        user_id = None

    # 获取整合后的数据
    result = await model_service.get_providers_with_models(user_id=user_id)

    if result is None:
        result=[]
    return success_200(
        data=result,
        message="获取供应商列表成功",
        request_id=request_id,
        host_id=client_ip
    )

#获取所有内置提供商及其模型列表
@router.get(
    "/builtin/providers_with_models",
    summary="获取所有内置供应商及模型列表",
    response_model=BaseResponse[List[dict]]
)
async def get_builtin_providers_with_models(
    request: Request,
    model_service: LanguageModelServiceDep
):
    """获取所有内置供应商及其模型列表（公开接口）
    注意：此接口不返回任何用户配置信息
    """
    client_ip = request.state.client_ip
    request_id = request.state.request_id

    # user_id=None 表示只获取系统模板，不混合用户配置
    result = await model_service.get_providers_with_models(user_id=None)
    
    if result is None:
        result=[]
    return success_200(
        data=result,
        message="获取内置供应商列表成功",
        request_id=request_id,
        host_id=client_ip
    )


# ==================== 供应商管理 ====================

@router.post(
    "/provider/create",
    summary="创建供应商",
    response_model=BaseResponse[dict]
)
async def create_provider(
    request: Request,
    data: ModelProviderCreate,
    provider_service:ModelProviderService=Depends(get_model_provider_service),
):
    """创建模型供应商
    - 管理员：创建系统级供应商 (owner_id = None)
    - 普通用户：创建私有供应商 (owner_id = user_id)
    """
    client_ip = request.state.client_ip
    request_id = request.state.request_id

    from app.src.common.context import get_user_roles, get_current_user_id
    
    # 获取上下文信息
    roles = []
    user_id = None
    try:
        roles = get_user_roles()
        user_id = get_current_user_id()
    except:
        pass
        
    is_admin = "admin" in roles
    if not user_id:
        # 如果未登录且无法获取ID，可能需要抛出异常或处理
        pass

    # 调用 Service 安全方法
    provider = await provider_service.create_provider_safe(data, user_id, is_admin)

    return success_200(
        data={"id": str(provider.id), "name": provider.name},
        message="创建供应商成功",
        request_id=request_id,
        host_id=client_ip
    )


@router.post(
    "/provider/update",
    summary="更新供应商",
    response_model=BaseResponse[dict]
)
async def update_provider(
    request: Request,
    data: ModelProviderUpdate,
    provider_service:ModelProviderService=Depends(get_model_provider_service),
):
    """更新模型供应商
    - Admin: 更新 SystemModelProvider (全局影响)
    - User: 更新 UserProviderConfig (仅影响自己)
    """
    client_ip = request.state.client_ip
    request_id = request.state.request_id

    from app.src.common.context import get_user_roles, get_current_user_id
    
    roles = []
    user_id = None
    try:
        roles = get_user_roles()
        user_id = get_current_user_id()
    except:
        pass
        
    is_admin = "admin" in roles
    
    result = await provider_service.update_provider_safe(data.provider_id, data, user_id, is_admin)
    
    # 构造返回
    if hasattr(result, "name"): # SystemModelProvider
        res_data = {"id": str(result.id), "name": result.name}
        msg = "更新系统供应商成功"
    else: # UserProviderConfig
        res_data = {"id": str(result.id)}
        msg = "更新个人配置成功"

    return success_200(
        data=res_data,
        message=msg,
        request_id=request_id,
        host_id=client_ip
    )


@router.post(
    "/provider/delete",
    summary="删除供应商",
    response_model=BaseResponse[None]
)
async def delete_provider(
    request: Request,
    data: ModelProviderDelete,
    provider_service:ModelProviderService=Depends(get_model_provider_service),

):
    """删除模型供应商
    - 管理员：可删除任意供应商（慎用）
    - 普通用户：仅可删除自己创建的私有供应商
    """
    client_ip = request.state.client_ip
    request_id = request.state.request_id

    from app.src.common.context import get_user_roles, get_current_user_id
    
    roles = []
    user_id = None
    try:
        roles = get_user_roles()
        user_id = get_current_user_id()
    except:
        pass
    
    is_admin = "admin" in roles
    
    # 调用 Service 安全方法
    await provider_service.delete_provider_safe(data.provider_id, user_id, is_admin)

    return success_200(
        data=None,
        message="删除供应商成功",
        request_id=request_id,
        host_id=client_ip
    )

@router.post(
    "/provider/verify_api_key",
    summary="验证供应商API Key",
    response_model=BaseResponse[dict]
)
async def verify_provider_api_key(
    request: Request,
    data: ProviderApiKeyVerify,
    provider_service: ModelProviderService = Depends(get_model_provider_service),
):
    """验证供应商API Key是否有效"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id

    result = await provider_service.verify_api_key(data.provider_id, data.api_key, data.base_url, data.model_name)

    return success_200(
        data=result,
        message="验证成功" if result.get("valid") else "验证失败",
        request_id=request_id,
        host_id=client_ip
    )


# ==================== 管理员接口：模型配置管理 ====================

@router.post(
    "/model/config/create",
    summary="创建模型配置",
    response_model=BaseResponse[dict]
)
async def create_model_config(
    request: Request,
    data: ModelConfigCreate,
    model_config_service:ModelConfigService=Depends(get_model_config_service),
):
    """创建模型配置
    - 管理员：可在任意供应商下创建
    - 普通用户：仅可在自己拥有的供应商下创建
    """
    client_ip = request.state.client_ip
    request_id = request.state.request_id
    
    from app.src.common.context import get_user_roles, get_current_user_id
    
    roles = []
    user_id = None
    try:
        roles = get_user_roles()
        user_id = get_current_user_id()
    except:
        pass
    
    is_admin = "admin" in roles

    # 调用 Service 安全方法
    config = await model_config_service.create_model_config_safe(data, user_id, is_admin)

    return success_200(
        data={"id": str(config.id), "model_name": config.model_name},
        message="创建模型配置成功",
        request_id=request_id,
        host_id=client_ip
    )


@router.post(
    "/model/config/update",
    summary="更新模型配置",
    response_model=BaseResponse[dict]
)
async def update_model_config(
    request: Request,
    data: ModelConfigUpdate,
    model_config_service: ModelConfigService = Depends(get_model_config_service),
):
    """更新模型配置
    - 管理员 & 内置模型：更新系统定义
    - 普通用户 OR (管理员 & 非内置字段更新)：更新用户偏好 (UserModelPreference)
    """
    client_ip = request.state.client_ip
    request_id = request.state.request_id

    from app.src.common.context import get_user_roles, get_current_user_id
    
    roles = []
    user_id = None
    try:
        roles = get_user_roles()
        user_id = get_current_user_id()
    except:
        pass
    
    is_admin = "admin" in roles
    
    # 调用 Service 安全方法
    result = await model_config_service.update_model_config_safe(
        data.model_config_id, data, user_id, is_admin
    )
    
    # 构造返回
    if hasattr(result, "model_name"): # SystemModelDefinition
        res_id = result.id
        res_name = result.model_name
        msg = "更新系统模型配置成功"
    else: # UserModelPreference
        res_id = result.model_def_id
        res_name = "" # 偏好对象没有名称，暂留空
        msg = "更新个人模型偏好成功"

    return success_200(
        data={"id": str(res_id), "model_name": res_name},
        message=msg,
        request_id=request_id,
        host_id=client_ip
    )


@router.post(
    "/model/config/delete",
    summary="删除模型配置",
    response_model=BaseResponse[None]
)
async def delete_model_config(
    request: Request,
    data: ModelConfigDelete,
    model_config_service:ModelConfigService=Depends(get_model_config_service),
):
    """删除模型配置
    - 管理员：可删除任意模型
    - 普通用户：仅可删除自己创建的模型
    """
    client_ip = request.state.client_ip
    request_id = request.state.request_id

    from app.src.common.context import get_user_roles, get_current_user_id
    
    roles = []
    user_id = None
    try:
        roles = get_user_roles()
        user_id = get_current_user_id()
    except:
        pass
    
    is_admin = "admin" in roles

    # 调用 Service 安全方法
    await model_config_service.delete_model_config_safe(
        data.model_config_id, user_id, is_admin
    )

    return success_200(
        data=None,
        message="删除模型配置成功",
        request_id=request_id,
        host_id=client_ip
    )
