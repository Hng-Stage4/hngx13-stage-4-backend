# ============================================
# api-gateway/app/controllers/health_controller.py
# ============================================
import logging

logger = logging.getLogger(__name__)


class HealthController:
    async def check_health(self):
        """
        Overall health check
        """
        rabbitmq_status = await self._check_rabbitmq()
        redis_status = await self._check_redis()

        is_healthy = True  # Gateway itself is healthy even if dependencies aren't

        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "service": "api-gateway",
            "version": "1.0.0",
            "dependencies": {
                "rabbitmq": "up" if rabbitmq_status else "down",
                "redis": "up" if redis_status else "down",
            },
            "note": "Gateway is operational. Some features may be limited if dependencies are down.",
        }

    async def check_readiness(self):
        """
        Readiness probe
        """
        health = await self.check_health()

        # Gateway is ready even if optional dependencies are down
        return {"ready": True, "details": health}

    async def _check_rabbitmq(self) -> bool:
        """Check RabbitMQ connection"""
        try:
            from app.config.rabbitmq import rabbitmq_manager

            # Ensure we return a bool (some analyzers consider the expression
            # may produce None). Cast explicitly to bool to satisfy type
            # checkers while preserving runtime behavior.
            return bool(
                rabbitmq_manager.connection
                and not rabbitmq_manager.connection.is_closed
            )
        except Exception as e:
            logger.debug(f"RabbitMQ check failed: {e}")
            return False

    async def _check_redis(self) -> bool:
        """Check Redis connection"""
        try:
            from app.config.redis import redis_manager

            if redis_manager.client:
                await redis_manager.client.ping()
                return True
            return False
        except Exception as e:
            logger.debug(f"Redis check failed: {e}")
            return False
