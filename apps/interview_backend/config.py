"""AI面试系统配置"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Claude API配置
    

    # 数据库配置
    database_url: str = "sqlite:///./ai_interview.db"

    # 微信小程序配置
    wechat_app_id: str = ""
    wechat_app_secret: str = ""

    # 支付配置
    wechat_mch_id: str = ""
    wechat_pay_key: str = ""

    # 阿里云语音识别配置
    dashscope_api_key: str = "sk-088194a0fd464b2199940e165f9ae1ac"

    # 业务配置
    free_daily_limit: int = 1  # 免费用户每天次数
    vip_monthly_price: float = 29.9  # 月度会员价格
    single_interview_price: float = 9.9  # 单次面试价格

    class Config:
        env_file = ".env"


settings = Settings()
