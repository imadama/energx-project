"""Centrale configuratie via Pydantic Settings (leest uit .env)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    api_key: str | None = None
    pagespeed_api_key: str | None = None
    gsc_service_account_json: str | None = None
    gsc_site_url: str | None = None

    log_level: str = "INFO"
    request_timeout: int = 30
    user_agent: str = "EnergxAuditBot/1.0 (+https://energx.nl)"


settings = Settings()
