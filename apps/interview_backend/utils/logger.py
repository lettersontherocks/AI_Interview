"""
统一日志配置模块
提供结构化日志、自动轮转、请求追踪等功能
"""
import logging
import sys
import json
from datetime import datetime
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
from typing import Any, Dict
import traceback


class JSONFormatter(logging.Formatter):
    """JSON格式化器 - 输出结构化日志"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加请求上下文（如果存在）
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "session_id"):
            log_data["session_id"] = record.session_id

        # 添加额外字段
        if hasattr(record, "extra_data"):
            log_data["extra"] = record.extra_data

        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }

        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """彩色格式化器 - 控制台输出带颜色"""

    # ANSI颜色码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        # 添加颜色
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"

        # 格式化时间
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')

        # 构建日志消息
        log_parts = [
            f"{timestamp}",
            f"[{record.levelname}]",
            f"[{record.name}]",
        ]

        # 添加请求上下文
        if hasattr(record, "request_id"):
            log_parts.append(f"[req:{record.request_id[:8]}]")
        if hasattr(record, "user_id"):
            log_parts.append(f"[user:{record.user_id[:12]}]")

        log_parts.append(f"{record.getMessage()}")

        # 添加位置信息（仅DEBUG级别）
        if record.levelno == logging.DEBUG:
            log_parts.append(f"({record.filename}:{record.lineno})")

        message = " ".join(log_parts)

        # 添加异常信息
        if record.exc_info:
            message += "\n" + self.formatException(record.exc_info)

        return message


def setup_logger(
    name: str = "ai_interview",
    log_dir: str = "logs",
    log_level: str = "INFO",
    enable_console: bool = True,
    enable_file: bool = True,
    json_format: bool = False
) -> logging.Logger:
    """
    配置并返回logger实例

    Args:
        name: logger名称
        log_dir: 日志目录
        log_level: 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        enable_console: 是否输出到控制台
        enable_file: 是否输出到文件
        json_format: 文件日志是否使用JSON格式

    Returns:
        配置好的logger实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    logger.handlers.clear()  # 清除已有的handler

    # 创建日志目录
    if enable_file:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

    # 控制台处理器（带颜色）
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(ColoredFormatter())
        logger.addHandler(console_handler)

    # 文件处理器 - 应用日志（按天轮转）
    if enable_file:
        app_log_path = log_path / "app.log"

        # 按天轮转，保留30天
        file_handler = TimedRotatingFileHandler(
            filename=str(app_log_path),
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8"
        )
        file_handler.suffix = "%Y-%m-%d"
        file_handler.setLevel(logging.DEBUG)

        if json_format:
            file_handler.setFormatter(JSONFormatter())
        else:
            file_handler.setFormatter(
                logging.Formatter(
                    '%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
            )
        logger.addHandler(file_handler)

        # 错误日志单独记录（按大小轮转）
        error_log_path = log_path / "error.log"
        error_handler = RotatingFileHandler(
            filename=str(error_log_path),
            maxBytes=100 * 1024 * 1024,  # 100MB
            backupCount=10,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)

        if json_format:
            error_handler.setFormatter(JSONFormatter())
        else:
            error_handler.setFormatter(
                logging.Formatter(
                    '%(asctime)s [%(levelname)s] [%(name)s] %(message)s\n'
                    'Location: %(pathname)s:%(lineno)d\n'
                    '%(message)s\n',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
            )
        logger.addHandler(error_handler)

    return logger


class LoggerAdapter(logging.LoggerAdapter):
    """
    日志适配器 - 自动添加上下文信息
    """

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """处理日志消息，添加上下文"""
        # 将extra字段添加到record中
        if "extra" not in kwargs:
            kwargs["extra"] = {}

        # 合并适配器的extra字段
        kwargs["extra"].update(self.extra)

        return msg, kwargs


def get_logger(name: str = None) -> logging.Logger:
    """
    获取logger实例（便捷方法）

    Args:
        name: logger名称，如果为None则使用调用模块名

    Returns:
        logger实例
    """
    if name is None:
        # 自动获取调用模块名
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'ai_interview')

    return logging.getLogger(name)


# 全局logger实例
logger = setup_logger(
    name="ai_interview",
    log_level="INFO",
    enable_console=True,
    enable_file=True,
    json_format=False  # 生产环境可以改为True
)


# 便捷的日志函数
def log_info(message: str, **kwargs):
    """记录INFO日志"""
    logger.info(message, extra={"extra_data": kwargs})


def log_error(message: str, exc_info=None, **kwargs):
    """记录ERROR日志"""
    logger.error(message, exc_info=exc_info, extra={"extra_data": kwargs})


def log_warning(message: str, **kwargs):
    """记录WARNING日志"""
    logger.warning(message, extra={"extra_data": kwargs})


def log_debug(message: str, **kwargs):
    """记录DEBUG日志"""
    logger.debug(message, extra={"extra_data": kwargs})


# 测试代码
if __name__ == "__main__":
    # 测试日志系统
    test_logger = setup_logger(log_level="DEBUG")

    test_logger.debug("这是一条调试日志")
    test_logger.info("这是一条信息日志")
    test_logger.warning("这是一条警告日志")
    test_logger.error("这是一条错误日志")

    try:
        1 / 0
    except Exception as e:
        test_logger.error("捕获到异常", exc_info=True)

    print("\n日志测试完成！请检查 logs/ 目录")
