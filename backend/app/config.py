import os
from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./paywall.db")
    webhook_secret: str = os.getenv("MOCK_WEBHOOK_SECRET", "local-demo-secret")

settings = Settings()

def utc_now() -> datetime:
    return datetime.now(UTC)

