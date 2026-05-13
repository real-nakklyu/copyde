from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Copyde"
    environment: Literal["local", "staging", "production"] = "local"
    supabase_url: AnyHttpUrl | None = Field(default=None, alias="SUPABASE_URL")
    supabase_service_role_key: str | None = Field(default=None, alias="SUPABASE_SERVICE_ROLE_KEY")
    supabase_jwt_secret: str | None = Field(default=None, alias="SUPABASE_JWT_SECRET")
    supabase_jwks_url: AnyHttpUrl | None = Field(default=None, alias="SUPABASE_JWKS_URL")
    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    redis_url: str | None = Field(default=None, alias="REDIS_URL")
    encryption_master_key: str | None = Field(default=None, alias="ENCRYPTION_MASTER_KEY")
    jwt_audience: str = Field(default="authenticated", alias="JWT_AUDIENCE")
    binance_env: Literal["testnet", "production"] = Field(default="testnet", alias="BINANCE_ENV")
    disable_live_trading: bool = Field(default=True, alias="DISABLE_LIVE_TRADING")
    enable_production_trading: bool = Field(default=False, alias="ENABLE_PRODUCTION_TRADING")
    allowed_origins: str = Field(default="http://localhost:3000", alias="ALLOWED_ORIGINS")
    admin_emails: str = Field(default="", alias="ADMIN_EMAILS")
    rate_limit_per_minute: int = Field(default=120, alias="RATE_LIMIT_PER_MINUTE")

    @field_validator("encryption_master_key")
    @classmethod
    def allow_missing_only_for_bootstrap(cls, value: str | None) -> str | None:
        if value == "":
            return None
        return value

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def admins(self) -> set[str]:
        return {email.strip().lower() for email in self.admin_emails.split(",") if email.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()

