from fastapi import APIRouter, Request, Depends
from app.src.core.utils.auth_utils import get_current_user_id_from_jwt
from app.src.dependencies.dependency import UserServiceDep
from app.src.response.utils import success_200
from app.src.service.conversation_service import ConversationService
from app.src.dependencies.dependency import get_conversation_service

from app.src.dependencies.dependency import ConversationServiceDep

router = APIRouter(prefix="/conversations", tags=["对话管理"])



@router.get("/me")
async def get_user_conversations(
        request: Request,
        conversation_service: ConversationServiceDep
):
    """
    获取当前用户的对话列表
    """
    
    # 获取用户的会话
    conversations = await conversation_service.get_my_conversations()
    
    client_ip = request.state.client_ip
    request_id = request.state.request_id
    
    return success_200(
        data=[conversation.model_dump() for conversation in conversations],
        message="获取对话列表成功",
        request_id=request_id,
        host_id=client_ip
    )