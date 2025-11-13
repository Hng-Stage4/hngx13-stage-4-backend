from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Service settings
    service_name: str = "email-service"
    version: str = "1.0.0"

    # Server settings
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", 8001))

    # RabbitMQ settings
    rabbitmq_host: str = os.getenv("RABBITMQ_HOST", "localhost")
    rabbitmq_port: int = int(os.getenv("RABBITMQ_PORT", 5672))
    rabbitmq_user: str = os.getenv("RABBITMQ_USER", "guest")
    rabbitmq_password: str = os.getenv("RABBITMQ_PASSWORD", "guest")
    rabbitmq_vhost: str = os.getenv("RABBITMQ_VHOST", "/")

    # Redis settings
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", 6379))
    redis_db: int = int(os.getenv("REDIS_DB", 0))

    # SMTP settings
    smtp_host: Optional[str] = os.getenv("SMTP_HOST")
    smtp_port: int = int(os.getenv("SMTP_PORT", 587))
    smtp_user: Optional[str] = os.getenv("SMTP_USER")
    smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

    # Email providers
    sendgrid_api_key: Optional[str] = os.getenv("SENDGRID_API_KEY")
    mailgun_api_key: Optional[str] = os.getenv("MAILGUN_API_KEY")
    mailgun_domain: Optional[str] = os.getenv("MAILGUN_DOMAIN")
    gmail_client_id: Optional[str] = os.getenv("GMAIL_CLIENT_ID")
    gmail_client_secret: Optional[str] = os.getenv("GMAIL_CLIENT_SECRET")
    gmail_refresh_token: Optional[str] = os.getenv("GMAIL_REFRESH_TOKEN")
    zoho_api_key: Optional[str] = os.getenv("ZOHO_API_KEY")

    # Template service
    template_service_url: str = os.getenv("TEMPLATE_SERVICE_URL", "http://template-service:8003")

    # Circuit breaker
    circuit_breaker_failure_threshold: int = int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", 5))
    circuit_breaker_recovery_timeout: int = int(os.getenv("CIRCUIT_BREAKER_RECOVERY_TIMEOUT", 60))

    # Retry settings
    max_retries: int = int(os.getenv("MAX_RETRIES", 3))
    retry_delay: int = int(os.getenv("RETRY_DELAY", 5))

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
