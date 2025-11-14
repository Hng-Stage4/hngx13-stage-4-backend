# ============================================
# api-gateway/app/routers/notification.py
# ============================================
from fastapi import APIRouter, HTTPException, Request
from app.schemas.notification_schema import NotificationRequest, NotificationResponse
from app.schemas.response_schema import ApiResponse
from app.controllers.notification_controller import NotificationController
from app.utils.decorators import monitor_endpoint

router = APIRouter()
controller = NotificationController()


@router.post("/notifications/", response_model=ApiResponse[NotificationResponse])
@monitor_endpoint()
async def create_notification(
    request: Request,
    notification: NotificationRequest,
):
    """
    Create and queue a new notification
    """
    correlation_id = request.state.correlation_id
    result = await controller.create_notification(notification, correlation_id)

    return ApiResponse(
        success=True, data=result, message="Notification queued successfully", meta=None
    )


@router.get(
    "/notifications/{notification_id}", response_model=ApiResponse[NotificationResponse]
)
async def get_notification_status(notification_id: str, ):
    """
    Get notification status by ID
    """
    result = await controller.get_notification_status(notification_id)

    if not result:
        raise HTTPException(status_code=404, detail="Notification not found")

    return ApiResponse(
        success=True, data=result, message="Notification status retrieved", meta=None
    )
