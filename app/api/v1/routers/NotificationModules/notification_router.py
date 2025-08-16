from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.services.NotificationModules.notification_service import NotificationService
from app.schemas.NotificationModules.notification_schemas import (
    NotificationResponse, NotificationListResponse, NotificationCountResponse,
    NotificationFilter, NotificationBulkAction, NotificationPreferences
)
from app.auth.jwt import get_current_user
from app.models.UserModules.users import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])

def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    """Dependency to get notification service."""
    return NotificationService(db)

@router.get("/", response_model=NotificationListResponse)
async def get_notifications(
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
    limit: int = Query(50, ge=1, le=100, description="Number of notifications to return"),
    offset: int = Query(0, ge=0, description="Number of notifications to skip"),
    unread_only: bool = Query(False, description="Show only unread notifications"),
    notification_type: Optional[str] = Query(None, description="Filter by notification type"),
    priority: Optional[str] = Query(None, description="Filter by priority")
):
    """
    Get notifications for the current user with filtering and pagination.
    """
    try:
        notifications = notification_service.get_user_notifications(
            user_id=current_user.user_id,
            limit=limit,
            offset=offset,
            unread_only=unread_only
        )
        
        # Apply additional filters
        if notification_type:
            notifications = [n for n in notifications if n.notification_type == notification_type]
        if priority:
            notifications = [n for n in notifications if n.priority == priority]
        
        # Get counts
        total_count = notification_service.get_notification_count(current_user.user_id, unread_only=False)
        unread_count = notification_service.get_notification_count(current_user.user_id, unread_only=True)
        
        return NotificationListResponse(
            notifications=notifications,
            total_count=total_count,
            unread_count=unread_count,
            has_more=len(notifications) == limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notifications: {str(e)}"
        )

@router.get("/count", response_model=NotificationCountResponse)
async def get_notification_count(
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Get notification counts for the current user.
    """
    try:
        total_count = notification_service.get_notification_count(current_user.user_id, unread_only=False)
        unread_count = notification_service.get_notification_count(current_user.user_id, unread_only=True)
        
        # Get high priority notifications count
        high_priority_notifications = notification_service.get_high_priority_notifications(current_user.user_id)
        high_priority_count = len(high_priority_notifications)
        
        return NotificationCountResponse(
            total_count=total_count,
            unread_count=unread_count,
            high_priority_count=high_priority_count
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notification count: {str(e)}"
        )

@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Get a specific notification by ID.
    """
    try:
        notification = notification_service.get_notification_by_id(notification_id, current_user.user_id)
        return notification
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notification: {str(e)}"
        )

@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Mark a notification as read.
    """
    try:
        notification = notification_service.mark_notification_as_read(notification_id, current_user.user_id)
        return notification
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}"
        )

@router.patch("/mark-all-read")
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Mark all notifications as read for the current user.
    """
    try:
        result = notification_service.mark_all_notifications_as_read(current_user.user_id)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notifications as read: {str(e)}"
        )

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Delete a notification.
    """
    try:
        result = notification_service.delete_notification(notification_id, current_user.user_id)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete notification: {str(e)}"
        )

@router.post("/bulk-action")
async def bulk_notification_action(
    action_data: NotificationBulkAction,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Perform bulk actions on notifications (mark as read, delete).
    """
    try:
        if action_data.action == "mark_read":
            count = 0
            for notification_id in action_data.notification_ids:
                try:
                    notification_service.mark_notification_as_read(notification_id, current_user.user_id)
                    count += 1
                except:
                    continue
            return {"status": "success", "message": f"Marked {count} notifications as read"}
            
        elif action_data.action == "delete":
            count = 0
            for notification_id in action_data.notification_ids:
                try:
                    notification_service.delete_notification(notification_id, current_user.user_id)
                    count += 1
                except:
                    continue
            return {"status": "success", "message": f"Deleted {count} notifications"}
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid action. Supported actions: mark_read, delete"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform bulk action: {str(e)}"
        )

@router.get("/high-priority", response_model=List[NotificationResponse])
async def get_high_priority_notifications(
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
    limit: int = Query(10, ge=1, le=50, description="Number of notifications to return")
):
    """
    Get high priority notifications for the current user.
    """
    try:
        notifications = notification_service.get_high_priority_notifications(current_user.user_id, limit)
        return notifications
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch high priority notifications: {str(e)}"
        )

@router.get("/by-type/{notification_type}", response_model=List[NotificationResponse])
async def get_notifications_by_type(
    notification_type: str,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
    limit: int = Query(20, ge=1, le=100, description="Number of notifications to return")
):
    """
    Get notifications by type for the current user.
    """
    try:
        notifications = notification_service.get_notifications_by_type(
            current_user.user_id, notification_type, limit
        )
        return notifications
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notifications by type: {str(e)}"
        )

@router.get("/unread", response_model=List[NotificationResponse])
async def get_unread_notifications(
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
    limit: int = Query(20, ge=1, le=100, description="Number of notifications to return")
):
    """
    Get unread notifications for the current user.
    """
    try:
        notifications = notification_service.get_user_notifications(
            current_user.user_id, limit=limit, unread_only=True
        )
        return notifications
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch unread notifications: {str(e)}"
        ) 