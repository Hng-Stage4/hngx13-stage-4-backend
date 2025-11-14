import httpx
from datetime import datetime
from app.config.settings import settings
from app.utils.logger import logger
from app.models.delivery_status import DeliveryStatus, DeliveryStatusEnum

class StatusUpdater:
    def __init__(self):
        self.gateway_url = settings.API_GATEWAY_URL

    async def update_status(self, status: DeliveryStatus):
        """Send status update to API Gateway asynchronously"""
        try:

            internal_to_gateway = {
                DeliveryStatusEnum.sent: "delivered",
                DeliveryStatusEnum.failed: "failed",
            }

            payload = {
                "notification_id": status.notification_id,
                "status": internal_to_gateway[status.status],
                "timestamp": status.timestamp.isoformat(),
                "error": status.error,
            }

            timestamp = payload.get("timestamp")
            if isinstance(timestamp, datetime):
                payload["timestamp"] = timestamp.isoformat()

            url = f"{self.gateway_url}/api/v1/email/status/"

            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()

            logger.info(
                f"Status update sent: {status.status}",
                extra={
                    "notification_id": status.notification_id,
                    "event": "status_update_sent",
                    "status": status.status,
                },
            )

        except Exception as e:
            logger.error(
                f"Failed to send status update: {str(e)}",
                extra={
                    "notification_id": status.notification_id,
                    "event": "status_update_failed",
                },
            )
