from fastapi import APIRouter, HTTPException
from datetime import datetime
import redis
import pika
from app.config.settings import settings
from app.config.redis import get_redis_client
from app.config.rabbitmq import get_rabbitmq_connection

router = APIRouter()

@router.get("/health")
async def health_check():
    checks = {
        "database": "healthy",  # Email service doesn't have its own DB
        "redis": "healthy",
        "rabbitmq": "healthy"
    }

    try:
        redis_client = get_redis_client()
        redis_client.ping()
    except Exception:
        checks["redis"] = "unhealthy"

    try:
        connection = get_rabbitmq_connection()
        connection.close()
    except Exception:
        checks["rabbitmq"] = "unhealthy"

    status = "healthy"
    if "unhealthy" in checks.values():
        status = "degraded"

    return {
        "status": status,
        "service": settings.service_name,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "checks": checks
    }
