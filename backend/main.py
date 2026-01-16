import os
import time
from fastapi import FastAPI
from app.src.common.config.app_config import create_app
from app.src.response.utils import success_200
from app.src.response.response_models import BaseResponse
from app.src.utils import get_logger

# 创建应用实例
app: FastAPI = create_app()
logger = get_logger("main")


@app.get("/", response_model=None)
async def root():
    """根路径 - 健康检查"""
    logger.info("健康检查请求")
    return success_200(
        data={
            "service": "SmartTCM-Agent-SYSTEM",
            "version": "1.0.0",
            "status": "healthy",
            "timestamp": time.time()
        },
        message="服务运行正常"
    )


@app.get("/health", response_model=BaseResponse[dict])
async def health_check():
    """健康检查接口"""
    logger.info("健康检查请求")
    return success_200(
        data={
            "status": "healthy",
            "timestamp": time.time(),
            "uptime": "running",
            "log_level": "INFO"
        },
        message="服务健康检查通过"
    )


@app.get("/logs/status", response_model=BaseResponse[dict])
async def logs_status():
    """日志状态检查"""
    logger.info("日志状态检查请求")

    log_files = []
    log_dir = "logs"
    if os.path.exists(log_dir):
        for file in os.listdir(log_dir):
            if file.endswith('.log'):
                file_path = os.path.join(log_dir, file)
                file_size = os.path.getsize(file_path)
                log_files.append({
                    "name": file,
                    "size_bytes": file_size,
                    "size_mb": round(file_size / 1024 / 1024, 2)
                })

    return success_200(
        data={
            "log_directory": log_dir,
            "log_files": log_files,
            "log_level": "INFO"
        },
        message="日志状态检查完成"
    )


@app.get("/test/logging", response_model=BaseResponse[dict])
async def test_logging():
    """测试日志功能"""
    logger.info("开始测试日志功能")
    logger.debug("这是调试信息")
    logger.info("这是信息日志")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")
    logger.info("日志功能测试完成")

    return success_200(
        data={
            "test": "logging",
            "levels_tested": ["debug", "info", "warning", "error"],
            "status": "success"
        },
        message="日志功能测试完成"
    )


if __name__ == "__main__":
    import uvicorn
    logger.info("应用启动中")
    uvicorn.run(
        app=app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
