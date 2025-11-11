# ============================================
# api-gateway/app/config/redis.py
# ============================================
import redis.asyncio as redis
import logging
from typing import Optional
from app.config.settings import settings

logger = logging.getLogger(__name__)


class RedisManager:
    def __init__(self):
        self.client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True
            )
            await self.client.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()
            logger.info("Disconnected from Redis")
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis"""
        return await self.client.get(key)
    
    async def set(self, key: str, value: str, ttl: int = None):
        """Set value in Redis"""
        if ttl:
            await self.client.setex(key, ttl, value)
        else:
            await self.client.set(key, value)
    
    async def delete(self, key: str):
        """Delete key from Redis"""
        await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return await self.client.exists(key)


redis_manager = RedisManager()