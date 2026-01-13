import tiktoken
from langchain_qwq import ChatQwen
from typing_extensions import Tuple

from app.src.core.language_model.entities.model_entity import BaseLanguageModel


class Chat(ChatQwen, BaseLanguageModel):
    """通义千问聊天模型"""



    def _get_encoding_model(self) -> Tuple[str, tiktoken.Encoding]:
        """重写月之暗面获取编码模型名字+模型函数，该类继承OpenAI，词表模型可以使用gpt-3.5-turbo防止出错"""
        # 1.将DeepSeek的词表模型设置为gpt-3.5-turbo
        model = "gpt-3.5-turbo"

        # 2.返回模型名字+编码器
        return model, tiktoken.encoding_for_model(model)
