"""Configuration settings for AutoVPN."""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = "sqlite:///./autovpn.db"

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Admin setup
    admin_master_password: Optional[str] = None

    # File storage
    upload_dir: str = "./uploads"
    download_dir: str = "./downloads"
    static_dir: str = "./autovpn/web/static"

    # Puppeteer settings
    puppeteer_headless: bool = True  # Set to True for production
    puppeteer_timeout: int = 30000

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


# Ensure directories exist
def ensure_directories():
    """Ensure required directories exist."""
    Path(settings.upload_dir).mkdir(exist_ok=True)
    Path(settings.download_dir).mkdir(exist_ok=True)
    Path(settings.static_dir).mkdir(exist_ok=True)
