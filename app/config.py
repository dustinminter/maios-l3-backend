from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = "MAIOS L3 Orchestration Engine"
    app_version: str = "0.1.0"
    debug: bool = False

    # API Keys
    anthropic_api_key: Optional[str] = None

    # CORS
    cors_origins: str = "*"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
