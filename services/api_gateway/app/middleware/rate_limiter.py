# ============================================
# api-gateway/app/middleware/rate_limiter.py
# ============================================
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.config.redis import redis_manager
from app.config.settings import settings


class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path.startswith("/api/v1/health"):
            return await call_next(request)

        # Get client identifier (IP or user ID from auth)
        client_id = request.client.host

        # Check rate limit
        if not await self._check_rate_limit(client_id):
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": "Rate limit exceeded",
                    "message": "Too many requests",
                },
            )

        return await call_next(request)

    async def _check_rate_limit(self, client_id: str) -> bool:
        """
        Check if client has exceeded rate limit
        """
        key = f"rate_limit:{client_id}"
        current = await redis_manager.get(key)

        if current is None:
            await redis_manager.set(key, "1", ttl=60)
            return True

        count = int(current)
        if count >= settings.RATE_LIMIT_PER_MINUTE:
            return False

        await redis_manager.client.incr(key)
        return True
