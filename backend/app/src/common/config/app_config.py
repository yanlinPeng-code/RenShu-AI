import contextlib
import os

from  fastapi import  FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.src.response.exception.global_exception import GlobalReOrExHandler
from app.src.common.config.prosgresql_config import async_db_manager
from app.src.response.response_middleware import ResponseMiddleware
from app.src.utils import get_logger
from app.src.controller import account_router, model_config_router
from app.src.middleware.auth_middleware import AuthContextMiddleware

from app.src.common.config.prosgresql_config import create_db_tables

# from app.src.common.config.prosgresql_config import create_db_tables

# 创建日志记录器
logger = get_logger("app")







def add_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    # 添加响应中间件
    app.add_middleware(
        ResponseMiddleware,
        enable_tracing=True,
        enable_request_id=True
    )
    # 添加认证上下文中间件（自动解析JWT并设置用户上下文）
    app.add_middleware(AuthContextMiddleware)




async  def init_resource():
      logger.info("正在注册数据库")

      #初始化PostgreSQL配置

      await async_db_manager.init()
      # await model_manager_init.init()
      # await create_db_tables()
      # await preload_all_on_startup()
      logger.info("注册数据库完成")





async def register_router(app:FastAPI):
    #这里注册的是新版本的路由。

    logger.info("正在注册路由")
    app.include_router(account_router)
    app.include_router(model_config_router)
    logger.info("注册路由完成")






@contextlib.asynccontextmanager
async def life_span(app:FastAPI):
    logger.info(f"正在启动fastapi应用")
    try:
         #初始化数据库
         await init_resource()
         #注册路由
         await register_router(app)
         yield
    finally:
         logger.error(f"fastapi应用关闭")

def create_app():
    logger.info("创建 FastAPI 应用实例")
    
    app = FastAPI(
        title="SmartTCM-Agent-SYSTEM",
        description="智能中医代理系统",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=life_span
    )
    logger.info("正在注册全局异常管理器")
    GlobalReOrExHandler(app)
    logger.info("注册全局异常管理器成功")
    logger.info("正在注册中间件")
    add_middleware(app)
    logger.info("注册中间件成功")
    
    return app



