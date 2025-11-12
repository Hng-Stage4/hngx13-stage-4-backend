from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Service settings
    service_name: str = "template-service"
    version: str = "1.0.0"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8003

    # Database settings
    database_host: str = "localhost"
    database_port: int = 5432
    database_user: str = "postgres"
    database_password: str = "password"
    database_name: str = "template_db"

    # Redis settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # Cache settings
    cache_ttl: int = 3600

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
