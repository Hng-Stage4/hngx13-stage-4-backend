# ============================================
# api-gateway/app/routers/status.py
# ============================================
from fastapi import APIRouter, Depends
from app.schemas.notification_schema import StatusUpdateRequest
from app.schemas.response_schema import ApiResponse
from app.controllers.status_controller import StatusController
from app.middleware.auth import get_current_user

router = APIRouter()
controller = StatusController()


@router.post("/{notification_type}/status/", response_model=ApiResponse)
async def update_notification_status(
    notification_type: str,
    status_update: StatusUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Update notification delivery status
    """
    result = await controller.update_status(notification_type, status_update)

    return ApiResponse(
        success=True, data=result, message="Status updated successfully", meta=None
    )
