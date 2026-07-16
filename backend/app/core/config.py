from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Resume Builder API"
    app_version: str = "1.0.0"
    debug: bool = False

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/resume_builder",
        description="PostgreSQL connection string",
    )
    database_sync_url: Optional[str] = Field(
        default=None,
        description="Synchronous PostgreSQL URL for Alembic",
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection string",
    )

    secret_key: str = Field(
        default="change-me-in-production",
        description="Secret key for JWT and encryption",
    )
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    algorithm: str = "HS256"

    gemini_api_key: Optional[str] = Field(
        default=None,
        description="Google Gemini API key",
    )
    gemini_model: str = "gemini-1.5-pro"
    gemini_max_retries: int = 3
    gemini_request_timeout: int = 60

    storage_backend: str = "local"
    storage_local_path: str = "storage"
    s3_endpoint: Optional[str] = None
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None
    s3_bucket: Optional[str] = None
    s3_region: Optional[str] = None

    max_upload_size_mb: int = 10
    max_template_file_count: int = 50
    max_resume_count: int = 100

    cors_origins: list[str] = ["http://localhost:3000"]
    sentry_dsn: Optional[str] = None
    environment: str = "development"

    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[str] = None

    google_oauth_client_id: Optional[str] = None
    google_oauth_client_secret: Optional[str] = None
    linkedin_oauth_client_id: Optional[str] = None
    linkedin_oauth_client_secret: Optional[str] = None

    rate_limit_per_minute: int = 60
    max_login_attempts: int = 5
    login_lockout_minutes: int = 15

    celery_broker_url: str = Field(
        default="redis://localhost:6379/1",
        description="Celery broker URL",
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/2",
        description="Celery result backend URL",
    )

    log_level: str = "INFO"
    otel_enabled: bool = False
    otel_service_name: str = "resume-builder"
    otel_exporter_otlp_endpoint: Optional[str] = None

    @property
    def sync_database_url(self) -> str:
        if self.database_sync_url:
            return self.database_sync_url
        return self.database_url.replace("+asyncpg", "")


settings = Settings()
