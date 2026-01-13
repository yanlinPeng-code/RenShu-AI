"""
模型供应商适配器模块

提供各个供应商的 Chat 类适配器。
"""

from .openai.chat import Chat as OpenAIChat
from .deepseek.chat import Chat as DeepSeekChat
from .tongyi.chat import Chat as TongyiChat
from .moonshot.chat import Chat as MoonshotChat
from .ollama.chat import Chat as OllamaChat

# 供应商名称到 Chat 类的映射
PROVIDER_CHAT_CLASSES = {
    "openai": OpenAIChat,
    "deepseek": DeepSeekChat,
    "tongyi": TongyiChat,
    "moonshot": MoonshotChat,
    "ollama": OllamaChat,
}


def get_chat_class(provider_name: str):
    """
    根据供应商名称获取对应的 Chat 类

    Args:
        provider_name: 供应商名称，如 'openai', 'deepseek' 等

    Returns:
        对应的 Chat 类，如果不存在则返回 None
    """
    return PROVIDER_CHAT_CLASSES.get(provider_name)


__all__ = [
    'OpenAIChat',
    'DeepSeekChat',
    'TongyiChat',
    'MoonshotChat',
    'OllamaChat',
    'PROVIDER_CHAT_CLASSES',
    'get_chat_class',
]
