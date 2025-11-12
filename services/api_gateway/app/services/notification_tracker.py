# ============================================
# api-gateway/app/services/notification_tracker.py
# ============================================
import json
import logging
from datetime import datetime
from app.config.redis import redis_manager
from app.schemas.notification_schema import NotificationStatus

logger = logging.getLogger(__name__)

TRACKER_TTL = 604800  # 7 days


class NotificationTracker:
    async def track(self, notification_id: str, status: NotificationStatus):
        """
        Track notification status
        """
        key = f"notification:{notification_id}"
        data = {
            "notification_id": notification_id,
            "status": status.value,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        await redis_manager.set(key, json.dumps(data), ttl=TRACKER_TTL)

    async def update_status(
        self, notification_id: str, status: NotificationStatus, error: str = None
    ):
        """
        Update notification status
        """
        key = f"notification:{notification_id}"
        existing = await redis_manager.get(key)

        if existing:
            data = json.loads(existing)
            data["status"] = status.value
            data["updated_at"] = datetime.utcnow().isoformat()
            if error:
                data["error"] = error

            await redis_manager.set(key, json.dumps(data), ttl=TRACKER_TTL)

    async def get_status(self, notification_id: str) -> dict:
        """
        Get notification status
        """
        key = f"notification:{notification_id}"
        result = await redis_manager.get(key)
        return json.loads(result) if result else None
