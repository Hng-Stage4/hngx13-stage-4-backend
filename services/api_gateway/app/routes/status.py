"""
Status Routes
Track notification delivery status
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from datetime import datetime

from app.models.response import StandardResponse, PaginationMeta
from app.dependencies import get_current_active_user

router = APIRouter()

@router.get("/", response_model=StandardResponse)
async def get_notification_statuses(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status_filter: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get list of notification statuses with pagination
    """
    # Mock data - replace with actual database query
    mock_statuses = [
        {
            "notification_id": f"notif-{i}",
            "status": "delivered",
            "notification_type": "email",
            "created_at": datetime.utcnow().isoformat()
        }
        for i in range(limit)
    ]
    
    return {
        "success": True,
        "message": "Notification statuses retrieved",
        "data": mock_statuses,
        "meta": PaginationMeta(
            total=100,
            limit=limit,
            page=page,
            total_pages=10,
            has_next=page < 10,
            has_previous=page > 1
        )
    }