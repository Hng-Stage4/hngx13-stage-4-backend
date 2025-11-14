# ============================================
# api-gateway/app/services/queue_service.py
# ============================================
import json
import logging
from app.config.rabbitmq import rabbitmq_manager
from app.services.circuit_breaker import CircuitBreaker
from fastapi.encoders import jsonable_encoder  # Add this import

from app.utils.logger import logger


class QueueService:
    def __init__(self):
        self.circuit_breaker = CircuitBreaker()

    async def publish(self, queue_name: str, message: dict):
        """
        Publish message to RabbitMQ queue with circuit breaker
        """

        async def _publish():
            # Convert Pydantic models and special types to JSON-serializable dict
            serializable_message = jsonable_encoder(message)
            # Pass dict directly - let publish_message handle json.dumps
            await rabbitmq_manager.publish_message(queue_name, serializable_message)

        try:
            await self.circuit_breaker.call(_publish)
        except Exception as e:
            logger.error(f"Failed to publish to {queue_name}: {e}")
            # Move to failed queue
            await self._handle_failed_publish(message, str(e))
            raise

    async def _handle_failed_publish(self, message: dict, error: str):
        """
        Handle failed message publication
        """
        try:
            failed_message = {
                **jsonable_encoder(message),  # Convert to serializable
                "error": error,
                "original_queue": message.get("notification_type", "unknown"),
            }
            await rabbitmq_manager.publish_message("failed.queue", failed_message)
        except Exception as e:
            logger.critical(f"Failed to publish to dead letter queue: {e}")