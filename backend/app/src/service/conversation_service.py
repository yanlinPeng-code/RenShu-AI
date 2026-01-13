import uuid

from app.src.model import Conversation, User
from app.src.response.exception.exceptions import InternalServerException
from app.src.service.base_service import BaseService
from app.src.core.decorators import require_login
from app.src.core.context import get_current_user_id
from sqlmodel import select


class ConversationService(BaseService):
    def __init__(self, session):
        super().__init__(Conversation, session)

    # ========== 外部接口方法（带装饰器） ==========

    @require_login
    async def get_my_conversations(self):
        """获取当前登录用户的会话列表"""
        user_id = get_current_user_id()
        return await self._get_conversation_by_user_id(user_id)

    @require_login
    async def create_my_conversation(self, **kwargs):
        """为当前登录用户创建会话"""
        user_id = get_current_user_id()
        return await self._create_conversation(user_id, **kwargs)

    # ========== 内部方法（不加装饰器） ==========

    async def _get_conversation_by_user_id(self, user_id: str):
        """内部方法：根据用户id获取会话"""
        stmt = select(User).where(User.id == user_id)
        res = await self.session.exec(stmt)
        user = res.one_or_none()

        if not user:
            raise ValueError("用户不存在")
        if not user.is_active:
            raise ValueError("用户账户未激活")

        conversation_stmt = select(Conversation).where(Conversation.user_id == user_id)
        conversation_res = await self.session.exec(conversation_stmt)
        return conversation_res.all()

    async def _create_conversation(self, user_id: str, **kwargs):
        """内部方法：创建会话"""
        try:
            conversation = await self.get(user_id)
            if not conversation:
                conversation = Conversation(
                    user_id=user_id,
                    session_id=str(uuid.uuid4()),
                    conversation_type="日常交流",
                )
                return await self.create(conversation)
            return conversation
        except Exception as e:
            raise InternalServerException(message="会话添加错误", details={"error": str(e)})

















