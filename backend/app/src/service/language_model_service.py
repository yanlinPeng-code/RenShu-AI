"""
语言模型服务

管理员层：管理供应商和内置模型配置
用户层：配置 API Key 和自定义参数
"""
import logging
from typing import Any, Optional, List, Dict
from uuid import UUID
from copy import deepcopy

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.src.core.language_model.entities.model_entity import BaseLanguageModel, ModelFeature
from app.src.core.language_model.providers import get_chat_class
from app.src.core.language_model.default_models import DEFAULT_PROVIDERS, DEFAULT_MODELS

from app.src.response.exception.exceptions import ResourceNotFoundException, BusinessException
from app.src.service.base_service import BaseService
from app.src.core.decorators import require_login, require_roles
from app.src.core.context import get_current_user_id

from app.src.model.model_config_models import ModelProvider, ModelConfig, UserModelConfig
from app.src.schema.model_config_schema import ModelProviderCreate, ModelProviderUpdate, ModelConfigCreate, \
    ModelConfigUpdate, UserModelConfigUpdate, UserModelConfigCreate


# ==================== 管理员服务 ====================

class ModelProviderService(BaseService[ModelProvider]):
    """模型供应商服务（管理员使用）"""

    def __init__(self, session: AsyncSession):
        super().__init__(ModelProvider, session)

    async def get_all_providers(self, enabled_only: bool = True) -> List[ModelProvider]:
        """获取所有供应商"""
        query = select(ModelProvider)
        if enabled_only:
            query = query.where(ModelProvider.is_enabled == True)
        query = query.order_by(ModelProvider.position)
        result = await self.session.exec(query)
        return list(result.all())

    async def get_provider_by_name(self, name: str) -> Optional[ModelProvider]:
        """根据名称获取供应商"""
        query = select(ModelProvider).where(ModelProvider.name == name)
        result = await self.session.exec(query)
        return result.first()

    # ========== 管理员方法（带装饰器） ==========

    @require_roles("admin", "super_admin")
    async def create_provider(self, data: ModelProviderCreate) -> ModelProvider:
        """创建供应商（需要管理员权限）"""
        existing = await self.get_provider_by_name(data.name)
        if existing:
            raise BusinessException(f"供应商 '{data.name}' 已存在")

        provider = ModelProvider(**data.model_dump())
        return await self.create(provider)

    @require_roles("admin", "super_admin")
    async def update_provider(self, provider_id: UUID, data: ModelProviderUpdate) -> ModelProvider:
        """更新供应商（需要管理员权限）"""
        provider = await self.get(provider_id)
        if not provider:
            raise ResourceNotFoundException("供应商不存在")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(provider, key, value)

        return await self.update(provider)

    @require_roles("admin", "super_admin")
    async def delete_provider(self, provider_id: UUID) -> None:
        """删除供应商（需要管理员权限）"""
        provider = await self.get(provider_id)
        if not provider:
            raise ResourceNotFoundException("供应商不存在")

        if provider.is_builtin:
            raise BusinessException("内置供应商不可删除")

        await self.delete(provider)

    async def init_default_providers(self) -> None:
        """初始化默认供应商（仅在数据库为空时调用）"""
        existing = await self.get_all_providers(enabled_only=False)
        if existing:
            return

        for provider_data in DEFAULT_PROVIDERS:
            provider = ModelProvider(**provider_data)
            self.session.add(provider)

        await self.session.flush()


class ModelConfigService(BaseService[ModelConfig]):
    """模型配置服务（管理员使用）"""

    def __init__(self,
                 session: AsyncSession,
                 provider_service:ModelProviderService):
        super().__init__(ModelConfig, session)
        self.provider_service = provider_service

    async def get_models_by_provider(
        self,
        provider_id: UUID,
        enabled_only: bool = True
    ) -> List[ModelConfig]:
        """获取供应商下的所有模型"""
        query = select(ModelConfig).where(ModelConfig.provider_id == provider_id)
        if enabled_only:
            query = query.where(ModelConfig.is_enabled == True)
        query = query.order_by(ModelConfig.position)
        result = await self.session.exec(query)
        return list(result.all())

    async def get_model_by_name(
        self,
        provider_name: str,
        model_name: str
    ) -> Optional[ModelConfig]:
        """根据供应商名称和模型名称获取模型配置"""
        provider = await self.provider_service.get_provider_by_name(provider_name)
        if not provider:
            return None

        query = select(ModelConfig).where(
            ModelConfig.provider_id == provider.id,
            ModelConfig.model_name == model_name
        )
        result = await self.session.exec(query)
        return result.first()

    async def get_model_by_id(self, model_id: UUID) -> Optional[ModelConfig]:
        """根据ID获取模型配置"""
        return await self.get(model_id)

    # ========== 管理员方法（带装饰器） ==========

    @require_roles("admin", "super_admin")
    async def create_model_config(self, data: ModelConfigCreate) -> ModelConfig:
        """创建模型配置（需要管理员权限）"""
        model_config = ModelConfig(**data.model_dump())
        return await self.create(model_config)

    @require_roles("admin", "super_admin")
    async def update_model_config(
        self,
        config_id: UUID,
        data: ModelConfigUpdate
    ) -> ModelConfig:
        """更新模型配置（需要管理员权限）"""
        config = await self.get(config_id)
        if not config:
            raise ResourceNotFoundException("模型配置不存在")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(config, key, value)

        return await self.update(config)

    @require_roles("admin", "super_admin")
    async def delete_model_config(self, config_id: UUID) -> None:
        """删除模型配置（需要管理员权限）"""
        config = await self.get(config_id)
        if not config:
            raise ResourceNotFoundException("模型配置不存在")

        await self.delete(config)

    async def init_default_models(self) -> None:
        """初始化默认模型配置"""
        await self.provider_service.init_default_providers()

        query = select(ModelConfig).limit(1)
        result = await self.session.exec(query)
        if result.first():
            return

        providers = await self.provider_service.get_all_providers(enabled_only=False)
        provider_map = {p.name: p.id for p in providers}

        for model_data in DEFAULT_MODELS:
            data = deepcopy(model_data)
            provider_name = data.pop("provider_name")
            provider_id = provider_map.get(provider_name)
            if provider_id:
                model_config = ModelConfig(provider_id=provider_id, **data)
                self.session.add(model_config)

        await self.session.flush()

    @require_login
    async def get_my_configs(self, enabled_only: bool = True) -> List[UserModelConfig]:
        """获取当前用户的所有模型配置"""
        user_id = get_current_user_id()
        return await self._get_user_configs(user_id, enabled_only)

    @require_login
    async def get_my_default_config(self) -> Optional[UserModelConfig]:
        """获取当前用户的默认模型配置"""
        user_id = get_current_user_id()
        return await self._get_default_config(user_id)

    @require_login
    async def create_my_config(self, data: UserModelConfigCreate) -> UserModelConfig:
        """当前用户创建模型配置"""
        user_id = get_current_user_id()
        return await self._create_user_config(user_id, data)

    @require_login
    async def update_my_config(self, config_id: UUID, data: UserModelConfigUpdate) -> UserModelConfig:
        """当前用户更新模型配置"""
        user_id = get_current_user_id()
        return await self._update_user_config(config_id, user_id, data)

    @require_login
    async def delete_my_config(self, config_id: UUID) -> None:
        """当前用户删除模型配置"""
        user_id = get_current_user_id()
        await self._delete_user_config(config_id, user_id)

    @require_login
    async def set_my_default(self, config_id: UUID) -> UserModelConfig:
        """当前用户设置默认配置"""
        user_id = get_current_user_id()
        return await self._set_default(config_id, user_id)

    # ========== 内部方法 ==========

    async def _get_user_configs(self, user_id: UUID, enabled_only: bool = True) -> List[UserModelConfig]:
        """内部方法：获取用户的所有模型配置"""
        query = select(UserModelConfig).where(UserModelConfig.user_id == user_id)
        if enabled_only:
            query = query.where(UserModelConfig.is_enabled == True)
        result = await self.session.exec(query)
        return list(result.all())

    async def _get_default_config(self, user_id: UUID) -> Optional[UserModelConfig]:
        """内部方法：获取用户的默认模型配置"""
        query = select(UserModelConfig).where(
            UserModelConfig.user_id == user_id,
            UserModelConfig.is_default == True,
            UserModelConfig.is_enabled == True
        )
        result = await self.session.exec(query)
        return result.first()

    async def _get_config_by_provider(self, user_id: UUID, provider_id: UUID) -> Optional[UserModelConfig]:
        """内部方法：获取用户在指定供应商的配置"""
        query = select(UserModelConfig).where(
            UserModelConfig.user_id == user_id,
            UserModelConfig.provider_id == provider_id,
            UserModelConfig.is_enabled == True
        )
        result = await self.session.exec(query)
        return result.first()

    async def _create_user_config(self, user_id: UUID, data: UserModelConfigCreate) -> UserModelConfig:
        """内部方法：创建用户模型配置"""
        provider = await self.provider_service.get(data.provider_id)
        if not provider or not provider.is_enabled:
            raise BusinessException("供应商不存在或未启用")

        if data.model_config_id:
            stmt=select(UserModelConfig).where(
                UserModelConfig.model_config_id==data.model_config_id
            )
            result = await self.session.exec(stmt)
            model_config=result.one_or_none()
            if not model_config or model_config.provider_id != data.provider_id:
                raise BusinessException("模型配置不存在或不属于该供应商")

        if data.is_default:
            await self._clear_default(user_id)

        config = UserModelConfig(user_id=user_id, **data.model_dump())
        self.session.add(config)
        await self.session.flush()
        await self.session.refresh(config)
        return config
    async def _update_user_config(self, config_id: UUID, user_id: UUID, data: UserModelConfigUpdate) -> UserModelConfig:
        """内部方法：更新用户模型配置"""
        config = await self.session.get(UserModelConfig,config_id)
        if not config or config.user_id != user_id:
            raise ResourceNotFoundException("配置不存在")

        if data.is_default:
            await self._clear_default(user_id)

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(config, key, value)
        self.session.add(config)
        await self.session.flush()
        await self.session.refresh(config)
        return config


    async def _delete_user_config(self, config_id: UUID, user_id: UUID) -> None:
        """内部方法：删除用户模型配置"""
        config = await self.session.get(UserModelConfig, config_id)
        if not config or config.user_id != user_id:
            raise ResourceNotFoundException("配置不存在")

        await self.session.delete(config)
        await self.session.flush()

    async def _set_default(self, config_id: UUID, user_id: UUID) -> UserModelConfig:
        """内部方法：设置为默认配置"""
        config = await self.session.get(UserModelConfig, config_id)
        if not config or config.user_id != user_id:
            raise ResourceNotFoundException("配置不存在")

        await self._clear_default(user_id)
        config.is_default = True
        self.session.add(config)
        await self.session.flush()
        await self.session.refresh(config)
        return config

    async def _clear_default(self, user_id: UUID) -> None:
        """清除用户的所有默认配置"""
        query = select(UserModelConfig).where(
            UserModelConfig.user_id == user_id,
            UserModelConfig.is_default == True
        )
        result = await self.session.exec(query)
        for config in result.all():
            config.is_default = False
            self.session.add(config)
        await self.session.flush()

    async def get_default_config(self, user_id: UUID) -> Optional[UserModelConfig]:
        """获取用户的默认模型配置（兼容旧接口）"""
        return await self._get_default_config(user_id)

    async def get_config_by_provider(self, user_id: UUID, provider_id: UUID) -> Optional[UserModelConfig]:
        """获取用户在指定供应商的配置（兼容旧接口）"""
        return await self._get_config_by_provider(user_id, provider_id)


# ==================== 用户服务 ====================
#
# class UserModelConfigService(BaseService[UserModelConfig]):
#     """用户模型配置服务"""
#
#     def __init__(self,
#                  session: AsyncSession,
#                  model_config_service:ModelConfigService
#                  ):
#         super().__init__(UserModelConfig, session)
#         self.model_service = model_config_service
#
#     # ========== 用户方法（带装饰器） ==========
#
#     @require_login
#     async def get_my_configs(self, enabled_only: bool = True) -> List[UserModelConfig]:
#         """获取当前用户的所有模型配置"""
#         user_id = get_current_user_id()
#         return await self._get_user_configs(user_id, enabled_only)
#
#     @require_login
#     async def get_my_default_config(self) -> Optional[UserModelConfig]:
#         """获取当前用户的默认模型配置"""
#         user_id = get_current_user_id()
#         return await self._get_default_config(user_id)
#
#     @require_login
#     async def create_my_config(self, data: UserModelConfigCreate) -> UserModelConfig:
#         """当前用户创建模型配置"""
#         user_id = get_current_user_id()
#         return await self._create_user_config(user_id, data)
#
#     @require_login
#     async def update_my_config(self, config_id: UUID, data: UserModelConfigUpdate) -> UserModelConfig:
#         """当前用户更新模型配置"""
#         user_id = get_current_user_id()
#         return await self._update_user_config(config_id, user_id, data)
#
#     @require_login
#     async def delete_my_config(self, config_id: UUID) -> None:
#         """当前用户删除模型配置"""
#         user_id = get_current_user_id()
#         await self._delete_user_config(config_id, user_id)
#
#     @require_login
#     async def set_my_default(self, config_id: UUID) -> UserModelConfig:
#         """当前用户设置默认配置"""
#         user_id = get_current_user_id()
#         return await self._set_default(config_id, user_id)
#
#     # ========== 内部方法 ==========
#
#     async def _get_user_configs(self, user_id: UUID, enabled_only: bool = True) -> List[UserModelConfig]:
#         """内部方法：获取用户的所有模型配置"""
#         query = select(UserModelConfig).where(UserModelConfig.user_id == user_id)
#         if enabled_only:
#             query = query.where(UserModelConfig.is_enabled == True)
#         result = await self.session.exec(query)
#         return list(result.all())
#
#     async def _get_default_config(self, user_id: UUID) -> Optional[UserModelConfig]:
#         """内部方法：获取用户的默认模型配置"""
#         query = select(UserModelConfig).where(
#             UserModelConfig.user_id == user_id,
#             UserModelConfig.is_default == True,
#             UserModelConfig.is_enabled == True
#         )
#         result = await self.session.exec(query)
#         return result.first()
#
#     async def _get_config_by_provider(self, user_id: UUID, provider_id: UUID) -> Optional[UserModelConfig]:
#         """内部方法：获取用户在指定供应商的配置"""
#         query = select(UserModelConfig).where(
#             UserModelConfig.user_id == user_id,
#             UserModelConfig.provider_id == provider_id,
#             UserModelConfig.is_enabled == True
#         )
#         result = await self.session.exec(query)
#         return result.first()
#
#     async def _create_user_config(self, user_id: UUID, data: UserModelConfigCreate) -> UserModelConfig:
#         """内部方法：创建用户模型配置"""
#         provider = await self.model_service.provider_service.get(data.provider_id)
#         if not provider or not provider.is_enabled:
#             raise BusinessException("供应商不存在或未启用")
#
#         if data.model_config_id:
#             model_config = await self.model_service.get(data.model_config_id)
#             if not model_config or model_config.provider_id != data.provider_id:
#                 raise BusinessException("模型配置不存在或不属于该供应商")
#
#         if data.is_default:
#             await self._clear_default(user_id)
#
#         config = UserModelConfig(user_id=user_id, **data.model_dump())
#         return await self.create(config)
#
#     async def _update_user_config(self, config_id: UUID, user_id: UUID, data: UserModelConfigUpdate) -> UserModelConfig:
#         """内部方法：更新用户模型配置"""
#         config = await self.get(config_id)
#         if not config or config.user_id != user_id:
#             raise ResourceNotFoundException("配置不存在")
#
#         if data.is_default:
#             await self._clear_default(user_id)
#
#         update_data = data.model_dump(exclude_unset=True)
#         for key, value in update_data.items():
#             setattr(config, key, value)
#
#         return await self.update(config)
#
#     async def _delete_user_config(self, config_id: UUID, user_id: UUID) -> None:
#         """内部方法：删除用户模型配置"""
#         config = await self.get(config_id)
#         if not config or config.user_id != user_id:
#             raise ResourceNotFoundException("配置不存在")
#
#         await self.delete(config)
#
#     async def _set_default(self, config_id: UUID, user_id: UUID) -> UserModelConfig:
#         """内部方法：设置为默认配置"""
#         config = await self.get(config_id)
#         if not config or config.user_id != user_id:
#             raise ResourceNotFoundException("配置不存在")
#
#         await self._clear_default(user_id)
#         config.is_default = True
#         return await self.update(config)
#
#     async def _clear_default(self, user_id: UUID) -> None:
#         """清除用户的所有默认配置"""
#         query = select(UserModelConfig).where(
#             UserModelConfig.user_id == user_id,
#             UserModelConfig.is_default == True
#         )
#         result = await self.session.exec(query)
#         for config in result.all():
#             config.is_default = False
#             self.session.add(config)
#         await self.session.flush()
#
#
#     async def get_default_config(self, user_id: UUID) -> Optional[UserModelConfig]:
#         """获取用户的默认模型配置（兼容旧接口）"""
#         return await self._get_default_config(user_id)
#
#     async def get_config_by_provider(self, user_id: UUID, provider_id: UUID) -> Optional[UserModelConfig]:
#         """获取用户在指定供应商的配置（兼容旧接口）"""
#         return await self._get_config_by_provider(user_id, provider_id)




# ==================== 整合服务 ====================

class LanguageModelService:
    """语言模型服务（整合管理员和用户功能）"""

    def __init__(self, session: AsyncSession,model_config_service:ModelConfigService):
        self.session = session

        self.model_config_service = model_config_service

    # ---------- 公共接口：获取供应商和模型列表 ----------

    async def get_providers_with_models(self) -> List[Dict[str, Any]]:
        """获取所有启用的供应商及其模型列表（给前端用）"""
        providers = await self.model_config_service.provider_service.get_all_providers()

        result = []
        for provider in providers:
            models = await self.model_config_service.get_models_by_provider(provider.id)

            result.append({
                "id": str(provider.id),
                "name": provider.name,
                "label": provider.label,
                "description": provider.description,
                "icon": provider.icon,
                "icon_background": provider.icon_background,
                "default_base_url": provider.default_base_url,
                "supported_model_types": provider.supported_model_types,
                "help_url": provider.help_url,
                "is_builtin": provider.is_builtin,
                "models": [
                    {
                        "id": str(m.id),
                        "model_name": m.model_name,
                        "label": m.label,
                        "description": m.description,
                        "model_type": m.model_type,
                        "features": m.features,
                        "context_window": m.context_window,
                        "max_output_tokens": m.max_output_tokens,
                        "default_temperature": m.default_temperature,
                        "default_top_p": m.default_top_p,
                        "default_max_tokens": m.default_max_tokens,
                        "pricing": m.pricing,
                    }
                    for m in models
                ],
            })

        return result

    # ---------- 模型加载 ----------

    async def load_language_model(
        self,
        user_id: UUID,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> BaseLanguageModel:
        """
        加载用户配置的语言模型

        Args:
            user_id: 用户ID
            provider_name: 供应商名称（可选，不传则使用用户默认配置）
            model_name: 模型名称（可选）
            parameters: 额外参数（可选）

        Returns:
            BaseLanguageModel 实例
        """
        try:
            # 1. 获取用户配置
            if provider_name:
                provider = await self.model_config_service.provider_service.get_provider_by_name(provider_name)
                if not provider:
                    raise BusinessException(f"供应商 '{provider_name}' 不存在")
                user_config = await self.model_config_service.get_config_by_provider(
                    user_id, provider.id
                )
            else:
                user_config = await self.model_config_service.get_default_config(user_id)

            if not user_config:
                raise BusinessException("用户未配置模型，请先在个人中心配置 API Key")

            # 2. 获取供应商信息
            provider = await self.model_config_service.provider_service.get(user_config.provider_id)
            if not provider:
                raise BusinessException("供应商配置已失效")

            # 3. 确定模型名称和参数
            if user_config.model_config_id:
                # 使用内置模型配置
                model_config = await self.model_config_service.get(user_config.model_config_id)
                actual_model_name = model_config.model_name if model_config else model_name
                default_params = self._get_model_defaults(model_config)
                attributes = model_config.attributes if model_config else {}
                features = model_config.features if model_config else []
                metadata = {"pricing": model_config.pricing} if model_config and model_config.pricing else {}
            else:
                # 使用自定义模型
                actual_model_name = user_config.custom_model_name or model_name
                default_params = {}
                attributes = {"model": actual_model_name}
                features = []
                metadata = {}

            if not actual_model_name:
                raise BusinessException("未指定模型名称")

            # 4. 合并参数（优先级：调用参数 > 用户配置 > 内置默认值）
            final_params = self._merge_parameters(
                default_params,
                user_config,
                parameters or {}
            )

            # 5. 获取模型类
            model_class = get_chat_class(provider.name)
            if not model_class:
                raise BusinessException(f"不支持的供应商: {provider.name}")

            # 6. 确定 base_url
            base_url = user_config.base_url or provider.default_base_url or ""

            # 7. 实例化模型
            return model_class(
                api_key=user_config.api_key,
                base_url=base_url,
                **attributes,
                **final_params,
                features=[ModelFeature(f) for f in features] if features else [],
                metadata=metadata,
            )

        except BusinessException:
            raise
        except Exception as error:
            logging.error(f"加载模型失败: {error}", exc_info=True)
            raise BusinessException(f"加载模型失败: {str(error)}")

    def _get_model_defaults(self, model_config: Optional[ModelConfig]) -> Dict[str, Any]:
        """获取模型默认参数"""
        if not model_config:
            return {}

        return {
            "temperature": model_config.default_temperature,
            "top_p": model_config.default_top_p,
            "max_tokens": model_config.default_max_tokens,
            **model_config.default_parameters,
        }

    def _merge_parameters(
        self,
        defaults: Dict[str, Any],
        user_config: UserModelConfig,
        call_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        合并参数

        优先级：调用参数 > 用户配置 > 内置默认值
        """
        result = {**defaults}

        # 用户配置覆盖
        if user_config.custom_temperature is not None:
            result["temperature"] = user_config.custom_temperature
        if user_config.custom_top_p is not None:
            result["top_p"] = user_config.custom_top_p
        if user_config.custom_max_tokens is not None:
            result["max_tokens"] = user_config.custom_max_tokens
        if user_config.custom_parameters:
            result.update(user_config.custom_parameters)

        # 调用参数覆盖
        result.update(call_params)

        return result

    # ---------- 初始化 ----------

    async def init_default_data(self) -> None:
        """初始化默认数据（管理员首次启动时调用）"""
        await self.model_config_service.init_default_models()
