from __future__ import annotations

from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    environment: Literal["development", "testing", "production"] = "development"
    app_name: str = "IELTSTask Newsroom"
    app_domain: str = "localhost"
    allowed_hosts: str = "localhost,127.0.0.1,testserver"
    cookie_secure: bool = False

    db_host: str = "127.0.0.1"
    db_port: int = 5432
    db_name: str = "newswebsite"
    db_user: str = "newswebsite"
    db_password: str = "development-password"
    database_url: str | None = None

    admin_username: str = "sainaveennews"
    admin_password: str = "development-admin-password"
    session_secret: str = "development-session-secret-change-me"

    page_size: int = 12
    max_import_urls: int = 50
    fetch_concurrency: int = 5
    fetch_timeout_seconds: float = 12.0
    fetch_max_bytes: int = 2_097_152

    @property
    def sqlalchemy_url(self) -> str | URL:
        if self.database_url:
            return self.database_url
        return URL.create(
            "postgresql+psycopg",
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )

    @property
    def allowed_host_list(self) -> list[str]:
        return [host.strip() for host in self.allowed_hosts.split(",") if host.strip()]

    @model_validator(mode="after")
    def validate_runtime_settings(self) -> "Settings":
        if not 1 <= self.page_size <= 100:
            raise ValueError("PAGE_SIZE must be between 1 and 100")
        if not 1 <= self.max_import_urls <= 100:
            raise ValueError("MAX_IMPORT_URLS must be between 1 and 100")
        if not 1 <= self.fetch_concurrency <= 10:
            raise ValueError("FETCH_CONCURRENCY must be between 1 and 10")

        if self.environment == "production":
            placeholders = ("replace-", "change-me", "development-")
            if len(self.db_password) < 16 or self.db_password.startswith(placeholders):
                raise ValueError("DB_PASSWORD must be a strong production secret")
            if len(self.admin_password) < 12 or self.admin_password.startswith(placeholders):
                raise ValueError("ADMIN_PASSWORD must be at least 12 characters")
            if len(self.session_secret) < 32 or self.session_secret.startswith(placeholders):
                raise ValueError("SESSION_SECRET must contain at least 32 random characters")
            if not self.cookie_secure:
                raise ValueError("COOKIE_SECURE must be true in production")
        return self
