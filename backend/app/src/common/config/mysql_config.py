# import contextlib
# from typing import Optional, AsyncGenerator, Annotated
#
# from fastapi import Depends
# from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker,create_async_engine
# from sqlalchemy.orm import declarative_base
#
# from sqlmodel.ext.asyncio.session import AsyncSession
#
#
# class MysqlSessionManager:
#     """管理异步的MysqlSession和连接池"""
#
#     def __init__(self):
#         self.async_engine:Optional[AsyncEngine]=None
#         self.async_session_factory:Optional[async_sessionmaker[AsyncSession]]=None
#
#     async def init(self)->None:
#         """初始化数据库配置"""
#         logger.info("----------初始化数据库配置----------------!")
#
#         #创建mysql的异步引擎
#         self.async_engine=create_async_engine(
#             url=settings.connection_url,
#             pool_size=settings.MYSQL_POOL_SIZE,
#             echo=settings.MYSQL_ECHO,
#             max_overflow=settings.MYSQL_MAX_OVERFLOW,
#             pool_recycle=settings.MYSQL_POOL_RECYCLE,
#             pool_pre_ping=True
#         )
#         logger.info(
#             "--------------mysql数据库异步引擎创建成功----------------",
#         )
#         print(settings.connection_url)
#
#         self.async_session_factory=async_sessionmaker(
#             bind=self.async_engine,
#             class_=AsyncSession,
#             expire_on_commit=False,
#             autoflush=False
#         )
#         logger.info("---------------数据库工厂类会话创建成功----------------")
#
#         logger.info("-----------数据库连接成功-----------")
#
#
#     async def close(self):
#         """关闭数据库引擎"""
#         if self.async_engine:
#             logger.info("------------正在关闭数据库连接！------------")
#             await self.async_engine.dispose()
#             logger.info("---------数据库连接已关闭！--------")
#
#
#
#     @contextlib.asynccontextmanager
#     async def get_session(self)->AsyncGenerator[AsyncSession, None]:
#         """
#         获取一个事务安全的session对话，
#
#
#         """
#         if self.async_session_factory is None:
#             raise Exception("-----------请先初始化数据库连接！------------")
#
#         async with self.async_session_factory() as session:
#             async with session.begin():
#                 yield session
# Base=declarative_base()
#
# mysql_session_manager=MysqlSessionManager()
#
# def get_session_factory():
#     """
#     获取数据库会话工厂
#     """
#     return mysql_session_manager.async_session_factory()
#
#
#
# async  def get_db()->AsyncGenerator[AsyncSession, None]:
#     """
#     FASTAPI 依赖注入会话生成器
#     用法：
#     @Depends(get_db)
#
#
#
#     """
#     async with mysql_session_manager.get_session() as session:
#         yield session
#
#
#
#
#
# SessionDep=Annotated[AsyncSession, Depends(get_db)]
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
