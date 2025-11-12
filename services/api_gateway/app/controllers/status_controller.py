# ============================================
# api-gateway/app/controllers/status_controller.py
# ============================================
import logging
from app.schemas.notification_schema import StatusUpdateRequest
from app.services.notification_tracker import NotificationTracker

logger = logging.getLogger(__name__)


class StatusController:
    def __init__(self):
        self.tracker = NotificationTracker()

    async def update_status(
        self, notification_type: str, status_update: StatusUpdateRequest
    ):
        """
        Update notification delivery status
        """
        try:
            await self.tracker.update_status(
                status_update.notification_id, status_update.status, status_update.error
            )

            logger.info(
                f"Status updated for {status_update.notification_id}: {status_update.status}"
            )

            return {"updated": True}

        except Exception as e:
            logger.error(f"Failed to update status: {e}")
            raise
