"""
JSON Web Token
"""

import jwt  # type: ignore

import bcrypt  # type: ignore
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException  # type: ignore
from app.src.common.config.setting_config import settings
from app.src.utils import get_logger
from fastapi import Request


logger=get_logger("auth")
   

# JWT配置
# 生产配置：这里需要 使用加密安全的随机生成器生成，可以通过环境变量或者外部服务管理秘钥，并做定期轮换
# 硬编码仅使用课程演示环境或者研发测试环境
JWT_SECRET = settings.JWT_SECRET_KEY
ACCESS_TOKEN_EXPIRE_HOURS = 24  # 普通接口访问携带的token过期时间为24小时
REFRESH_TOKEN_EXPIRE_DAYS = 30  # 刷新token过期时间为30天


def hash_api_key(api_key: str) -> str:
        """API key hashing"""
        try:
            hashed = hashlib.sha256(api_key.encode('utf-8')).hexdigest()
            return hashed
        except Exception as e:
            logger.error(f"API key hashing failed: {e}")
            raise
def verify_api_key(hashed_api_key: str, input_api_key: str) -> bool:
        """API key verification"""
        try:
            is_valid = hashed_api_key == hash_api_key(input_api_key)
            if is_valid:
                logger.info("API key verification successful")
            else:
                logger.warning("API key verification failed: invalid API key")
            return is_valid
        except Exception as e:
            logger.error(f"API key verification error: {e}")
            return False
        


def hash_password(password: str) -> str:
        """password hashing"""
        try:
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            return hashed
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            raise


def verify_password(password: str, hashed: str) -> bool:
        """密码验证"""
        try:
            is_valid = bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
            if is_valid:
                logger.info("Password verification successful")
            else:
                logger.warning("Password verification failed: invalid password")
            return is_valid
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False

    
def create_access_token(user_id: str) -> str:
        """Create access token

        # 传统Session方式（有状态）
        # 服务器需要存储每个用户的登录状态
        sessions = {
            "session_123": {"user_id": "user_456", "login_time": "2024-01-01"}
        }

        # JWT方式（无状态）
        # 所有信息都编码在token中，服务器无需存储状态
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

        """
        try:
            expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
            payload = {
                "sub": user_id,  # Subject - 主题(用户ID)
                "exp": expire,  # Expiration time - 过期时间
                "iat": datetime.now(timezone.utc),  # Issued at - 发行时间
                "type": "access"  # Custom - 自定义字段
            }

            # 使用标准HS256算法
            token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
            logger.info(f"Created access token for user {user_id}, expires at {expire}")
            return token
        except Exception as e:
            logger.error(f"Failed to create access token for user {user_id}: {e}")
            raise

    
def create_refresh_token() -> str:
        """Create refresh token
        Access Token过期时 或者 前端自动请求刷新token时触发
        1. 验证refresh_token是否有效
        2. 删除旧的refresh_token
        3. 生成新的access_token和refresh_token
        4. 返回新的token对
        """
        try:
            token = secrets.token_urlsafe(32)
            logger.info(f"Created refresh token: {token[:8]}...")
            return token
        except Exception as e:
            logger.error(f"Failed to create refresh token: {e}")
            raise

    
def verify_token(token: str) -> Dict[str, Any]:
        """Verify token"""
        try:
            logger.debug(f"Verifying token: {token[:10]}...")

            # Step 1: JWT结构验证和签名验证
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

            # Step 2: 检查必需字段
            user_id = payload.get("sub")
            if not user_id:
                logger.warning(f"Token verification failed: missing user_id in payload")
                raise HTTPException(status_code=401, detail="Invalid token")
            logger.info(f"Token verified successfully for user {user_id}")

            # Step 3: 自动检查过期时间（jwt.decode会自动检查exp字段）
            # 如果过期会抛出jwt.ExpiredSignatureError
            return {"user_id": user_id, "payload": payload}
        except jwt.ExpiredSignatureError:
            # Token过期
            logger.warning(f"Token verification failed: token expired")
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            # Token无效
            logger.warning(f"Token verification failed: invalid token")
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise HTTPException(status_code=401, detail="Token verification failed")


def hash_refresh_token(token: str) -> str:
        """hash refresh token"""
        try:
            hashed = hashlib.sha256(token.encode()).hexdigest()
            logger.debug(f"Refresh token hashed: {hashed[:8]}...")
            return hashed
        except Exception as e:
            logger.error(f"Failed to hash refresh token: {e}")
            raise


def get_refresh_token_expire_time() -> datetime:
        """get refresh token expire time"""
        try:
            expire_time = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            logger.debug(f"Refresh token expire time calculated: {expire_time}")
            return expire_time
        except Exception as e:
            logger.error(f"Failed to calculate refresh token expire time: {e}")
            raise


def is_token_expired(token: str) -> bool:
        """check token is expired"""
        try:
            logger.debug(f"Checking token expiration: {token[:10]}...")
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            exp = payload.get("exp")
            if exp:
                is_expired = datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc)
                if is_expired:
                    logger.info("Token is expired")
                else:
                    logger.debug("Token is still valid")
                return is_expired
            logger.warning("Token has no expiration time")
            return True
        except Exception as e:
            logger.error(f"Error checking token expiration: {e}")
            return True


async def get_account_id_from_thread(client, thread_id: str) -> str:
        """
        Get account ID from thread ID

        Args:
            client: database client
            thread_id: thread ID

        Returns:
            str: USER ID

        Raises:
            HTTPException: if thread not found
        """
        try:
            thread_result = await client.table('threads').select('account_id').eq('thread_id', thread_id).execute()
            if not thread_result.data:
                logger.error(f"Thread not found: {thread_id}")
                raise HTTPException(status_code=404, detail="Thread not found")

            account_id = thread_result.data[0]['account_id']
            logger.debug(f"Retrieved account_id {account_id} for thread {thread_id}")
            return account_id

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting account_id from thread {thread_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error retrieving account information: {str(e)}")

async def get_current_user_id_from_jwt(
            request: Request
    ) -> str:
        """
        从JWT token中提取用户ID
        这个函数替代原来的 get_current_user_id_from_jwt，保持接口兼容
        """
        # 对于OPTIONS请求，跳过认证检查
        if request.method == "OPTIONS":
            return "anonymous"  # 返回一个占位符，不会被使用

        # 检查Authorization头
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(
                status_code=401,
                detail="该用户未认证",
                headers={"WWW-Authenticate": "Bearer"}
            )

        token = auth_header.split(' ')[1]

        try:
            token_data = verify_token(token)
            user_id = token_data["user_id"]

            logger.debug(f"Authenticated user: {user_id}")
            return user_id

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"JWT verification error: {e}")
            raise HTTPException(
                status_code=401,
                detail="无效认证信息",
                headers={"WWW-Authenticate": "Bearer"}
            )

async def get_user_id_from_stream_auth(
            request: Request,
            token: Optional[str] = None
    ) -> str:
        """
        支持流式端点的认证
        """
        try:
            # 首先尝试标准认证
            return await get_current_user_id_from_jwt(request)
        except HTTPException:
            pass

        # 尝试从查询参数获取token（用于EventSource）
        if token:
            try:
                token_data = verify_token(token)
                return token_data["user_id"]
            except Exception:
                pass

        raise HTTPException(
            status_code=401,
            detail="No valid authentication credentials found",
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_optional_user_id(request: Request) -> Optional[str]:
        """
        可选的用户认证，不强制要求认证
        """
        try:
            return await get_current_user_id_from_jwt(request)
        except HTTPException:
            return None

    # 为了兼容现有代码，保持相同的函数名
async def verify_thread_access(client, thread_id: str, user_id: str):
        """
        验证用户对线程的访问权限
        """
        try:
            # 查询线程的完整信息
            thread_result = await client.table('threads').select('*').eq('thread_id', thread_id).execute()

            if not thread_result.data:
                raise HTTPException(status_code=404, detail="Thread not found")

            thread_data = thread_result.data[0]
            thread_user_id = thread_data['account_id']

            # 1. 检查是否为线程所有者
            if thread_user_id == user_id:
                return True

            # # 2. 检查项目是否为公开项目 TODO：如果涉及项目公开需求，可以放开，示例：
            # project_id = thread_data.get('project_id')
            # if project_id:
            #     project_result = await client.table('projects').select('is_public').eq('project_id', project_id).execute()
            #     if project_result.data and len(project_result.data) > 0:
            #         if project_result.data[0].get('is_public'):
            #             return True

            # 3. 检查是否为账户成员（如果需要团队协作功能）
            # 这里可以根据你的具体需求实现账户成员检查
            # 例如：检查用户是否在同一个账户/团队中

            # 如果都不满足，则拒绝访问
            raise HTTPException(status_code=403, detail="Not authorized to access this thread")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error verifying thread access: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error verifying thread access: {str(e)}"
            )