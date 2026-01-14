"""AI面试系统配置"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    应用配置类 - 所有敏感信息都从环境变量读取

    使用方法：
    1. 复制 .env.example 为 .env
    2. 填写真实的密钥和密码
    3. 确保 .env 文件已加入 .gitignore
    """

    # ==================== 数据库配置 ====================
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "ai_interview"
    postgres_user: str = "interview_user"
    postgres_password: str  # 必须从环境变量提供，无默认值

    # 完整的数据库URL（如果提供则优先使用）
    database_url: Optional[str] = None

    @property
    def get_database_url(self) -> str:
        """获取数据库连接URL"""
        if self.database_url:
            return self.database_url
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    # ==================== AI服务配置 ====================
    dashscope_api_key: str  # 阿里云通义千问API Key，必须提供

    # ==================== 语音服务配置 ====================
    # 阿里云ASR（语音识别）
    aliyun_asr_app_key: str = ""
    aliyun_asr_access_key_id: str = ""
    aliyun_asr_access_key_secret: str = ""

    # 火山引擎TTS（豆包语音合成）
    volcengine_app_id: str = ""
    volcengine_access_token: str = ""

    # ==================== 微信小程序配置 ====================
    wechat_app_id: str = ""
    wechat_app_secret: str = ""

    # 支付配置（支付功能未实现，仅保留配置字段）
    wechat_mch_id: str = ""
    wechat_pay_key: str = ""

    # ==================== 业务配置 ====================
    free_user_daily_limit: int = 1  # 普通用户每天次数
    normal_vip_daily_limit: int = 2  # 普通VIP每天次数
    # 超级VIP无限次，无需配置

    vip_monthly_price: float = 9.98  # 月度会员价格
    single_interview_price: float = 0.99  # 单次面试价格

    # ==================== Elasticsearch配置 ====================
    es_host: str = "http://47.93.141.137:9200"  # ES 服务地址
    es_index: str = "interview_questions"  # ES 索引名
    es_username: str = ""
    es_password: str = ""

    # ==================== 应用配置 ====================
    port: int = 8003
    environment: str = "development"  # development, production, test
    log_level: str = "INFO"

    # CORS配置
    allowed_origins: str = "*"  # 生产环境应改为具体域名

    # ==================== 日志配置 ====================
    log_dir: str = "logs"  # 日志目录
    log_json_format: bool = False  # 是否使用JSON格式（生产环境建议True）
    log_retention_days: int = 30  # 日志保留天数
    log_max_bytes: int = 100 * 1024 * 1024  # 单个日志文件最大大小（100MB）

    @property
    def get_allowed_origins(self) -> list:
        """获取允许的CORS来源列表"""
        if self.allowed_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    # ==================== 文件存储配置 ====================
    audio_output_dir: str = "audio_outputs"
    resume_upload_dir: str = "uploads/resumes"
    file_cleanup_days: int = 7  # 文件自动清理天数，0表示不清理

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  # 环境变量不区分大小写


# 创建全局配置实例
settings = Settings()

# 启动时验证关键配置
def validate_settings():
    """验证关键配置是否已设置"""
    required_fields = {
        "dashscope_api_key": "阿里云DashScope API Key",
        "postgres_password": "数据库密码",
    }

    missing_fields = []
    for field, desc in required_fields.items():
        value = getattr(settings, field, None)
        if not value:
            missing_fields.append(f"{desc} ({field})")

    if missing_fields:
        error_msg = (
            "❌ 缺少必需的环境变量配置！\n\n"
            "缺少的配置项：\n" +
            "\n".join(f"  - {field}" for field in missing_fields) +
            "\n\n请执行以下步骤：\n"
            "1. 复制 .env.example 为 .env\n"
            "2. 在 .env 文件中填写所有必需的配置\n"
            "3. 重启应用\n"
        )
        raise ValueError(error_msg)

    # 安全提醒
    if settings.environment == "production" and settings.allowed_origins == "*":
        print("⚠️  警告：生产环境不应使用 CORS='*'，请在 .env 中设置具体域名")

    print("✅ 配置验证通过")
    print(f"📊 运行环境: {settings.environment}")
    print(f"🌐 数据库: {settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}")
    print(f"📁 音频目录: {settings.audio_output_dir}")
    print(f"🧹 文件清理: {settings.file_cleanup_days}天")
