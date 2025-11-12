"""
Health Check Routes
"""
from fastapi import APIRouter, status
from app.queue.rabbitmq import rabbitmq_connection
import asyncio

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Basic health check endpoint
    """
    return {
        "status": "healthy",
        "service": "api_gateway",
        "version": "1.0.0"
    }

@router.get("/health/detailed", status_code=status.HTTP_200_OK)
async def detailed_health_check():
    """
    Detailed health check with dependency status
    """
    health_status = {
        "status": "healthy",
        "service": "api_gateway",
        "version": "1.0.0",
        "dependencies": {}
    }
    
    # Check RabbitMQ
    try:
        if rabbitmq_connection and not rabbitmq_connection.is_closed:
            health_status["dependencies"]["rabbitmq"] = "healthy"
        else:
            health_status["dependencies"]["rabbitmq"] = "unhealthy"
            health_status["status"] = "degraded"
    except Exception:
        health_status["dependencies"]["rabbitmq"] = "unhealthy"
        health_status["status"] = "degraded"
    
    # Check Redis (add if implemented)
    # Check Database (add if implemented)
    
    return health_status

@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """
    Kubernetes readiness probe
    """
    # Check if service is ready to accept traffic
    if rabbitmq_connection and not rabbitmq_connection.is_closed:
        return {"ready": True}
    return {"ready": False}, 503

@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """
    Kubernetes liveness probe
    """
    return {"alive": True}