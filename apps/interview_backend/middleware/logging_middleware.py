"""
请求日志中间件
自动记录所有HTTP请求和响应，提供请求追踪功能
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

logger = logging.getLogger("ai_interview")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件
    功能：
    1. 为每个请求生成唯一的request_id
    2. 记录请求的基本信息（方法、路径、参数）
    3. 记录响应状态码和耗时
    4. 捕获并记录异常
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成唯一的请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # 记录开始时间
        start_time = time.time()

        # 获取请求信息
        method = request.method
        url = str(request.url)
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"

        # 记录请求开始
        logger.info(
            f"📥 Request started: {method} {path}",
            extra={
                "request_id": request_id,
                "extra_data": {
                    "method": method,
                    "url": url,
                    "client_ip": client_host,
                    "user_agent": request.headers.get("user-agent", ""),
                }
            }
        )

        # 处理请求
        try:
            response = await call_next(request)

            # 计算耗时
            duration = time.time() - start_time
            duration_ms = round(duration * 1000, 2)

            # 确定日志级别（根据状态码）
            status_code = response.status_code
            if status_code >= 500:
                log_level = logging.ERROR
                emoji = "❌"
            elif status_code >= 400:
                log_level = logging.WARNING
                emoji = "⚠️"
            else:
                log_level = logging.INFO
                emoji = "✅"

            # 记录响应
            logger.log(
                log_level,
                f"{emoji} Request completed: {method} {path} - {status_code} ({duration_ms}ms)",
                extra={
                    "request_id": request_id,
                    "extra_data": {
                        "method": method,
                        "path": path,
                        "status_code": status_code,
                        "duration_ms": duration_ms,
                        "client_ip": client_host,
                    }
                }
            )

            # 慢请求警告（超过2秒）
            if duration > 2.0:
                logger.warning(
                    f"🐌 Slow request detected: {method} {path} took {duration_ms}ms",
                    extra={
                        "request_id": request_id,
                        "extra_data": {
                            "duration_ms": duration_ms,
                            "threshold_ms": 2000,
                        }
                    }
                )

            # 添加request_id到响应头（方便前端追踪）
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # 计算耗时
            duration = time.time() - start_time
            duration_ms = round(duration * 1000, 2)

            # 记录异常
            logger.error(
                f"💥 Request failed: {method} {path} - {type(e).__name__}: {str(e)}",
                exc_info=True,
                extra={
                    "request_id": request_id,
                    "extra_data": {
                        "method": method,
                        "path": path,
                        "duration_ms": duration_ms,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                    }
                }
            )

            # 重新抛出异常，让FastAPI的异常处理器处理
            raise


class ContextLoggingMiddleware(BaseHTTPMiddleware):
    """
    上下文日志中间件
    将请求上下文（request_id, user_id等）注入到日志记录器
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 从请求中提取用户ID（如果存在）
        user_id = None

        # 尝试从query参数获取user_id
        if "user_id" in request.query_params:
            user_id = request.query_params["user_id"]

        # 尝试从请求体获取user_id（对于POST请求）
        if not user_id and request.method == "POST":
            try:
                # 注意：这里不能直接读取body，因为会被消费掉
                # 实际项目中可以从认证token中获取user_id
                pass
            except:
                pass

        # 保存用户ID到请求状态
        if user_id:
            request.state.user_id = user_id

        response = await call_next(request)
        return response


def log_with_context(logger_instance: logging.Logger, request: Request):
    """
    创建带有请求上下文的logger适配器

    使用方法:
        logger = log_with_context(logger, request)
        logger.info("这条日志会自动包含request_id和user_id")
    """
    extra = {}

    if hasattr(request.state, "request_id"):
        extra["request_id"] = request.state.request_id

    if hasattr(request.state, "user_id"):
        extra["user_id"] = request.state.user_id

    return logging.LoggerAdapter(logger_instance, extra)
