from langchain_openai import ChatOpenAI

from app.src.core.language_model.entities.model_entity import BaseLanguageModel


class Chat(ChatOpenAI, BaseLanguageModel):
    """openai基础聊天模型类"""

    pass