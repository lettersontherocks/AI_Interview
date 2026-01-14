"""面试后端主程序"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import logging

from database.db import init_db
from api.routes import router
from config import settings
from utils.logger import setup_logger
from middleware.logging_middleware import RequestLoggingMiddleware

# 初始化日志系统
logger = setup_logger(
    name="ai_interview",
    log_dir=settings.log_dir,
    log_level=settings.log_level,
    enable_console=True,
    enable_file=True,
    json_format=settings.log_json_format
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    logger.info("🚀 应用启动中...")
    logger.info(f"📊 环境: {settings.environment}")
    logger.info(f"🌐 监听端口: {settings.port}")
    logger.info(f"📝 日志级别: {settings.log_level}")
    logger.info(f"📁 日志目录: {settings.log_dir}")

    init_db()
    logger.info("✅ 数据库初始化完成")

    yield

    # 关闭时清理资源
    logger.info("👋 应用正在关闭...")
    logger.info("✅ 应用已安全关闭")


app = FastAPI(
    title="AI面试系统后端API",
    description="基于阿里云通义千问Qwen的智能面试练习平台",
    version="1.0.0",
    lifespan=lifespan
)

# 添加请求日志中间件（最先添加，确保能捕获所有请求）
app.add_middleware(RequestLoggingMiddleware)

# CORS配置 - 从config读取
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api/v1", tags=["interview"])

# 挂载静态文件目录（用于TTS音频文件）
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI面试系统后端API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "interview-backend"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True
    )
