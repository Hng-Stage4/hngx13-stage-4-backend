# ============================================
# api-gateway/app/services/user_service.py
# ============================================
import httpx
import logging
from app.config.settings import settings
from app.config.redis import redis_manager
import json

logger = logging.getLogger(__name__)

USER_CACHE_TTL = 3600  # 1 hour


class UserService:
    def __init__(self):
        self.base_url = settings.USER_SERVICE_URL

    async def get_user(self, user_id: str) -> dict:
        """
        Get user from User Service with caching
        """
        # Check cache first
        cache_key = f"user:{user_id}"
        cached = await redis_manager.get(cache_key)

        if cached:
            return json.loads(cached)

        # Fetch from service
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/v1/users/{user_id}")
                response.raise_for_status()
                user_data = response.json()

                # Cache result
                await redis_manager.set(
                    cache_key, json.dumps(user_data), ttl=USER_CACHE_TTL
                )

                return user_data
        except Exception as e:
            logger.error(f"Failed to fetch user {user_id}: {e}")
            return None

    async def check_preference(self, user_id: str, notification_type: str) -> bool:
        """
        Check if user has enabled notification type
        """
        user = await self.get_user(user_id)

        if not user:
            return False

        preferences = user.get("data", {}).get("preferences", {})
        return preferences.get(notification_type, True)
