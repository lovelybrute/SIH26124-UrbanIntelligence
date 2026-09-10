from __future__ import annotations

import os
from dataclasses import dataclass


def _csv(name: str, default: str) -> list[str]:
    raw = os.getenv(name, default)
    return [value.strip() for value in raw.split(",") if value.strip()]


@dataclass(frozen=True)
class Settings:
    environment: str = os.getenv("APP_ENV", "development")
    cors_origins: tuple[str, ...] = tuple(_csv("CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173"))
    api_write_key: str | None = os.getenv("API_WRITE_KEY") or None
    max_evidence_mb: int = int(os.getenv("MAX_EVIDENCE_MB", "25"))

    @property
    def production(self) -> bool:
        return self.environment.lower() == "production"


settings = Settings()
