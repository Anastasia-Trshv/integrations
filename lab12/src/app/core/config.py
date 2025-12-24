import os
from pydantic import BaseModel


class Settings(BaseModel):
    api_title: str = "Tasks API"
    api_version: str = "2.0.0"
    api_key_header: str = "X-API-Key"
    default_api_key: str = os.environ.get("API_KEY", "dev-secret-key")
    rate_limit_requests: int = int(os.environ.get("RATE_LIMIT_REQUESTS", "60"))
    rate_limit_window_seconds: int = int(os.environ.get("RATE_LIMIT_WINDOW", "60"))
    idempotency_header: str = "Idempotency-Key"
    internal_token_header: str = "X-Internal-Token"
    internal_token_default: str = os.environ.get("INTERNAL_TOKEN", "dev-internal")


settings = Settings()

