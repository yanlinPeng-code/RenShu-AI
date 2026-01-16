import contextlib
from typing import Optional, AsyncGenerator, Generator, Annotated
from fastapi import Depends
from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    Session as SyncSession,
)
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.src.common.config.setting_config import settings
from app.src.utils.logs.logger import get_logger

# 创建日志记录器
logger = get_logger("sql")
# 共享的基础模型类
Base = declarative_base()


class PostgreSQLAsyncSessionManager:
    """管理异步的PostgreSQL Session和连接池（修复版）"""

    def __init__(self):
        self.async_engine: Optional[AsyncEngine] = None
        self.async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None

    async def init(self) -> None:
        """初始化异步数据库配置"""
        logger.info("----------初始化异步数据库配置----------------!")

        self.async_engine = create_async_engine(
            url=settings.async_connection_url,
            pool_size=settings.POSTGRESQL_POOL_SIZE,
            echo=settings.POSTGRESQL_ECHO,
            max_overflow=settings.POSTGRESQL_MAX_OVERFLOW,
            pool_recycle=settings.POSTGRESQL_POOL_RECYCLE,
            pool_timeout=settings.POSTGRESQL_POOL_TIMEOUT,
            pool_pre_ping=True  # 健康检查：确保连接可用
        )
        logger.info("--------------PostgreSQL异步引擎创建成功----------------")
        print(f"异步连接URL: {settings.async_connection_url}")

        self.async_session_factory = async_sessionmaker(
            bind=self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False,  # 提交后不失效对象（避免重复查询）
            autoflush=False,  # 关闭自动刷新（手动控制更安全）
            autocommit=False  # 事务手动控制
        )
        logger.info("---------------异步会话工厂创建成功----------------")

    async def close(self):
        """关闭异步数据库引擎"""
        if self.async_engine:
            logger.info("------------正在关闭异步数据库连接！------------")
            await self.async_engine.dispose()
            logger.info("---------异步数据库连接已关闭！--------")

    @contextlib.asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        if self.async_session_factory is None:
            await self.init()

        session = self.async_session_factory()
        try:
            # 使用 session.begin() 开启事务上下文
            # 它会自动处理 commit (成功时) 和 rollback (异常时)
            # 并且能正确处理 BaseException
            async with session.begin():
                logger.debug(f"🔄 开启新事务，会话ID: {id(session)}")
                yield session

            # 注意：离开 async with session.begin() 块时会自动 commit
            logger.debug(f"✅ 事务自动提交成功，会话ID: {id(session)}")

        except Exception as e:
            # 这里的 rollback 是多重保险，session.begin 已经处理了
            logger.error(f"❌ 数据库事务失败: {str(e)}", exc_info=True)
            raise
        finally:
            await session.close()
            logger.debug(f"🔌 会话已关闭，ID: {id(session)}")

class PostgreSQLSyncSessionManager:
    """管理同步的PostgreSQL Session和连接池（修复版）"""

    def __init__(self):
        self.engine: Optional[Engine] = None
        self.session_factory: Optional[sessionmaker[SyncSession]] = None

    def init(self) -> None:
        """初始化同步数据库配置"""
        logger.info("----------初始化同步数据库配置----------------!")

        self.engine = create_engine(
            url=settings.sync_connection_url,
            pool_size=settings.POSTGRESQL_POOL_SIZE,
            echo=settings.POSTGRESQL_ECHO,
            max_overflow=settings.POSTGRESQL_MAX_OVERFLOW,
            pool_recycle=settings.POSTGRESQL_POOL_RECYCLE,
            pool_timeout=settings.POSTGRESQL_POOL_TIMEOUT,
            pool_pre_ping=True
        )
        logger.info("--------------PostgreSQL同步引擎创建成功----------------")
        print(f"同步连接URL: {settings.sync_connection_url}")

        self.session_factory = sessionmaker(
            bind=self.engine,
            class_=SyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False
        )
        logger.info("---------------同步会话工厂创建成功----------------")

    def close(self):
        """关闭同步数据库引擎"""
        if self.engine:
            logger.info("------------正在关闭同步数据库连接！------------")
            self.engine.dispose()
            logger.info("---------同步数据库连接已关闭！--------")

    @contextlib.contextmanager
    def get_session(self) -> Generator[SyncSession, None, None]:
        """获取事务安全的同步session（修复核心逻辑）"""
        if self.session_factory is None:
            raise Exception("-----------请先初始化同步数据库连接！------------")

        with self.session_factory() as session:
            try:
                session.begin()  # 开启事务
                yield session
            except Exception as e:
                session.rollback()
                logger.error(f"同步数据库会话出错，已回滚: {str(e)}", exc_info=True)
                raise
            # 无异常时，上下文自动commit；无需手动close（with已处理）


# 实例化管理器
async_db_manager = PostgreSQLAsyncSessionManager()
sync_db_manager = PostgreSQLSyncSessionManager()


# 异步会话依赖（FastAPI使用）
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_db_manager.get_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]


# 同步会话依赖（FastAPI使用）
def get_sync_db() -> Generator[SyncSession, None, None]:
    with sync_db_manager.get_session() as session:
        yield session


SyncSessionDep = Annotated[SyncSession, Depends(get_sync_db)]


# 快捷初始化和关闭函数
async def init_dbs():
    """初始化所有数据库连接"""
    await async_db_manager.init()
    sync_db_manager.init()


async def close_dbs():
    """关闭所有数据库连接"""
    await async_db_manager.close()
    sync_db_manager.close()


async def create_db_tables():
    """创建所有 SQLModel 表（如果不存在）"""
    # 导入模型以确保它们被注册到 SQLModel.metadata
    # 从统一入口导入所有模型
    from app.src.model import (
        # 用户相关模型
        User, Patient, UserSession, UserState, UserActivity, RefreshToken,
        # 对话相关模型
        Conversation, Message,
        # 医疗相关模型
        MedicalCase, Symptom, Syndrome, MedicalRecord, TongueAnalysis,
        PrescriptionRecommendation,
        # 药材相关模型
        Herb, HerbInventory, Prescription, ClassicText,
        # 系统相关模型
        SystemConfig, SystemStats, DatabaseStats, HealthCheck, LogEntry,
        AuditLog, BackupInfo, SystemInfo
    )

    if async_db_manager.async_engine is None:
        raise Exception("请先初始化数据库连接")

    async with async_db_manager.async_engine.begin() as conn:
        # 使用 checkfirst 参数只创建不存在的表，避免重复创建
        await conn.run_sync(lambda sync_conn: SQLModel.metadata.create_all(sync_conn, checkfirst=True))
        logger.info("数据库表创建/检查完成")


async def drop_db_tables():
    """删除所有 SQLModel 表"""
    # 导入模型以确保它们被注册到 SQLModel.metadata
    # 从统一入口导入所有模型
    from app.src.model import (
        # 用户相关模型
        User, Patient, UserSession, UserState, UserActivity, RefreshToken,
        # 对话相关模型
        Conversation, Message,
        # 医疗相关模型
        MedicalCase, Symptom, Syndrome, MedicalRecord, TongueAnalysis,
        PrescriptionRecommendation,
        # 药材相关模型
        Herb, HerbInventory, Prescription, ClassicText,
        # 系统相关模型
        SystemConfig, SystemStats, DatabaseStats, HealthCheck, LogEntry,
        AuditLog, BackupInfo, SystemInfo
    )

    if async_db_manager.async_engine is None:
        raise Exception("请先初始化数据库连接")

    async with async_db_manager.async_engine.begin() as conn:
        # 删除所有表
        await conn.run_sync(lambda sync_conn: SQLModel.metadata.drop_all(sync_conn))
        logger.info("数据库表删除成功")
