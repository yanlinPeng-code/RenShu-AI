"""
用户认证中间件
用于保护现有的API端点
"""

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.src.service.auth_service import  AuthService
from app.src.utils import get_logger

security = HTTPBearer(auto_error=False)
auth_utils = AuthService()

logger=get_logger("认证工具")
