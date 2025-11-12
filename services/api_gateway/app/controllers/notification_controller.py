# ============================================
# api-gateway/app/controllers/notification_controller.py
# ============================================
import uuid
import json
import logging
from app.schemas.notification_schema import NotificationRequest, NotificationResponse, NotificationStatus
from app.services.queue_service import QueueService
from app.services.idempotency_service import IdempotencyService
from app.services.user_service import UserService
from app.services.notification_tracker import NotificationTracker

logger = logging.getLogger(__name__)


class NotificationController:
    def __init__(self):
        self.queue_service = QueueService()
        self.idempotency_service = IdempotencyService()
        self.user_service = UserService()
        self.tracker = NotificationTracker()
    
    async def create_notification(
        self,
        notification: NotificationRequest,
        correlation_id: str
    ) -> NotificationResponse:
        """
        Process and queue notification request
        """
        try:
            # Check idempotency
            if await self.idempotency_service.is_duplicate(notification.request_id):
                logger.warning(f"Duplicate request detected: {notification.request_id}")
                existing = await self.idempotency_service.get_result(notification.request_id)
                return NotificationResponse(**existing)
            
            # Verify user exists and get preferences
            user = await self.user_service.get_user(notification.user_id)
            if not user:
                raise Exception(f"User {notification.user_id} not found")
            
            # Check user preferences
            if not await self.user_service.check_preference(
                notification.user_id,
                notification.notification_type.value
            ):
                logger.info(f"User {notification.user_id} has disabled {notification.notification_type}")
                return NotificationResponse(
                    notification_id=str(uuid.uuid4()),
                    status=NotificationStatus.failed,
                    message=f"User has disabled {notification.notification_type} notifications"
                )
            
            # Generate notification ID
            notification_id = str(uuid.uuid4())
            
            # Prepare message for queue
            message = {
                "notification_id": notification_id,
                "user_id": notification.user_id,
                "template_code": notification.template_code,
                "variables": notification.variables.dict(),
                "priority": notification.priority,
                "metadata": notification.metadata or {},
                "correlation_id": correlation_id,
                "request_id": notification.request_id
            }
            
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
                message="Notification queued successfully"
            )
            
            await self.idempotency_service.store_result(
                notification.request_id,
                response.dict()
            )
            
            logger.info(f"Notification {notification_id} queued to {queue_name}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create notification: {e}")
            raise
    
    async def get_notification_status(self, notification_id: str) -> NotificationResponse:
        """
        Get notification status from tracker
        """
        status_data = await self.tracker.get_status(notification_id)
        
        if not status_data:
            return None
        
        return NotificationResponse(**status_data)