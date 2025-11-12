from fastapi import APIRouter, HTTPException
from datetime import datetime
import redis
import psycopg2
from app.config.settings import settings
from app.config.database import engine

router = APIRouter()

@router.get("/health")
async def health_check():
    checks = {
        "database": "healthy",
        "redis": "healthy"
    }

    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
    except Exception:
        checks["database"] = "unhealthy"

    try:
        # Test Redis connection
        redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db
        )
        redis_client.ping()
    except Exception:
        checks["redis"] = "unhealthy"

    status = "healthy"
    if "unhealthy" in checks.values():
        status = "degraded"

    return {
        "status": status,
        "service": settings.service_name,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "checks": checks
    }
