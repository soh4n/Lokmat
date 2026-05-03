"""
LokMat API — Configuration module.

All configuration via pydantic-settings. No raw os.environ outside this file.
Secrets injected at runtime via environment variables (or Secret Manager in production).
"""

import secrets
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file="api/.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "LokMat API"
    app_version: str = "1.0.0"
    debug: bool = False
    testing: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://lokmat-495121.web.app",
        "https://lokmat-495121.firebaseapp.com",
    ]
    allowed_hosts: list[str] = [
        "test",
        "localhost",
        "127.0.0.1",
        "lokmat-495121.web.app",
        "lokmat-495121.firebaseapp.com",
        "*.run.app",
    ]

    # GCP Project
    gcp_project_id: str = "lokmat-495121"

    # Firebase Auth — set to true in production
    firebase_auth_enabled: bool = True

    # Legacy JWT (used when firebase_auth_enabled=false)
    jwt_secret: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 1440  # 24 hours

    # Gemini API
    gemini_api_key: str = ""
    gemini_model_flash: str = "gemini-3.1-flash-lite"
    gemini_model_pro: str = "gemini-2.5-pro"
    gemini_max_output_tokens: int = 1024
    gemini_temperature: float = 0.7

    # Database — Cloud SQL (PostgreSQL)
    database_url: str = "sqlite+aiosqlite:///./lokmat.db"

    # Redis — Memorystore
    redis_url: str = ""

    # Cloud Storage (GCS)
    gcs_bucket: str = ""
    gcs_voter_slip_prefix: str = "voter-slips/"

    # Rate Limiting
    rate_limit_per_minute: int = 60
    inference_rate_limit_per_minute: int = 10

    # Token Budget (per GEMINI.md efficiency rules)
    max_context_tokens: int = 8_000
    warn_threshold_tokens: int = 50_000

    @field_validator("debug", "firebase_auth_enabled", "testing", mode="before")
    @classmethod
    def parse_boolish_environment(cls, value: Any) -> Any:
        """Accept common deployment-mode strings for boolean environment flags."""
        if not isinstance(value, str):
            return value

        normalized = value.strip().lower()
        if normalized in {"release", "prod", "production", "false", "0", "no", "off"}:
            return False
        if normalized in {"debug", "dev", "development", "true", "1", "yes", "on"}:
            return True
        return value

    @property
    def clean_gemini_api_key(self) -> str:
        """Strip trailing newlines often present in Secret Manager payloads."""
        return self.gemini_api_key.strip()


settings = Settings()
