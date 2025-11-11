# ============================================
# api-gateway/app/routers/health.py
# ============================================
from fastapi import APIRouter
from app.controllers.health_controller import HealthController

router = APIRouter()
controller = HealthController()


@router.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return await controller.check_health()


@router.get("/health/ready")
async def readiness_check():
    """
    Readiness check for Kubernetes
    """
    return await controller.check_readiness()


@router.get("/health/live")
async def liveness_check():
    """
    Liveness check for Kubernetes
    """
    return {"status": "alive"}