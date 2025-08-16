from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from app.models.common import Notification
from app.schemas.NotificationModules.notification_schemas import NotificationCreate, NotificationUpdate
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import List, Optional
import json

class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_notification(self, notification_data: NotificationCreate) -> Notification:
        """Create a new notification."""
        try:
            notification = Notification(
                user_id=notification_data.user_id,
                title=notification_data.title,
                message=notification_data.message,
                notification_type=notification_data.notification_type,
                priority=notification_data.priority,
                action_url=notification_data.action_url,
                action_data=notification_data.metadata,  # Changed from metadata to action_data
                is_read=notification_data.is_read,
                created_at=notification_data.created_at
            )
            
            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)
            return notification
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create notification: {str(e)}"
            )

    def get_user_notifications(self, user_id: int, limit: int = 50, offset: int = 0, 
                             unread_only: bool = False) -> List[Notification]:
        """Get notifications for a user with pagination and filtering."""
        try:
            query = self.db.query(Notification).filter(Notification.user_id == user_id)
            
            if unread_only:
                query = query.filter(Notification.is_read == "N")  # Changed from False to "N"
            
            notifications = query.order_by(desc(Notification.created_at)).offset(offset).limit(limit).all()
            return notifications
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch notifications: {str(e)}"
            )

    def get_notification_by_id(self, notification_id: int, user_id: int) -> Notification:
        """Get a specific notification by ID for a user."""
        try:
            notification = self.db.query(Notification).filter(
                and_(
                    Notification.notification_id == notification_id,
                    Notification.user_id == user_id
                )
            ).first()
            
            if not notification:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Notification not found"
                )
            
            return notification
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch notification: {str(e)}"
            )

    def mark_as_read(self, notification_id: int, user_id: int) -> Notification:
        """Mark a notification as read."""
        try:
            notification = self.get_notification_by_id(notification_id, user_id)
            notification.is_read = "Y"  # Changed from True to "Y"
            notification.read_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(notification)
            return notification
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to mark notification as read: {str(e)}"
            )

    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user."""
        try:
            count = self.db.query(Notification).filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == "N"  # Changed from False to "N"
                )
            ).update({
                "is_read": "Y",  # Changed from True to "Y"
                "read_at": datetime.utcnow()
            })
            
            self.db.commit()
            return count
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to mark notifications as read: {str(e)}"
            )

    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """Delete a notification."""
        try:
            notification = self.get_notification_by_id(notification_id, user_id)
            self.db.delete(notification)
            self.db.commit()
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete notification: {str(e)}"
            )

    def get_notification_count(self, user_id: int, unread_only: bool = True) -> int:
        """Get notification count for a user."""
        try:
            query = self.db.query(Notification).filter(Notification.user_id == user_id)
            
            if unread_only:
                query = query.filter(Notification.is_read == "N")  # Changed from False to "N"
            
            return query.count()
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get notification count: {str(e)}"
            )

    def get_notifications_by_type(self, user_id: int, notification_type: str, 
                                 limit: int = 20) -> List[Notification]:
        """Get notifications by type for a user."""
        try:
            notifications = self.db.query(Notification).filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.notification_type == notification_type
                )
            ).order_by(desc(Notification.created_at)).limit(limit).all()
            
            return notifications
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch notifications by type: {str(e)}"
            )

    def get_high_priority_notifications(self, user_id: int, limit: int = 10) -> List[Notification]:
        """Get high priority notifications for a user."""
        try:
            notifications = self.db.query(Notification).filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.priority.in_(["HIGH", "URGENT"])
                )
            ).order_by(desc(Notification.created_at)).limit(limit).all()
            
            return notifications
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch high priority notifications: {str(e)}"
            )

    def cleanup_old_notifications(self, days_old: int = 30) -> int:
        """Clean up old notifications (for maintenance)."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            count = self.db.query(Notification).filter(
                and_(
                    Notification.created_at < cutoff_date,
                    Notification.is_read == "Y"  # Changed from True to "Y"
                )
            ).delete()
            
            self.db.commit()
            return count
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to cleanup old notifications: {str(e)}"
            ) 