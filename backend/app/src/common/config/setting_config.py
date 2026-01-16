from datetime import timedelta
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

# 计算项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent.parent.parent


class Settings(BaseSettings):

    JWT_SECRET_KEY: str = Field(default="your_jwt_secret_key", description="JWT密钥")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT算法")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="JWT访问令牌有效期（分钟）")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30, description="JWT刷新令牌有效期（天）")


    # 未知配置（保持注释，需要时可启用）
    # BASE_URL: str = Field(..., description="基础URL")
    # CHAT_MODEL: str = Field(..., description="模型名称")
    # API_KEY: str = Field(..., description="API_KEY")

    # 阿里云模型配置（保持注释，需要时可启用）
    # ALI_BASE_URL: str = Field(..., description="阿里云模型基础URL")
    # ALI_API_KEY: str = Field(..., description="阿里云模型API_KEY")
    # ALI_CHAT_MODEL: str = Field(..., description="阿里云模型名称")
    # ALI_EMBEDDING_MODEL: str = Field(..., description="阿里云模型Embedding_MODEL")

    # 向量数据库配置（保持注释，需要时可启用）
    # SERVER_HOST: str = Field(..., description="向量数据库HOST")
    # SERVER_PORT: int = Field(..., description="向量数据库PORT")
    # DB_NAME: str = Field(..., description="向量数据库名称")

    # 数据库配置（与环境变量对应）
    POSTGRESQL_DATABASE_NAME: str = Field(default="your_database_name", description="所连接的数据库名称")
    POSTGRESQL_ASYNC_DRIVER: str = Field(default="asyncpg", description="异步数据库驱动")
    POSTGRESQL_SYNC_DRIVER: str = Field(default="psycopg2", description="同步数据库驱动")
    POSTGRESQL_USER_NAME: str = Field(default="your_username", description="数据库用户名")
    POSTGRESQL_PASSWORD: str = Field(default="your_password", description="数据库密码")
    POSTGRESQL_HOST: str = Field(default="localhost", description="数据库地址")
    POSTGRESQL_PORT: int = Field(default=5432, description="数据库端口")
    POSTGRESQL_POOL_SIZE: int = Field(default=20, description="数据库连接池大小")
    POSTGRESQL_MAX_OVERFLOW: int = Field(default=10, description="数据库连接池溢出大小")
    POSTGRESQL_POOL_RECYCLE: int = Field(default=3600, description="数据库连接池回收时间")
    POSTGRESQL_ECHO: bool = Field(default=False, description="数据库是否打印SQL")
    POSTGRESQL_POOL_TIMEOUT:int=300
    # 谷歌搜索配置
    SERPER_API_KEY: str = Field(default="your_serper_api_key", description="谷歌搜索API_KEY")


    DEEPSEEK_API_KEY:str=Field(default="",description="deepseek的apikey")
    DEEPSEEK_BASE_URL:str=Field(default="",description="deepseek的base_url")
    OPENAI_API_KEY:str=Field(default="",description="openai的apikey")
    OPENAI_BASE_URL:str=Field(default="",description="openai的base_url")
    DASHSCOPE_API_KEY:str=Field(default="",description="tongyi的apikey")
    DASHSCOPE_BASE_URL:str=Field(default="",description="tongyi的base_url")

    # langsmith配置（保持注释，需要时可启用）
    # LANGSMITH_TRACING: bool = Field(..., description="是否开启langsmith")
    # LANGSMITH_ENDPOINT: str = Field(..., description="langsmith endpoint")
    # LANGSMITH_API_KEY: str = Field(..., description="langsmith api_key")

    @computed_field
    @property
    def async_connection_url(self) -> str:
        """构建异步数据库连接URL"""
        encoded_password = quote_plus(self.POSTGRESQL_PASSWORD)
        return (
            f"postgresql+{self.POSTGRESQL_ASYNC_DRIVER}://"
            f"{self.POSTGRESQL_USER_NAME}:{encoded_password}@"
            f"{self.POSTGRESQL_HOST}:{self.POSTGRESQL_PORT}/"
            f"{self.POSTGRESQL_DATABASE_NAME}"
        )

    @computed_field
    @property
    def sync_connection_url(self) -> str:
        """构建同步数据库连接URL"""
        encoded_password = quote_plus(self.POSTGRESQL_PASSWORD)
        return (
            f"postgresql+{self.POSTGRESQL_SYNC_DRIVER}://"
            f"{self.POSTGRESQL_USER_NAME}:{encoded_password}@"
            f"{self.POSTGRESQL_HOST}:{self.POSTGRESQL_PORT}/"
            f"{self.POSTGRESQL_DATABASE_NAME}"
        )

    model_config = ConfigDict(
        # 环境变量文件路径（通常命名为.env，这里保持你的配置）
        env_file=str(ROOT_DIR / ".env"),  # 修复：正确指定.env文件路径
        env_file_encoding="utf-8",
        extra="ignore"  # 忽略未定义的环境变量
    )


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
if __name__ == '__main__':
    print(f"Root directory: {ROOT_DIR}")
    print(f"Environment file path: {ROOT_DIR / '.env'}")
    print("Settings loaded successfully!")
    print(f"Async connection URL: {settings.OPENAI_BASE_URL}")



