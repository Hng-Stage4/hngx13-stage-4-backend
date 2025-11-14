from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Service settings
    service_name: str = "template-service"
    version: str = "1.0.0"

    # Server settings
    host: str = "0.0.0.0"
    port: int = int(os.getenv("TEMPLATE_PORT", 8003))

    # Database settings
    database_host: str = os.getenv("DATABASE_HOST", "localhost")
    database_port: int = int(os.getenv("DATABASE_PORT", 5432))
    database_user: str = os.getenv("DATABASE_USER", "admin")
    database_password: str = os.getenv("DATABASE_PASSWORD", "secret")
    database_name: str = os.getenv("DATABASE_NAME", "notifications")

    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", 6379))
    redis_db: int = int(os.getenv("REDIS_DB", 0))

    # Cache settings
    cache_ttl: int = int(os.getenv("CACHE_TTL", 3600))

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
