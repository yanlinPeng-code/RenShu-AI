from fastapi import APIRouter, Request, Depends

from app.src.dependencies.dependency import ChatServiceDep
from app.src.schema.chat_schema import ChatRequest
from app.src.utils import get_logger
from app.src.core.utils.auth_utils import get_current_user_id_from_jwt
router =APIRouter(prefix="/api/v1/chat", tags=["聊天模块"])

logger=get_logger("chat_controller")


@router.post("/generate")
async def chat_generate(request: Request,
                        chat_service: ChatServiceDep,
                        chat_request: ChatRequest,
                        ):

    logger.info("开始生成,块状生成")
    response=await chat_service.generate_chat(chat_request)

    return response
