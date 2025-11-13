import redis
import json
from typing import Any, Optional
from app.config.settings import settings

class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True
        )

    def get(self, key: str) -> Optional[Any]:
        try:
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        try:
            ttl = ttl or settings.cache_ttl
            data = json.dumps(value, default=str)
            return self.redis_client.set(key, data, ex=ttl)
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        try:
            return self.redis_client.delete(key) > 0
        except Exception:
            return False
