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
