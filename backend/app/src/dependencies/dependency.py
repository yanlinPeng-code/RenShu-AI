# 依赖注入
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.src.service import UserService
from app.src.service.chat_servcie import ChatService
from app.src.service.conversation_service import ConversationService
from app.src.service.language_model_service import LanguageModelService
from app.src.service.language_model_service import ModelProviderService, ModelConfigService

from app.src.common.config.prosgresql_config import get_db


def get_conversation_service(
        session:AsyncSession=Depends(get_db),
)->ConversationService:
    """获取会话服务实例"""
    return ConversationService(session=session)




def get_user_service(
    session:AsyncSession=Depends(get_db),

)->UserService:
    """获取用户服务实例"""
    return UserService(
        session=session,
    )

def get_model_provider_service(
        session: AsyncSession = Depends(get_db),
):
    return ModelProviderService(session=session)


def get_model_config_service(
        session: AsyncSession = Depends(get_db),
        provider_service:ModelProviderService=Depends(get_model_provider_service)
):
    return ModelConfigService(
        session=session,
        provider_service=provider_service
    )



def get_model_service(session:AsyncSession=Depends(get_db),
                      model_config_service:ModelConfigService=Depends(get_model_config_service)

                      )->LanguageModelService:
    """获取模型服务实例"""
    return LanguageModelService(session=session,model_config_service=model_config_service)



def get_chat_service(
        conversation_service:Annotated[ConversationService,Depends(get_conversation_service)],
        model_service:Annotated[LanguageModelService,Depends(get_model_service)]
)->ChatService:
    """获取聊天服务实例"""
    return ChatService(conversation_service=conversation_service,model_service=model_service)





UserServiceDep=Annotated[UserService,Depends(get_user_service)]
ChatServiceDep=Annotated[ChatService,Depends(get_chat_service)]
LanguageModelServiceDep=Annotated[LanguageModelService,Depends(get_model_service)]
ConversationServiceDep=Annotated[ConversationService,Depends(get_conversation_service)]