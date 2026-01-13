from typing import List,Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.src.entity.model_entity import DEFAULT_MODEL_CONFIG


class ChatRequest(BaseModel):
    """
    聊天请求参数
    """
    user_id: UUID=Field(..., description="用户ID")
    conversation_id: UUID=Field(..., description="会话ID")
    message:List[dict]=Field(..., description="消息列表")
    model_configuration: Optional[dict]=Field( description="模型配置",default=DEFAULT_MODEL_CONFIG)
    stream: bool=Field(False, description="是否流式返回")

