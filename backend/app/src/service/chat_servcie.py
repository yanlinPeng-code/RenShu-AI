from app.src.schema.chat_schema import ChatRequest
from app.src.service.base_service import BaseService
from app.src.service.conversation_service import ConversationService
from app.src.service.language_model_service import LanguageModelService
from app.src.core.decorators import require_login
from app.src.core.context import get_current_user_id


class ChatService:
    def __init__(self,
                 conversation_service: ConversationService,
                 model_service: LanguageModelService
                 ):
        self.conversation_service = conversation_service
        self.model_service = model_service

    # ========== 使用装饰器的方法 ==========

    @require_login
    async def generate_chat(self, chat_request: ChatRequest):
        """
        生成聊天回复（需要登录）
        :param chat_request: 聊天请求
        :return: 聊天回复
        """
        user_id = get_current_user_id()
        return await self._generate(chat_request, user_id)

    # ========== 内部方法 ==========

    async def _generate(self, chat_request: ChatRequest, user_id: str):
        """内部方法：生成聊天回复"""
        # 验证前端请求的用户是否存在会话信息
        conversation = await self.conversation_service._get_conversation_by_user_id(user_id)

        if not conversation:
            # 创建新的会话
            conversation = await self.conversation_service._create_conversation(user_id)

        # 获取当前会话的session_id
        session_id = conversation.session_id
        # 判断当前会话的session_id的消息排序
        # TODO: 实现消息生成逻辑


























           




















