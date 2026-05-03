"""
LokMat API — Configuration module.

All configuration via pydantic-settings. No raw os.environ outside this file.
Secrets injected at runtime via environment variables (or Secret Manager in production).
"""

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

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://lokmat-495121.web.app",
        "https://lokmat-495121.firebaseapp.com"
    ]

    # GCP Project
    gcp_project_id: str = "lokmat-495121"

    # Firebase Auth — set to true in production
    firebase_auth_enabled: bool = True

    # Legacy JWT (used when firebase_auth_enabled=false)
    jwt_secret: str = "lokmat-dev-secret-change-in-production"
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

    @property
    def clean_gemini_api_key(self) -> str:
        """Strip trailing newlines often present in Secret Manager payloads."""
        return self.gemini_api_key.strip()


settings = Settings()
