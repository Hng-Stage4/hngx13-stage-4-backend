"""
Notification Routes
Handles notification creation and queuing
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import uuid4

from app.models.notification import (
    NotificationRequest,
    NotificationResponse,
    NotificationListResponse
)
from app.models.response import StandardResponse
from app.dependencies import get_current_active_user
from app.queue.producer import publish_notification
from app.utils.validators import validate_notification_type

router = APIRouter()

@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_notification(
    request: NotificationRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Create and queue a new notification
    """
    # Validate notification type
    if not validate_notification_type(request.notification_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid notification type: {request.notification_type}"
        )
    
    # Generate unique notification ID if not provided
    notification_id = request.request_id or str(uuid4())
    
    # Prepare message
    message = {
        "notification_id": notification_id,
        "notification_type": request.notification_type,
        "user_id": str(request.user_id),
        "template_code": request.template_code,
        "variables": request.variables,
        "priority": request.priority,
        "metadata": request.metadata or {},
        "created_by": current_user.get("sub"),
        "created_at": None  # Will be set by worker
    }
    
    # Publish to queue
    try:
        await publish_notification(request.notification_type, message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue notification: {str(e)}"
        )
    
    return {
        "success": True,
        "message": "Notification queued successfully",
        "data": {
            "notification_id": notification_id,
            "status": "queued",
            "notification_type": request.notification_type,
            "user_id": request.user_id
        }
    }

@router.post("/bulk", response_model=NotificationListResponse)
async def create_bulk_notifications(
    requests: List[NotificationRequest],
    current_user: dict = Depends(get_current_active_user)
):
    """
    Create multiple notifications at once
    """
    if len(requests) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 notifications per bulk request"
        )
    
    results = []
    failed = []
    
    for req in requests:
        try:
            notification_id = req.request_id or str(uuid4())
            message = {
                "notification_id": notification_id,
                "notification_type": req.notification_type,
                "user_id": str(req.user_id),
                "template_code": req.template_code,
                "variables": req.variables,
                "priority": req.priority,
                "metadata": req.metadata or {},
                "created_by": current_user.get("sub")
            }
            
            await publish_notification(req.notification_type, message)
            results.append({
                "notification_id": notification_id,
                "status": "queued"
            })
        except Exception as e:
            failed.append({
                "request_id": req.request_id,
                "error": str(e)
            })
    
    return {
        "success": True,
        "message": f"Queued {len(results)} notifications, {len(failed)} failed",
        "data": results,
        "meta": {
            "total": len(requests),
            "successful": len(results),
            "failed": len(failed),
            "failed_items": failed
        }
    }

@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification_status(
    notification_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get status of a specific notification
    """
    # In production, fetch from status store (Redis/PostgreSQL)
    # For now, return mock data
    return {
        "success": True,
        "message": "Notification status retrieved",
        "data": {
            "notification_id": notification_id,
            "status": "delivered",
            "notification_type": "email",
            "user_id": "mock-user-id"
        }
    }