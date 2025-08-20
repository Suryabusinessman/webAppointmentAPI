from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
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
from app.core.config import config

router = APIRouter(prefix="/notifications", tags=["Notifications"])

def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    """Dependency to get notification service."""
    return NotificationService(db)

def verify_secret_key(secret_key: str = Header(None)):
    """Verify secret key for public endpoints."""
    if not secret_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Secret key required"
        )
    
    # Get the secret key from config
    config_secret_key = getattr(config, 'SECRET_KEY', None)
    if not config_secret_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error"
        )
    
    # Verify the secret key matches the config secret key
    if secret_key != config_secret_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid secret key"
        )
    
    return secret_key

@router.get("/", response_model=NotificationListResponse)
async def get_notifications(
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Get notifications for the current user with filtering and pagination.
    """
    try:
        notifications = notification_service.get_user_notifications(
            user_id=current_user.user_id,
            limit=50,  # Fixed limit for simplicity
            offset=0,  # Fixed offset for simplicity
            unread_only=False  # Get all notifications
        )
        
        # Convert SQLAlchemy models to response dictionaries
        notification_responses = [
            notification_service._convert_to_response_model(n) for n in notifications
        ]
        
        # Get counts
        total_count = notification_service.get_notification_count(current_user.user_id, unread_only=False)
        unread_count = notification_service.get_notification_count(current_user.user_id, unread_only=True)
        
        return NotificationListResponse(
            notifications=notification_responses,
            total_count=total_count,
            unread_count=unread_count,
            has_more=len(notifications) == 50  # Fixed limit value
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

# New endpoint to get notifications by user ID (requires secret key)
@router.get("/user/{user_id}", response_model=NotificationListResponse)
async def get_notifications_by_user_id(
    user_id: int,
    notification_service: NotificationService = Depends(get_notification_service),
    secret_key: str = Depends(verify_secret_key)
):
    """
    Get notifications for a specific user by user ID (no authentication required).
    This endpoint is useful for admin purposes or when you need to fetch notifications for any user.
    """
    try:
        notifications = notification_service.get_user_notifications(
            user_id=user_id,
            limit=50,  # Fixed limit for simplicity
            offset=0,  # Fixed offset for simplicity
            unread_only=False  # Get all notifications
        )
        
        # Convert SQLAlchemy models to response dictionaries
        notification_responses = [
            notification_service._convert_to_response_model(n) for n in notifications
        ]
        
        # Get counts
        total_count = notification_service.get_notification_count(user_id, unread_only=False)
        unread_count = notification_service.get_notification_count(user_id, unread_only=True)
        
        return NotificationListResponse(
            notifications=notification_responses,
            total_count=total_count,
            unread_count=unread_count,
            has_more=len(notifications) == 50  # Fixed limit value
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notifications: {str(e)}"
        )

# New endpoint to get notification count by user ID (requires secret key)
@router.get("/user/{user_id}/count", response_model=NotificationCountResponse)
async def get_notification_count_by_user_id(
    user_id: int,
    notification_service: NotificationService = Depends(get_notification_service),
    secret_key: str = Depends(verify_secret_key)
):
    """
    Get notification counts for a specific user by user ID (no authentication required).
    This endpoint is useful for admin purposes or when you need to fetch notification counts for any user.
    """
    try:
        total_count = notification_service.get_notification_count(user_id, unread_only=False)
        unread_count = notification_service.get_notification_count(user_id, unread_only=True)
        
        # Get high priority notifications count
        high_priority_notifications = notification_service.get_high_priority_notifications(user_id)
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

# New endpoint to get unread notifications by user ID (requires secret key)
@router.get("/user/{user_id}/unread", response_model=List[NotificationResponse])
async def get_unread_notifications_by_user_id(
    user_id: int,
    notification_service: NotificationService = Depends(get_notification_service),
    secret_key: str = Depends(verify_secret_key)
):
    """
    Get unread notifications for a specific user by user ID (no authentication required).
    This endpoint is useful for admin purposes or when you need to fetch unread notifications for any user.
    """
    try:
        notifications = notification_service.get_user_notifications(
            user_id=user_id, limit=20, unread_only=True  # Fixed limit for simplicity
        )
        # Convert SQLAlchemy models to response dictionaries
        notification_responses = [
            notification_service._convert_to_response_model(n) for n in notifications
        ]
        return notification_responses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch unread notifications: {str(e)}"
        )

# New endpoint to get high priority notifications by user ID (requires secret key)
@router.get("/user/{user_id}/high-priority", response_model=List[NotificationResponse])
async def get_high_priority_notifications_by_user_id(
    user_id: int,
    notification_service: NotificationService = Depends(get_notification_service),
    secret_key: str = Depends(verify_secret_key)
):
    """
    Get high priority notifications for a specific user by user ID (no authentication required).
    This endpoint is useful for admin purposes or when you need to fetch high priority notifications for any user.
    """
    try:
        notifications = notification_service.get_high_priority_notifications(user_id, 10)  # Fixed limit for simplicity
        # Convert SQLAlchemy models to response dictionaries
        notification_responses = [
            notification_service._convert_to_response_model(n) for n in notifications
        ]
        return notification_responses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch high priority notifications: {str(e)}"
        )

# New endpoint to get notifications by type for a specific user ID (requires secret key)
@router.get("/user/{user_id}/by-type/{notification_type}", response_model=List[NotificationResponse])
async def get_notifications_by_type_for_user_id(
    user_id: int,
    notification_type: str,
    notification_service: NotificationService = Depends(get_notification_service),
    secret_key: str = Depends(verify_secret_key)
):
    """
    Get notifications by type for a specific user by user ID (no authentication required).
    This endpoint is useful for admin purposes or when you need to fetch notifications by type for any user.
    """
    try:
        notifications = notification_service.get_notifications_by_type(
            user_id, notification_type, 20  # Fixed limit for simplicity
        )
        # Convert SQLAlchemy models to response dictionaries
        notification_responses = [
            notification_service._convert_to_response_model(n) for n in notifications
        ]
        return notification_responses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notifications by type: {str(e)}"
        )

# New endpoint to mark notification as read by user ID (requires secret key)
@router.patch("/user/{user_id}/notification/{notification_id}/read", response_model=dict)
async def mark_notification_as_read_by_user_id(
    user_id: int,
    notification_id: int,
    notification_service: NotificationService = Depends(get_notification_service),
    secret_key: str = Depends(verify_secret_key)
):
    """
    Mark a specific notification as read for a specific user by user ID (no authentication required).
    This endpoint is useful for admin purposes or when you need to mark notifications as read for any user.
    """
    try:
        notification = notification_service.mark_notification_as_read(notification_id, user_id)
        # Convert SQLAlchemy model to response dictionary
        return notification_service._convert_to_response_model(notification)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}"
        )

# New endpoint to mark all notifications as read by user ID (requires secret key)
@router.patch("/user/{user_id}/mark-all-read", response_model=dict)
async def mark_all_notifications_as_read_by_user_id(
    user_id: int,
    notification_service: NotificationService = Depends(get_notification_service),
    secret_key: str = Depends(verify_secret_key)
):
    """
    Mark all notifications as read for a specific user by user ID (no authentication required).
    This endpoint is useful for admin purposes or when you need to mark all notifications as read for any user.
    """
    try:
        result = notification_service.mark_all_notifications_as_read(user_id)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notifications as read: {str(e)}"
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
        # Convert SQLAlchemy model to response dictionary
        return notification_service._convert_to_response_model(notification)
        
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
        # Convert SQLAlchemy model to response dictionary
        return notification_service._convert_to_response_model(notification)
        
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
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Get high priority notifications for the current user.
    """
    try:
        notifications = notification_service.get_high_priority_notifications(current_user.user_id, 10)  # Fixed limit for simplicity
        # Convert SQLAlchemy models to response dictionaries
        notification_responses = [
            notification_service._convert_to_response_model(n) for n in notifications
        ]
        return notification_responses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch high priority notifications: {str(e)}"
        )

@router.get("/by-type/{notification_type}", response_model=List[NotificationResponse])
async def get_notifications_by_type(
    notification_type: str,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Get notifications by type for the current user.
    """
    try:
        notifications = notification_service.get_notifications_by_type(
            current_user.user_id, notification_type, 20  # Fixed limit for simplicity
        )
        # Convert SQLAlchemy models to response dictionaries
        notification_responses = [
            notification_service._convert_to_response_model(n) for n in notifications
        ]
        return notification_responses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notifications by type: {str(e)}"
        )

@router.get("/unread", response_model=List[NotificationResponse])
async def get_unread_notifications(
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Get unread notifications for the current user.
    """
    try:
        notifications = notification_service.get_user_notifications(
            current_user.user_id, limit=20, unread_only=True  # Fixed limit for simplicity
        )
        # Convert SQLAlchemy models to response dictionaries
        notification_responses = [
            notification_service._convert_to_response_model(n) for n in notifications
        ]
        return notification_responses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch unread notifications: {str(e)}"
        ) 

# ============================================================================
# ADDITIONAL PUBLIC ENDPOINTS FOR ADMIN PURPOSES (No Authentication Required)
# ============================================================================

# New endpoint to delete notification by user ID (requires secret key)
@router.delete("/user/{user_id}/notification/{notification_id}", response_model=dict)
async def delete_notification_by_user_id(
    user_id: int,
    notification_id: int,
    notification_service: NotificationService = Depends(get_notification_service),
    secret_key: str = Depends(verify_secret_key)
):
    """
    Delete a specific notification for a specific user by user ID (no authentication required).
    This endpoint is useful for admin purposes or when you need to delete notifications for any user.
    """
    try:
        result = notification_service.delete_notification(notification_id, user_id)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete notification: {str(e)}"
        )

# New endpoint to get specific notification by user ID (requires secret key)
@router.get("/user/{user_id}/notification/{notification_id}", response_model=dict)
async def get_notification_by_user_id(
    user_id: int,
    notification_id: int,
    notification_service: NotificationService = Depends(get_notification_service),
    secret_key: str = Depends(verify_secret_key)
):
    """
    Get a specific notification for a specific user by user ID (no authentication required).
    This endpoint is useful for admin purposes or when you need to fetch a specific notification for any user.
    """
    try:
        notification = notification_service.get_notification_by_id(notification_id, user_id)
        # Convert SQLAlchemy model to response dictionary
        return notification_service._convert_to_response_model(notification)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notification: {str(e)}"
        ) 