from sqlalchemy.orm import Session
from app.repositories.NotificationModules.notification_repository import NotificationRepository
from app.models.common import Notification
from app.schemas.NotificationModules.notification_schemas import NotificationCreate, NotificationUpdate
from fastapi import HTTPException, status
from datetime import datetime
from typing import List, Optional
import json

class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_repo = NotificationRepository(db)

    def create_notification(self, user_id: int, title: str, message: str, 
                          notification_type: str = "INFO", priority: str = "MEDIUM",
                          action_url: str = None, metadata: dict = None) -> Notification:
        """
        Create a notification following standard patterns.
        
        Args:
            user_id: ID of the user to notify
            title: Notification title
            message: Notification message
            notification_type: Type of notification (INFO, SUCCESS, WARNING, ERROR, SECURITY)
            priority: Priority level (LOW, MEDIUM, HIGH, URGENT)
            action_url: Optional URL for action button
            metadata: Optional metadata for the notification
        """
        try:
            notification_data = NotificationCreate(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority,
                action_url=action_url,
                metadata=json.dumps(metadata) if metadata else None,
                is_read="N",  # Changed from False to "N"
                created_at=datetime.utcnow()
            )
            
            notification = self.notification_repo.create_notification(notification_data)
            return notification
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create notification: {str(e)}"
            )

    def create_registration_notification(self, user_id: int, user_email: str, user_name: str) -> Notification:
        """Create a welcome notification for new user registration."""
        title = "Welcome to AppointmentTech! 🎉"
        message = f"Hi {user_name}, your account has been successfully created. Welcome to our platform! You can now start exploring our services."
        
        metadata = {
            "event_type": "USER_REGISTRATION",
            "user_email": user_email,
            "registration_date": datetime.utcnow().isoformat(),
            "welcome_message": True
        }
        
        return self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="SUCCESS",
            priority="MEDIUM",
            action_url="/dashboard",
            metadata=metadata
        )

    def create_login_notification(self, user_id: int, user_email: str, user_name: str, 
                                ip_address: str, device_info: str, is_suspicious: bool = False) -> Notification:
        """Create a login notification with security awareness."""
        if is_suspicious:
            title = "🔒 Suspicious Login Detected"
            message = f"Hi {user_name}, we detected a login from an unrecognized device. If this wasn't you, please secure your account immediately."
            notification_type = "SECURITY"
            priority = "HIGH"
        else:
            title = "✅ Successful Login"
            message = f"Hi {user_name}, you have successfully logged into your account."
            notification_type = "INFO"
            priority = "LOW"
        
        metadata = {
            "event_type": "USER_LOGIN",
            "user_email": user_email,
            "ip_address": ip_address,
            "device_info": device_info,
            "login_timestamp": datetime.utcnow().isoformat(),
            "is_suspicious": is_suspicious
        }
        
        return self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            action_url="/account/security" if is_suspicious else None,
            metadata=metadata
        )

    def create_password_change_notification(self, user_id: int, user_email: str, user_name: str) -> Notification:
        """Create a password change confirmation notification."""
        title = "🔐 Password Changed Successfully"
        message = f"Hi {user_name}, your password has been successfully changed. If you didn't make this change, please contact support immediately."
        
        metadata = {
            "event_type": "PASSWORD_CHANGE",
            "user_email": user_email,
            "change_timestamp": datetime.utcnow().isoformat(),
            "security_alert": True
        }
        
        return self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="SECURITY",
            priority="HIGH",
            action_url="/account/security",
            metadata=metadata
        )

    def create_account_locked_notification(self, user_id: int, user_email: str, user_name: str, 
                                         reason: str, unlock_time: datetime) -> Notification:
        """Create an account locked notification."""
        title = "🚫 Account Temporarily Locked"
        message = f"Hi {user_name}, your account has been temporarily locked due to {reason}. It will be unlocked at {unlock_time.strftime('%Y-%m-%d %H:%M:%S')}."
        
        metadata = {
            "event_type": "ACCOUNT_LOCKED",
            "user_email": user_email,
            "lock_reason": reason,
            "unlock_time": unlock_time.isoformat(),
            "security_alert": True
        }
        
        return self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="SECURITY",
            priority="URGENT",
            action_url="/account/unlock",
            metadata=metadata
        )

    def create_business_registration_notification(self, user_id: int, user_email: str, user_name: str, 
                                                business_name: str) -> Notification:
        """Create a business registration notification."""
        title = "🏢 Business Account Created"
        message = f"Hi {user_name}, your business account '{business_name}' has been successfully created. You can now start managing your business services."
        
        metadata = {
            "event_type": "BUSINESS_REGISTRATION",
            "user_email": user_email,
            "business_name": business_name,
            "registration_timestamp": datetime.utcnow().isoformat()
        }
        
        return self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="SUCCESS",
            priority="MEDIUM",
            action_url="/business/dashboard",
            metadata=metadata
        )

    def get_user_notifications(self, user_id: int, limit: int = 50, offset: int = 0, 
                             unread_only: bool = False) -> List[Notification]:
        """Get notifications for a user with pagination and filtering."""
        try:
            notifications = self.notification_repo.get_user_notifications(
                user_id=user_id,
                limit=limit,
                offset=offset,
                unread_only=unread_only
            )
            return notifications
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch notifications: {str(e)}"
            )

    def mark_notification_as_read(self, notification_id: int, user_id: int) -> Notification:
        """Mark a notification as read."""
        try:
            notification = self.notification_repo.mark_as_read(notification_id, user_id)
            return notification
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to mark notification as read: {str(e)}"
            )

    def mark_all_notifications_as_read(self, user_id: int) -> dict:
        """Mark all notifications as read for a user."""
        try:
            count = self.notification_repo.mark_all_as_read(user_id)
            return {"status": "success", "message": f"Marked {count} notifications as read"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to mark notifications as read: {str(e)}"
            )

    def delete_notification(self, notification_id: int, user_id: int) -> dict:
        """Delete a notification."""
        try:
            self.notification_repo.delete_notification(notification_id, user_id)
            return {"status": "success", "message": "Notification deleted successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete notification: {str(e)}"
            )

    def get_notification_count(self, user_id: int, unread_only: bool = True) -> int:
        """Get notification count for a user."""
        try:
            return self.notification_repo.get_notification_count(user_id, unread_only)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get notification count: {str(e)}"
            ) 