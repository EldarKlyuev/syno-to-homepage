"""
Core configuration settings for Synology API proxy.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with Synology NAS configuration."""
    
    # App settings
    APP_NAME: str = "Synology API Proxy"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # Synology NAS settings
    SYNOLOGY_URL: str  # https://192.168.1.1:5001
    SYNOLOGY_USER: str
    SYNOLOGY_PASSWORD: str
    SYNOLOGY_VERIFY_SSL: bool = False
    SYNOLOGY_SESSION_TIMEOUT: int = 3600  # 1 hour in seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()