from dataclasses import dataclass, field
from functools import lru_cache
import os
from typing import List


def _parse_csv(value: str | None) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_name: str = "AI Meeting Agent API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:Ashish19@localhost:5432/AI_Meeting_Flow",
        )
    )
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    secret_key: str = field(default_factory=lambda: os.getenv("SECRET_KEY", "change-me-in-production"))
    jwt_algorithm: str = field(default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256"))
    access_token_expire_minutes: int = field(
        default_factory=lambda: int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    )
    refresh_token_expire_days: int = field(
        default_factory=lambda: int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    )
    email_token_expire_minutes: int = field(
        default_factory=lambda: int(os.getenv("EMAIL_TOKEN_EXPIRE_MINUTES", "60"))
    )
    password_reset_token_expire_minutes: int = field(
        default_factory=lambda: int(os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_MINUTES", "30"))
    )
    uploads_root: str = field(default_factory=lambda: os.getenv("UPLOADS_ROOT", "uploads"))
    storage_backend: str = field(default_factory=lambda: os.getenv("STORAGE_BACKEND", "local"))
    aws_bucket_name: str | None = field(default_factory=lambda: os.getenv("AWS_BUCKET_NAME"))
    aws_region: str = field(default_factory=lambda: os.getenv("AWS_REGION", "us-east-1"))
    aws_s3_prefix: str = field(default_factory=lambda: os.getenv("AWS_S3_PREFIX", "meetings"))
    max_upload_size_mb: int = field(default_factory=lambda: int(os.getenv("MAX_UPLOAD_SIZE_MB", "100")))
    max_meeting_duration_minutes: int = field(
        default_factory=lambda: int(os.getenv("MAX_MEETING_DURATION_MINUTES", "480"))
    )
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    cors_origins: List[str] = field(
        default_factory=lambda: _parse_csv(
            os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
        )
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
