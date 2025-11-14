import uuid
import json
import logging
from datetime import datetime

from fastapi.encoders import jsonable_encoder
from app.schemas.notification_schema import (
    NotificationRequest,
    NotificationResponse,
    NotificationStatus,
)
from app.services.queue_service import QueueService
from app.services.idempotency_service import IdempotencyService
from app.services.user_service import UserService
from app.services.template_service import TemplateService
from app.services.notification_tracker import NotificationTracker

from app.utils.logger import logger


class NotificationController:
    def __init__(self):
        self.queue_service = QueueService()
        self.idempotency_service = IdempotencyService()
        self.user_service = UserService()
        self.template_service = TemplateService()
        self.tracker = NotificationTracker()

    async def create_notification(
        self, notification: NotificationRequest, correlation_id: str
    ) -> NotificationResponse:
        """
        Process and queue notification request
        """
        try:
            # Check idempotency
            if await self.idempotency_service.is_duplicate(notification.request_id):
                logger.warning(f"Duplicate request detected: {notification.request_id}")
                existing = await self.idempotency_service.get_result(
                    notification.request_id
                )
                return NotificationResponse(**existing)

            # Fetch user
            user = await self.user_service.get_user(notification.user_id)
            logger.debug(f"Fetched user data for {notification.user_id}: {user}")

            if not user:
                raise Exception(f"User {notification.user_id} not found")

            logger.info(f"User {notification.user_id} found: {user}")
            print(f"User data: {user}")  # You already have this

            # Extract user_data
            user_data = user.get("data", {})
            logger.info(f"Extracted user_data: {user_data}")
            logger.info(f"Push token from user_data: {user_data.get('push_token')}")

            # Check user preferences
            if not await self.user_service.check_preference(
                notification.user_id, notification.notification_type.value
            ):
                logger.info(
                    f"User {notification.user_id} has disabled {notification.notification_type} notifications"
                )
                return NotificationResponse(
                    notification_id=str(uuid.uuid4()),
                    status=NotificationStatus.failed,
                    message=f"User has disabled {notification.notification_type} notifications",
                )
            logger.info(f"User {notification.user_id} preferences allow {notification.notification_type} notifications")

            # Fetch template
            template = await self.template_service.get_template(notification.template_code)
            if not template:
                logger.error(f"Template {notification.template_code} not found")
                raise Exception(f"Template {notification.template_code} not found")

            logger.info(f"Template {notification.template_code} fetched successfully")

            notification_id = str(uuid.uuid4())
            user_data = user

            # Build canonical message for queue
            message = {
                "notification_id": notification_id,
                "notification_type": notification.notification_type.value,
                "user_id": notification.user_id,
                "template_code": notification.template_code,
                "template": template.get("data"),
                "variables": notification.variables.dict(),
                "delivery": {
                    "email": user_data.get("email"),
                    "push_token": user_data.get("push_token")
                },
                "priority": notification.priority,
                "metadata": notification.metadata or {},
                "request_id": notification.request_id,
                "correlation_id": correlation_id,
                "timestamp": datetime.utcnow().isoformat()
            }

            # Log the delivery object
            logger.info(f"Delivery object: {message['delivery']}")
            logger.info(f"Push token present: {bool(message['delivery']['push_token'])}")

            # Determine queue based on notification type
            queue_name = f"{notification.notification_type.value}.queue"

            # Publish to queue
            await self.queue_service.publish(queue_name, message)

            # Track notification
            await self.tracker.track(notification_id, NotificationStatus.pending)

            # Store result for idempotency
            response = NotificationResponse(
                notification_id=notification_id,
                status=NotificationStatus.pending,
                message="Notification queued successfully",
            )
            await self.idempotency_service.store_result(
                notification.request_id, response.dict()
            )

            logger.info(f"Notification {notification_id} queued to {queue_name}")
            return response

        except Exception as e:
            logger.error(f"Failed to create notification: {e}")
            raise

    async def get_notification_status(
        self, notification_id: str
    ) -> NotificationResponse:
        """
        Get notification status from tracker
        """
        status_data = await self.tracker.get_status(notification_id)
        if not status_data:
            return None
        return NotificationResponse(**status_data)
