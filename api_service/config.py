from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    
    api_host: str = "0.0.0.0"
    api_port: int = 8001
    api_title: str = "Claude API Service Platform"
    api_version: str = "1.0.0"

    # CORS Configuration
    allow_origins: str = "*"
    allow_credentials: bool = True
    allow_methods: str = "*"
    allow_headers: str = "*"

    # Rate Limiting
    max_requests_per_minute: int = 60
    max_tokens_per_request: int = 4096

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
