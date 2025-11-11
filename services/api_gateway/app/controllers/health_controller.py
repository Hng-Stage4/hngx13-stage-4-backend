# ============================================
# api-gateway/app/controllers/health_controller.py
# ============================================
import logging
from app.config.rabbitmq import rabbitmq_manager
from app.config.redis import redis_manager

logger = logging.getLogger(__name__)


class HealthController:
    async def check_health(self):
        """
        Overall health check
        """
        rabbitmq_status = await self._check_rabbitmq()
        redis_status = await self._check_redis()
        
        is_healthy = rabbitmq_status and redis_status
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "service": "api-gateway",
            "dependencies": {
                "rabbitmq": "up" if rabbitmq_status else "down",
                "redis": "up" if redis_status else "down"
            }
        }
    
    async def check_readiness(self):
        """
        Readiness probe
        """
        health = await self.check_health()
        
        if health["status"] != "healthy":
            return {"ready": False, "details": health}
        
        return {"ready": True}
    
    async def _check_rabbitmq(self) -> bool:
        """Check RabbitMQ connection"""
        try:
            return rabbitmq_manager.connection and not rabbitmq_manager.connection.is_closed
        except:
            return False
    
    async def _check_redis(self) -> bool:
        """Check Redis connection"""
        try:
            await redis_manager.client.ping()
            return True
        except:
            return False