"""
模型配置控制器

管理员：管理供应商和内置模型配置
用户：配置API Key和自定义参数
"""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, Request

from app.src.dependencies.dependency import UserServiceDep, LanguageModelServiceDep
from app.src.response.response_models import BaseResponse
from app.src.schema.model_config_schema import (
    ModelProviderCreate, ModelProviderUpdate, ModelProviderResponse,
    ModelConfigCreate, ModelConfigUpdate, ModelConfigResponse,
    UserModelConfigCreate, UserModelConfigUpdate, UserModelConfigResponse
)
from app.src.response.utils import success_200
from app.src.utils import get_logger

router = APIRouter(prefix="/api/v1/models", tags=["模型配置"])
logger = get_logger("model_config_controller")



# ==================== 公共接口 ====================

@router.get(
    "/providers",
    summary="获取所有供应商及模型列表",
    response_model=BaseResponse[List[dict]]
)
async def get_providers_with_models(
    request: Request,
    model_service: LanguageModelServiceDep
):
    """获取所有启用的供应商及其模型列表（公开接口）"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id

    result = await model_service.get_providers_with_models()

    return success_200(
        data=result,
        message="获取供应商列表成功",
        request_id=request_id,
        host_id=client_ip
    )


# ==================== 管理员接口：供应商管理 ====================

@router.post(
    "/admin/providers",
    summary="创建供应商（管理员）",
    response_model=BaseResponse[dict]
)
async def create_provider(
    request: Request,
    data: ModelProviderCreate,
    model_service: LanguageModelServiceDep,
):
    """创建模型供应商（需要管理员权限）"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id

    provider = await model_service.provider_service.create_provider(data)

    return success_200(
        data={"id": str(provider.id), "name": provider.name},
        message="创建供应商成功",
        request_id=request_id,
        host_id=client_ip
    )


@router.put(
    "/admin/providers/{provider_id}",
    summary="更新供应商（管理员）",
    response_model=BaseResponse[dict]
)
async def update_provider(
    request: Request,
    provider_id: UUID,
    data: ModelProviderUpdate,
    model_service: LanguageModelServiceDep,
):
    """更新模型供应商（需要管理员权限）"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id



    provider = await model_service.provider_service.update_provider(provider_id, data)

    return success_200(
        data={"id": str(provider.id), "name": provider.name},
        message="更新供应商成功",
        request_id=request_id,
        host_id=client_ip
    )


@router.delete(
    "/admin/providers/{provider_id}",
    summary="删除供应商（管理员）",
    response_model=BaseResponse[None]
)
async def delete_provider(
    request: Request,
    provider_id: UUID,
    model_service: LanguageModelServiceDep,

):
    """删除模型供应商（需要管理员权限，内置供应商不可删除）"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id



    await model_service.provider_service.delete_provider(provider_id)

    return success_200(
        data=None,
        message="删除供应商成功",
        request_id=request_id,
        host_id=client_ip
    )


# ==================== 管理员接口：模型配置管理 ====================

@router.post(
    "/admin/configs",
    summary="创建模型配置（管理员）",
    response_model=BaseResponse[dict]
)
async def create_model_config(
    request: Request,
    data: ModelConfigCreate,
    model_service: LanguageModelServiceDep,
):
    """创建模型配置（需要管理员权限）"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id



    config = await model_service.model_config_service.create_model_config(data)

    return success_200(
        data={"id": str(config.id), "model_name": config.model_name},
        message="创建模型配置成功",
        request_id=request_id,
        host_id=client_ip
    )


@router.put(
    "/admin/configs/{config_id}",
    summary="更新模型配置（管理员）",
    response_model=BaseResponse[dict]
)
async def update_model_config(
    request: Request,
    config_id: UUID,
    data: ModelConfigUpdate,
    model_service: LanguageModelServiceDep,
):
    """更新模型配置（需要管理员权限）"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id


    config = await model_service.model_config_service.update_model_config(config_id, data)

    return success_200(
        data={"id": str(config.id), "model_name": config.model_name},
        message="更新模型配置成功",
        request_id=request_id,
        host_id=client_ip
    )


@router.delete(
    "/admin/configs/{config_id}",
    summary="删除模型配置（管理员）",
    response_model=BaseResponse[None]
)
async def delete_model_config(
    request: Request,
    config_id: UUID,
    model_service: LanguageModelServiceDep,
):
    """删除模型配置（需要管理员权限）"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id



    await model_service.model_config_service.delete_model_config(config_id)

    return success_200(
        data=None,
        message="删除模型配置成功",
        request_id=request_id,
        host_id=client_ip
    )


# ==================== 用户接口：个人模型配置 ====================

@router.get(
    "/user/configs",
    summary="获取用户的模型配置列表",
    response_model=BaseResponse[List[UserModelConfigResponse]]
)
async def get_user_configs(
    request: Request,
    model_service: LanguageModelServiceDep,

):
    """获取当前用户的所有模型配置"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id


    configs = await model_service.get_my_configs()

    # 转换为响应模型
    result = []
    for config in configs:
        provider = await model_service.provider_service.get(config.provider_id)
        model_config = None
        if config.model_config_id:
            model_config = await model_service.model_config_service.get(config.model_config_id)

        result.append(UserModelConfigResponse(
            id=config.id,
            provider_id=config.provider_id,
            provider_name=provider.name if provider else None,
            provider_label=provider.label if provider else None,
            model_config_id=config.model_config_id,
            model_name=model_config.model_name if model_config else None,
            model_label=model_config.label if model_config else None,
            custom_model_name=config.custom_model_name,
            has_api_key=bool(config.api_key),
            base_url=config.base_url,
            alias=config.alias,
            is_default=config.is_default,
            is_enabled=config.is_enabled
        ))

    return success_200(
        data=result,
        message="获取用户模型配置成功",
        request_id=request_id,
        host_id=client_ip
    )


@router.post(
    "/user/configs",
    summary="创建用户模型配置",
    response_model=BaseResponse[dict]
)
async def create_user_config(
    request: Request,
    data: UserModelConfigCreate,
    model_service: LanguageModelServiceDep,

):
    """用户创建自己的模型配置（必须提供API Key）"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id

    config = await model_service.create_my_config( data)

    return success_200(
        data={"id": str(config.id)},
        message="创建用户模型配置成功",
        request_id=request_id,
        host_id=client_ip
    )


@router.put(
    "/user/configs/{config_id}",
    summary="更新用户模型配置",
    response_model=BaseResponse[dict]
)
async def update_user_config(
    request: Request,
    config_id: UUID,
    data: UserModelConfigUpdate,
    model_service: LanguageModelServiceDep,

):
    """用户更新自己的模型配置"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id


    config = await model_service.update_my_config(config_id,  data)

    return success_200(
        data={"id": str(config.id)},
        message="更新用户模型配置成功",
        request_id=request_id,
        host_id=client_ip
    )


@router.delete(
    "/user/configs/{config_id}",
    summary="删除用户模型配置",
    response_model=BaseResponse[None]
)
async def delete_user_config(
    request: Request,
    config_id: UUID,
    model_service: LanguageModelServiceDep,
):
    """用户删除自己的模型配置"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id


    await model_service.delete_my_config(config_id)

    return success_200(
        data=None,
        message="删除用户模型配置成功",
        request_id=request_id,
        host_id=client_ip
    )


@router.post(
    "/user/configs/{config_id}/default",
    summary="设置为默认配置",
    response_model=BaseResponse[dict]
)
async def set_default_config(
    request: Request,
    config_id: UUID,
    model_service: LanguageModelServiceDep,

):
    """将指定配置设置为用户的默认���型配置"""
    client_ip = request.state.client_ip
    request_id = request.state.request_id


    config = await model_service.set_my_default(config_id)

    return success_200(
        data={"id": str(config.id), "is_default": config.is_default},
        message="设置默认配置成功",
        request_id=request_id,
        host_id=client_ip
    )
