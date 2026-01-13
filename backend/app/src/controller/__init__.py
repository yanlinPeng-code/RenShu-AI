"""
控制器模块

包含所有的API控制器。
"""

from .user_controller import router as user_router
from .admin_controller import router as admin_router
from .model_config_controller import router as model_config_router
from .chat_controller import router as chat_router

__all__ = ["user_router", "admin_router", "model_config_router", "chat_router"]
