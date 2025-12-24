import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_title: str = "Tasks API (RabbitMQ)"
    api_version: str = "2.0.0"
    
    # Auth
    default_api_key: str = os.environ.get("API_KEY", "dev-secret-key")
    
    # RabbitMQ
    rabbitmq_url: str = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    queue_requests: str = "api.requests"
    queue_responses: str = "api.responses"
    queue_dlq: str = "api.dlq"
    
    # Idempotency
    idempotency_expire_seconds: int = 3600

settings = Settings()

