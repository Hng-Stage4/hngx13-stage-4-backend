# ============================================
# api-gateway/app/config/settings.py
# ============================================
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Notification API Gateway"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    GATEWAY_PORT: str | int = os.getenv("GATEWAY_PORT", 8020)
    service_name: str = "api-gateway-service"

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    # RabbitMQ
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_VHOST: str = "/"

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    # User Service
    USER_SERVICE_URL: str = os.getenv("USER_SERVICE_URL", "http://localhost:3001")
    TEMPLATE_SERVICE_URL: str = os.getenv("TEMPLATE_SERVICE_URL", "http://localhost:8003")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100

    # Circuit Breaker
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_TIMEOUT: int = 60

    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
