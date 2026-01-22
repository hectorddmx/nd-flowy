from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.devcontainer", ".env.development"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Workflowy API
    wf_api_key: str
    wf_api_base_url: str = "https://workflowy.com/api/v1"

    # Database
    database_path: Path = Path("workflowy_flow.db")

    # App
    app_name: str = "Workflowy Flow"
    debug: bool = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
