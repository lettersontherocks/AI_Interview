"""AI面试系统配置"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 阿里云配置（同时用于语音识别和大模型）
    dashscope_api_key: str = "sk-088194a0fd464b2199940e165f9ae1ac"

    # 数据库配置（默认 PostgreSQL，支持环境变量覆盖）
    database_url: str = "postgresql://interview_user:interview_pass_2024@postgres:5432/ai_interview"

    # 微信小程序配置
    wechat_app_id: str = ""
    wechat_app_secret: str = ""

    # 支付配置
    wechat_mch_id: str = ""
    wechat_pay_key: str = ""

    # 业务配置
    free_daily_limit: int = 2 # 免费用户每天次数
    vip_monthly_price: float = 9.98  # 月度会员价格
    single_interview_price: float = 0.99  # 单次面试价格

    class Config:
        env_file = ".env"


settings = Settings()
