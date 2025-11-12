# ============================================
# api-gateway/app/services/idempotency_service.py
# ============================================
import json
import logging
from app.config.redis import redis_manager

logger = logging.getLogger(__name__)

IDEMPOTENCY_TTL = 86400  # 24 hours


class IdempotencyService:
    async def is_duplicate(self, request_id: str) -> bool:
        """
        Check if request ID has been processed
        """
        key = f"idempotency:{request_id}"
        return await redis_manager.exists(key)

    async def store_result(self, request_id: str, result: dict):
        """
        Store request result for idempotency
        """
        key = f"idempotency:{request_id}"
        await redis_manager.set(key, json.dumps(result), ttl=IDEMPOTENCY_TTL)
        logger.info(f"Stored idempotency key: {request_id}")

    async def get_result(self, request_id: str) -> dict:
        """
        Get cached result for duplicate request
        """
        key = f"idempotency:{request_id}"
        result = await redis_manager.get(key)
        return json.loads(result) if result else None
