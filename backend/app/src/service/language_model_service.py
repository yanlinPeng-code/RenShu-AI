"""
语言模型服务

架构设计：
1. 管理员层：管理供应商和内置模型配置
2. 用户层：配置 API Key 和自定义参数
"""
import logging
import json
from typing import Any, Optional, List, Dict
from uuid import UUID
from copy import deepcopy

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from openai import AsyncOpenAI

from app.src.core.language_model.entities.model_entity import BaseLanguageModel, ModelFeature
from app.src.core.language_model.default_models import DEFAULT_PROVIDERS, DEFAULT_MODELS

from app.src.response.exception.exceptions import ResourceNotFoundException, BusinessException
from app.src.service.base_service import BaseService
from app.src.common.decorators import require_login
from app.src.common.context import get_current_user_id, get_user_roles
from app.src.utils.auth_utils import hash_api_key

from app.src.model.model_config_models import (
    SystemModelProvider, SystemModelDefinition, UserProviderConfig, UserModelPreference
)
from app.src.schema.model_config_schema import ModelProviderCreate, ModelProviderUpdate, ModelConfigCreate, ModelConfigUpdate


# ==================== 供应商服务 ====================

class ModelProviderService(BaseService[SystemModelProvider]):
    """模型供应商服务"""

    def __init__(self, session: AsyncSession):
        super().__init__(SystemModelProvider, session)

    async def get_all_providers(self, enabled_only: bool = True, user_id: Optional[UUID] = None) -> List[SystemModelProvider]:
        """获取所有系统供应商
        注意：此方法返回纯 SystemModelProvider，不包含用户配置。
        如果需要用户配置，请使用 language_model_service.get_providers_with_models
        
        更新逻辑：支持用户自定义供应商 (owner_id = user_id)
        """
        # 基础查询：所有者为 NULL (系统内置)
        conditions = [SystemModelProvider.owner_id == None]
        
        # 如果指定了用户，也包含该用户拥有的供应商
        if user_id:
            conditions.append(SystemModelProvider.owner_id == user_id)
            
        from sqlmodel import or_
        query = select(SystemModelProvider).where(or_(*conditions))
        query = query.order_by(SystemModelProvider.position)
        result = await self.session.exec(query)
        return list(result.all())

    async def get_builtin_providers(self) -> List[SystemModelProvider]:
        """获取所有系统内置供应商"""
        return await self.get_all_providers()

    async def get_provider_by_name(self, name: str) -> Optional[SystemModelProvider]:
        """根据名称获取供应商"""
        query = select(SystemModelProvider).where(SystemModelProvider.name == name)
        result = await self.session.exec(query)
        return result.first()
    
    async def get_user_config(self, user_id: UUID, provider_id: UUID) -> Optional[UserProviderConfig]:
        """获取用户的供应商配置"""
        query = select(UserProviderConfig).where(
            UserProviderConfig.user_id == user_id,
            UserProviderConfig.provider_id == provider_id
        )
        result = await self.session.exec(query)
        return result.first()

    @require_login
    async def update_user_config(self, provider_id: UUID, data: dict) -> UserProviderConfig:
        """更新用户的供应商配置 (API Key, Base URL)"""
        user_id = get_current_user_id()
        
        # 检查供应商是否存在
        provider = await self.get(provider_id)
        if not provider:
            raise ResourceNotFoundException("供应商不存在")

        # 查找现有配置或创建新配置
        config = await self.get_user_config(user_id, provider_id)
        if not config:
            config = UserProviderConfig(user_id=user_id, provider_id=provider_id)
            self.session.add(config)
        
        # 更新字段
        if "api_key" in data:
            # 如果提供了 API Key，则进行哈希存储；如果为空字符串，则可能意图清除（视业务逻辑而定）
            if data["api_key"]:
                config.api_key = hash_api_key(data["api_key"])
            else:
                config.api_key = None # 允许清除
                
        if "base_url" in data:
            # 如果是空字符串，设为 None 以使用系统默认
            config.base_url_override = data["base_url"] if data["base_url"] else None
            
        if "is_enabled" in data:
            config.is_enabled = data["is_enabled"]
            
        await self.session.flush()
        return config

    @require_login
    async def verify_api_key(self, provider_id: UUID, api_key: str, base_url: Optional[str] = None, model_name: Optional[str] = None) -> Dict[str, Any]:
        """验证供应商API Key是否有效
        
        策略：
        1. 尝试使用 models.list() 接口。如果成功，说明 API Key 有效。
        2. 如果 models.list() 失败 (某些供应商不支持或权限受限)，尝试发起一个极简的 Chat Completion 请求。
        """
        provider = await self.get(provider_id)
        if not provider:
            raise ResourceNotFoundException("供应商不存在")

        # 使用提供的base_url或provider的默认base_url
        test_base_url = base_url or provider.default_base_url

        # 创建 AsyncOpenAI 客户端
        # 注意：对于非 OpenAI 的供应商，它们通常也兼容 OpenAI SDK 协议
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=test_base_url,
            timeout=10.0,
            max_retries=1
        )

        # -------------------- 步骤 1: 尝试获取模型列表 --------------------
        try:
            await client.models.list()
            return {
                "valid": True,
                "message": "API Key验证成功",
                "method": "models.list"
            }
        except Exception as e1:
            logging.warning(f"API Key verification via models.list failed: {str(e1)}. Trying fallback...")

            try:
                    await client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": "Hi"}],
                        max_tokens=1
                    )
                    return {
                        "valid": True,
                        "message": f"API Key验证成功",
                        "method": "chat.completions.create"
                    }
            except Exception as e2:
                    last_error = e2
                    # 如果是认证错误 (401), 直接认定为失败，不再尝试其他模型
                    error_str = str(e2).lower()
                    if "401" in error_str or "unauthorized" in error_str or "invalid api key" in error_str:
                        return {
                            "valid": False,
                            "message": f"验证失败: API Key 无效 ({str(e2)})"
                        }
            # 如果所有尝试都失败
            return {
                "valid": False,
                "message": f"验证失败: 无法连接到服务或 API Key 无效。错误信息: {str(last_error) if last_error else str(e1)}"
            }

    async def create_provider_safe(self, data: ModelProviderCreate, user_id: UUID, is_admin: bool) -> SystemModelProvider:
        """安全创建供应商
        - 管理员：创建系统级供应商 (owner_id = None)
        - 普通用户：创建私有供应商 (owner_id = user_id)
        """
        # 1. 检查是否存在同名供应商 (不区分大小写)
        from sqlalchemy import func
        target_name = data.name.lower()
        
        # 检查逻辑：如果是系统级，检查所有系统级；如果是私有，检查该用户的所有私有
        # 或者更严格：全局不区分大小写唯一？
        # 用户需求："无论是用户还是管理员，相同name的提供商不能创建成功" -> 全局唯一
        
        query = select(SystemModelProvider).where(func.lower(SystemModelProvider.name) == target_name)
        existing = await self.session.exec(query)
        if existing.first():
            raise BusinessException(f"供应商 '{data.name}' 已存在 (不区分大小写)")

        # 确定 owner_id
        owner_id = None if is_admin else user_id

        # 准备创建数据
        create_data = data.model_dump()
        create_data["owner_id"] = owner_id
        
        # 字段适配
        db_data = create_data.copy()
        if "base_url" in db_data:
            db_data["default_base_url"] = db_data.pop("base_url")
            
        # 提取 API Key (不存入 SystemModelProvider)
        api_key = db_data.pop("api_key", None)
            
        # 创建 Provider
        provider = SystemModelProvider(**db_data)
        self.session.add(provider)
        await self.session.flush()
        
        # 如果有 API Key，创建 UserProviderConfig
        if api_key and owner_id:
            config = UserProviderConfig(
                user_id=owner_id,
                provider_id=provider.id,
                api_key=hash_api_key(api_key),
                is_enabled=True
            )
            self.session.add(config)
            await self.session.flush()
            
        return provider

    async def delete_provider_safe(self, provider_id: UUID, user_id: UUID, is_admin: bool) -> None:
        """安全删除供应商
        
        删除策略：
        1. 删除该供应商下的所有模型定义 (SystemModelDefinition)
        2. 删除该供应商下的所有用户配置 (UserProviderConfig)
        3. 删除供应商本身 (SystemModelProvider)
        """
        provider = await self.get(provider_id)
        if not provider:
            raise ResourceNotFoundException("供应商不存在")

        # 权限检查
        if not is_admin:
            if str(provider.owner_id) != str(user_id):
                # 既不是管理员，也不是拥有者
                from app.src.response.exception.exceptions import AuthorizationException
                raise AuthorizationException("无权删除此供应商")
        
        # 1. 删除关联的模型定义
        stmt_models = select(SystemModelDefinition).where(SystemModelDefinition.provider_id == provider_id)
        models = await self.session.exec(stmt_models)
        for model in models.all():
            # 删除模型关联的用户偏好
            stmt_prefs = select(UserModelPreference).where(UserModelPreference.model_def_id == model.id)
            prefs = await self.session.exec(stmt_prefs)
            for pref in prefs.all():
                await self.session.delete(pref)
            
            # 删除模型定义
            await self.session.delete(model)
            
        # 2. 删除关联的用户供应商配置
        stmt_configs = select(UserProviderConfig).where(UserProviderConfig.provider_id == provider_id)
        configs = await self.session.exec(stmt_configs)
        for config in configs.all():
            await self.session.delete(config)
            
        # 3. 删除供应商
        await self.delete(provider)

    async def update_provider_safe(self, provider_id: UUID, data: ModelProviderUpdate, user_id: UUID, is_admin: bool) -> Any:
        """安全更新供应商"""
        # 1. 获取供应商
        provider = await self.get(provider_id)
        if not provider:
             from app.src.response.exception.exceptions import ResourceNotFoundException
             raise ResourceNotFoundException("供应商不存在")

        # 2. 检查权限 (是否是拥有者)
        is_owner = str(provider.owner_id) == str(user_id)
        
        # 准备用户配置更新数据
        config_update_data = data.model_dump(exclude_unset=True)

        if is_admin or is_owner:
            # 管理员或拥有者：可以修改供应商元数据 (SystemModelProvider)
            
            update_dict = data.model_dump(exclude_unset=True)
            sys_updated = False

            # 特殊处理 base_url: 对于拥有者，修改的是 default_base_url
            if "base_url" in update_dict:
                 provider.default_base_url = update_dict["base_url"]
                 sys_updated = True
                 # 如果修改了默认地址，就不需要再设置覆盖地址了 (除非显式需要，但通常"编辑供应商"意为修改默认值)
                 if "base_url" in config_update_data:
                     del config_update_data["base_url"]

            # 更新其他元数据字段
            sys_fields = ["label", "description", "icon", "icon_background", "help_url", "supported_model_types", "position"]
            for key in sys_fields:
                if key in update_dict:
                    setattr(provider, key, update_dict[key])
                    sys_updated = True
            
            if sys_updated:
                self.session.add(provider)
                await self.session.flush()
            
            # 同时更新用户配置 (主要是 API Key 和 Enabled 状态)
            # 注意：base_url 已被从 config_update_data 中移除 (如果存在)，所以不会更新 base_url_override
            await self.update_user_config(provider_id, config_update_data)
            
            return provider # 返回 SystemModelProvider 对象
            
        else:
            # 普通用户修改系统供应商：只能修改用户配置 (UserProviderConfig)
            return await self.update_user_config(provider_id, config_update_data)



class ModelConfigService(BaseService[SystemModelDefinition]):
    """模型配置服务"""

    def __init__(self, session: AsyncSession, provider_service: ModelProviderService):
        super().__init__(SystemModelDefinition, session)
        self.provider_service = provider_service

    async def get_models_by_provider(self, provider_id: UUID, user_id: Optional[UUID] = None) -> List[Dict[str, Any]]:
        """获取供应商下的所有模型（合并用户偏好）
        包含：
        1. 系统内置模型 (owner_id IS NULL)
        2. 用户自定义模型 (owner_id == user_id)
        """
        # 1. 构建查询：获取系统模型 + 用户私有模型
        from sqlmodel import or_
        conditions = [SystemModelDefinition.provider_id == provider_id]
        
        owner_condition = SystemModelDefinition.owner_id == None
        if user_id:
            owner_condition = or_(SystemModelDefinition.owner_id == None, SystemModelDefinition.owner_id == user_id)
        
        conditions.append(owner_condition)
        
        query = select(SystemModelDefinition).where(*conditions).order_by(SystemModelDefinition.position)
        
        result = await self.session.exec(query)
        all_models = list(result.all())
        
        # 2. 如果没有用户ID，直接返回系统定义 (此时也只查到了系统定义)
        if not user_id:
            return all_models

        # 3. 获取用户偏好 (仅针对系统模型，或者用户也可能对自己创建的模型有偏好记录？通常用户直接修改模型本身即可，但保持一致性也无妨)
        # 这里主要为了获取系统模型的 enabled 状态覆盖等
        pref_query = select(UserModelPreference).where(
            UserModelPreference.user_id == user_id,
            UserModelPreference.model_def_id.in_([m.id for m in all_models])
        )
        pref_result = await self.session.exec(pref_query)
        user_prefs = {p.model_def_id: p for p in pref_result.all()}

        # 4. 合并数据
        merged_models = []
        for m in all_models:
            pref = user_prefs.get(m.id)
            
            # 判断是否是用户自定义模型
            is_custom = m.owner_id == user_id
            
            # 基础数据
            model_data = {
                "id": m.id,
                "provider_id": m.provider_id,
                "model_name": m.model_name,
                "label": m.label,
                "description": m.description,
                "model_type": m.model_type,
                "features": m.features,
                "context_window": m.context_window,
                "default_max_tokens": m.default_max_tokens,
                "default_parameters": m.default_parameters,
                "position": m.position,
                "is_enabled": m.is_enabled, # 系统级开关
                "owner_id": m.owner_id,
                "is_custom": is_custom,
                "created_at": m.created_at,
                "updated_at": m.updated_at
            }
            
            # 应用用户偏好覆盖 (仅当有偏好记录时)
            if pref:
                # 即使是用户自定义模型，如果有了偏好记录，也应用偏好（虽然用户可以直接改模型，但为了逻辑统一）
                model_data["is_enabled"] = pref.is_enabled 
                
                if pref.custom_parameters:
                    custom = pref.custom_parameters
                    if "context_window" in custom:
                        model_data["context_window"] = custom["context_window"]
                    if "default_max_tokens" in custom:
                        model_data["default_max_tokens"] = custom["default_max_tokens"]
                    if "temperature" in custom:
                        model_data["default_parameters"]["temperature"] = custom["temperature"]
                    # ... 其他参数 ...
            
            merged_models.append(model_data)
            
        return merged_models

    async def update_user_model_preference(self, user_id: UUID, model_def_id: UUID, data: dict) -> UserModelPreference:
        """更新用户对模型的偏好"""
        # 检查模型是否存在
        model_def = await self.get(model_def_id)
        if not model_def:
            raise ResourceNotFoundException("模型定义不存在")

        # 查找或创建偏好
        pref = await self.get_user_preference(user_id, model_def_id)
        if not pref:
            pref = UserModelPreference(user_id=user_id, model_def_id=model_def_id)
            self.session.add(pref)
            
        # 更新字段
        if "is_enabled" in data:
            pref.is_enabled = data["is_enabled"]
            
        # 更新自定义参数
        current_params = pref.custom_parameters or {}
        
        # 支持的覆盖字段
        overrides = ["context_window", "default_max_tokens", "temperature", "top_p"]
        for key in overrides:
            if key in data:
                current_params[key] = data[key]
        
        pref.custom_parameters = current_params
        
        await self.session.flush()
        return pref

    async def get_user_preference(self, user_id: UUID, model_def_id: UUID) -> Optional[UserModelPreference]:
        """获取用户对模型的偏好"""
        query = select(UserModelPreference).where(
            UserModelPreference.user_id == user_id,
            UserModelPreference.model_def_id == model_def_id
        )
        result = await self.session.exec(query)
        return result.first()

    async def create_model_config_safe(self, data: ModelConfigCreate, user_id: UUID, is_admin: bool) -> SystemModelDefinition:
        """安全创建模型配置
        - 管理员：可在任意供应商下创建模型 (默认创建为系统模型 owner_id=None，也可指定)
        - 普通用户：
            1. 在自己创建的供应商下创建模型 -> 设为私有 (owner_id=user_id)
            2. 在系统供应商下创建模型 -> 设为私有 (owner_id=user_id)
        """
        # 检查供应商是否存在
        provider = await self.provider_service.get(data.provider_id)
        if not provider:
            raise ResourceNotFoundException("供应商不存在")
            
        # 确定 owner_id
        owner_id = None
        if not is_admin:
            # 普通用户创建的模型，所有者必须是自己
            owner_id = user_id
            
            # 权限检查：
            # 如果是私有供应商，必须是自己的
            if str(provider.owner_id) and str(provider.owner_id) != str(user_id):
                 from app.src.response.exception.exceptions import AuthorizationException
                 raise AuthorizationException("无权在此私有供应商下创建模型")
            # 如果是系统供应商(provider.owner_id is None)，允许创建，但模型本身必须是私有的(已设置 owner_id=user_id)

        # 转换 Pydantic model 到 dict
        create_data = data.model_dump()
        create_data["owner_id"] = owner_id # 显式设置所有者
        
        # 手动创建 SystemModelDefinition 对象
        config = SystemModelDefinition(**create_data)
        
        self.session.add(config)
        await self.session.flush()
        return config

    async def update_model_config_safe(self, config_id: UUID, data: ModelConfigUpdate, user_id: UUID, is_admin: bool) -> Any:
        """安全更新模型配置
        - 管理员 OR 模型拥有者：更新系统定义
        - 普通用户 & 非拥有者：更新用户偏好 (UserModelPreference)
        """
        # 检查模型是否存在
        sys_model = await self.get(config_id)
        if not sys_model:
             raise ResourceNotFoundException("模型配置不存在")

        # 检查所有权
        # 模型本身的 owner_id 决定了归属
        is_owner = str(sys_model.owner_id) == str(user_id)
    
        if is_admin or is_owner:
            # 管理员或拥有者：直接更新定义
            
            # 更新实例字段 
            update_dict = data.model_dump(exclude_unset=True) 
            for key, value in update_dict.items(): 
                if hasattr(sys_model, key): 
                    setattr(sys_model, key, value) 
            
            # 调用 update 
            return await self.update(sys_model) 
        else: 
            # 普通用户修改系统模型(owner_id=None) 或 他人模型：更新偏好 
            update_data = data.model_dump(exclude_unset=True) 
            
            # 提取支持覆盖的字段 
            pref_data = {} 
            if "is_enabled" in update_data: 
                pref_data["is_enabled"] = update_data["is_enabled"] 
            # 参数映射 
            if "context_window" in update_data: 
                pref_data["context_window"] = update_data["context_window"] 
            if "default_max_tokens" in update_data: 
                pref_data["default_max_tokens"] = update_data["default_max_tokens"] 
            if "default_temperature" in update_data: 
                pref_data["temperature"] = update_data["default_temperature"] 
            if "default_top_p" in update_data: 
                pref_data["top_p"] = update_data["default_top_p"] 
                
            return await self.update_user_model_preference(user_id, config_id, pref_data)

    async def delete_model_config_safe(self, config_id: UUID, user_id: UUID, is_admin: bool) -> None:
        """安全删除模型配置
        - 管理员：可以删除任何模型
        - 普通用户：只能删除自己创建的模型 (model.owner_id == user_id)
        """
        model = await self.get(config_id)
        if not model:
            raise ResourceNotFoundException("模型配置不存在")

        if not is_admin:
            # 权限检查：必须是模型的所有者
            if str(model.owner_id) != str(user_id):
                # 尝试删除系统模型或其他用户的模型
                from app.src.response.exception.exceptions import AuthorizationException
                raise AuthorizationException("无权删除此模型配置")

        await self.delete(model)

    async def init_default_models(self) -> None:
        """初始化默认模型配置"""
        await self.provider_service.init_default_providers()

        query = select(SystemModelDefinition).limit(1)
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
                # 适配字段
                data.pop("is_builtin", None)
                data.pop("user_id", None)
                data.pop("template_id", None)
                
                model_config = SystemModelDefinition(provider_id=provider_id, **data)
                self.session.add(model_config)

        await self.session.flush()


class LanguageModelService:
    """语言模型服务（整合系统定义与用户配置）"""

    def __init__(self, session: AsyncSession, model_config_service: ModelConfigService):
        self.session = session
        self.model_config_service = model_config_service

    # ---------- 公共接口：获取供应商和模型列表 ----------

    async def get_providers_with_models(self, user_id: Optional[UUID] = None) -> List[Dict[str, Any]]:
        """获取所有系统供应商及其模型列表，并填充用户配置"""
        
        # 1. 获取所有系统供应商
        providers = await self.model_config_service.provider_service.get_all_providers(user_id=user_id)
        
        # 2. 如果有用户ID，批量获取用户配置
        user_configs_map = {}
        if user_id:
            query = select(UserProviderConfig).where(UserProviderConfig.user_id == user_id)
            result = await self.session.exec(query)
            for cfg in result.all():
                user_configs_map[cfg.provider_id] = cfg

        result = []
        for provider in providers:
            # 获取该供应商下的模型
            models = await self.model_config_service.get_models_by_provider(provider.id, user_id=user_id)
            
            # 获取用户配置
            user_cfg = user_configs_map.get(provider.id)
            
            # 构建返回数据（保持与前端原有结构兼容）
            provider_data = {
                "id": str(provider.id),
                "name": provider.name,
                "label": provider.label,
                "description": provider.description,
                "icon": provider.icon,
                "icon_background": provider.icon_background,
                "supported_model_types": provider.supported_model_types,
                "help_url": provider.help_url,
                "position": provider.position,
                "is_builtin": provider.owner_id is None, # 如果没有 owner_id，则是系统内置的
                
                # 动态字段：根据用户配置填充
                "base_url": user_cfg.base_url_override if user_cfg and user_cfg.base_url_override else provider.default_base_url,
                "api_key": user_cfg.api_key if user_cfg else None, # 前端需要知道是否有API Key
                "is_enabled": user_cfg.is_enabled if user_cfg else True, # 默认启用
            }
            
            # 构建模型列表
            models_data = []
            for m in models:
                # m 可能是 SystemModelDefinition 对象（如果是管理员调用）或者 dict（如果是普通用户调用）
                # 为了统一，我们检查类型
                if isinstance(m, dict):
                    models_data.append({
                        "id": str(m["id"]),
                        "model_name": m["model_name"],
                        "label": m["label"],
                        "description": m["description"],
                        "model_type": m["model_type"],
                        "features": m["features"],
                        "context_window": m["context_window"],
                        "default_temperature": m["default_parameters"].get("temperature", 0.7),
                        "default_top_p": m["default_parameters"].get("top_p", 1.0),
                        "default_max_tokens": m["default_max_tokens"],
                        "is_builtin": True,
                        "is_enabled": m["is_enabled"]
                    })
                else:
                    # SystemModelDefinition object
                    models_data.append({
                        "id": str(m.id),
                        "model_name": m.model_name,
                        "label": m.label,
                        "description": m.description,
                        "model_type": m.model_type,
                        "features": m.features,
                        "context_window": m.context_window,
                        "default_temperature": m.default_parameters.get("temperature", 0.7),
                        "default_top_p": m.default_parameters.get("top_p", 1.0),
                        "default_max_tokens": m.default_max_tokens,
                        "is_builtin": True,
                        "is_enabled": m.is_enabled
                    })
            
            provider_data["models"] = models_data
            result.append(provider_data)

        return result

    # ---------- 初始化 ----------

    async def init_default_data(self) -> None:
        """初始化默认数据"""
        await self.model_config_service.init_default_models()


