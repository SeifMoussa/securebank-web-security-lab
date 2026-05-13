"""Application settings."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="SECUREBANK_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = "development"
    debug: bool = False
    database_url: str = "sqlite:///./securebank_lab.sqlite3"
    secret_key: str = Field(default="change-me-in-local-development", min_length=16)
    session_cookie_name: str = "securebank_lab_session"
    session_max_age_seconds: int = 3600
    secure_cookie: bool = False
    csrf_cookie_name: str = "securebank_lab_csrf"
    csrf_token_max_age_seconds: int = 3600
    hsts_enabled: bool = False
    login_lockout_enabled: bool = False
    login_lockout_max_attempts: int = 5
    login_lockout_window_seconds: int = 900
    seed_demo_data: bool = True


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
