"""面试后端主程序"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database.db import init_db
from api.routes import router
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    init_db()
    print("数据库初始化完成")
    yield
    # 关闭时清理资源
    print("应用关闭")


app = FastAPI(
    title="AI面试系统后端API",
    description="基于Claude的智能面试练习平台",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api/v1", tags=["interview"])


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
