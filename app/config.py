from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    app_base_url: str = "http://localhost"
    app_domain: str = "news.ieltstask.com"
    site_name: str = "News"
    asset_version: str = "2026.07.16.2"
    database_url: str = "sqlite:///./data/news.db"
    data_dir: Path = Path("data")
    session_secret: str = Field(default="development-only-session-secret-change-me", min_length=32)
    admin_username: str = "sainaveennews"
    admin_password: str = Field(default="change-me-before-production", min_length=12)
    max_upload_mb: int = Field(default=2048, ge=1, le=10240)
    max_archive_files: int = Field(default=20000, ge=1, le=100000)
    max_archive_uncompressed_mb: int = Field(default=8192, ge=1, le=51200)
    google_site_verification: str = ""
    ga_measurement_id: str = ""
    adsense_publisher_id: str = ""

    @field_validator("app_base_url")
    @classmethod
    def normalize_base_url(cls, value: str) -> str:
        if not value.startswith(("http://", "https://")):
            raise ValueError("APP_BASE_URL must start with http:// or https://")
        return value.rstrip("/")

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def upload_limit_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

    @property
    def archive_limit_bytes(self) -> int:
        return self.max_archive_uncompressed_mb * 1024 * 1024

    @property
    def imports_dir(self) -> Path:
        return self.data_dir / "imports"

    @property
    def media_dir(self) -> Path:
        return self.data_dir / "media"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.imports_dir.mkdir(parents=True, exist_ok=True)
    settings.media_dir.mkdir(parents=True, exist_ok=True)
    return settings
