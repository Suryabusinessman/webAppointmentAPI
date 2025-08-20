from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    """Notification types following industry standards."""
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SECURITY = "SECURITY"
    SYSTEM = "SYSTEM"
    PROMOTION = "PROMOTION"
    BOOKING = "BOOKING"
    PAYMENT = "PAYMENT"

class NotificationPriority(str, Enum):
    """Notification priority levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class NotificationCreate(BaseModel):
    """Schema for creating a notification."""
    user_id: int = Field(..., description="ID of the user to notify")
    title: str = Field(..., max_length=255, description="Notification title")
    message: str = Field(..., description="Notification message")
    notification_type: NotificationType = Field(default=NotificationType.INFO, description="Type of notification")
    priority: NotificationPriority = Field(default=NotificationPriority.MEDIUM, description="Priority level")
    action_url: Optional[str] = Field(None, description="Optional URL for action button")
    metadata: Optional[str] = Field(None, description="JSON metadata for the notification")  # Keep as metadata for service layer
    is_read: str = Field(default="N", description="Whether the notification has been read (Y/N)")  # Changed from bool to str
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")

class NotificationUpdate(BaseModel):
    """Schema for updating a notification."""
    title: Optional[str] = Field(None, max_length=255, description="Notification title")
    message: Optional[str] = Field(None, description="Notification message")
    notification_type: Optional[NotificationType] = Field(None, description="Type of notification")
    priority: Optional[NotificationPriority] = Field(None, description="Priority level")
    action_url: Optional[str] = Field(None, description="Optional URL for action button")
    action_data: Optional[str] = Field(None, description="JSON action data for the notification")  # Changed from metadata to action_data
    is_read: Optional[str] = Field(None, description="Whether the notification has been read (Y/N)")  # Changed from bool to str

class NotificationResponse(BaseModel):
    """Schema for notification response."""
    notification_id: int = Field(..., description="Unique notification ID")
    user_id: int = Field(..., description="ID of the user")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    notification_type: NotificationType = Field(..., description="Type of notification")
    priority: NotificationPriority = Field(..., description="Priority level")
    action_url: Optional[str] = Field(None, description="Optional URL for action button")
    action_data: Optional[str] = Field(None, description="JSON action data for the notification")  # Changed from metadata to action_data
    is_read: str = Field(..., description="Whether the notification has been read (Y/N)")  # Changed from bool to str
    read_at: Optional[datetime] = Field(None, description="When the notification was read")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True

class NotificationListResponse(BaseModel):
    """Schema for notification list response."""
    notifications: List[NotificationResponse] = Field(..., description="List of notifications")
    total_count: int = Field(..., description="Total number of notifications")
    unread_count: int = Field(..., description="Number of unread notifications")
    has_more: bool = Field(..., description="Whether there are more notifications to load")

class NotificationCountResponse(BaseModel):
    """Schema for notification count response."""
    total_count: int = Field(..., description="Total number of notifications")
    unread_count: int = Field(..., description="Number of unread notifications")
    high_priority_count: int = Field(..., description="Number of high priority notifications")

class NotificationPreferences(BaseModel):
    """Schema for notification preferences."""
    user_id: int = Field(..., description="User ID")
    email_notifications: bool = Field(default=True, description="Enable email notifications")
    push_notifications: bool = Field(default=True, description="Enable push notifications")
    sms_notifications: bool = Field(default=False, description="Enable SMS notifications")
    security_alerts: bool = Field(default=True, description="Enable security alerts")
    promotional_notifications: bool = Field(default=False, description="Enable promotional notifications")
    system_notifications: bool = Field(default=True, description="Enable system notifications")

class NotificationFilter(BaseModel):
    """Schema for notification filtering."""
    notification_type: Optional[NotificationType] = Field(None, description="Filter by notification type")
    priority: Optional[NotificationPriority] = Field(None, description="Filter by priority")
    unread_only: bool = Field(default=False, description="Show only unread notifications")
    limit: int = Field(default=50, ge=1, le=100, description="Number of notifications to return")
    offset: int = Field(default=0, ge=0, description="Number of notifications to skip")

class NotificationBulkAction(BaseModel):
    """Schema for bulk notification actions."""
    notification_ids: List[int] = Field(..., description="List of notification IDs")
    action: str = Field(..., description="Action to perform (mark_read, delete)")

class NotificationTemplate(BaseModel):
    """Schema for notification templates."""
    template_id: str = Field(..., description="Template identifier")
    title_template: str = Field(..., description="Title template with placeholders")
    message_template: str = Field(..., description="Message template with placeholders")
    notification_type: NotificationType = Field(..., description="Default notification type")
    priority: NotificationPriority = Field(..., description="Default priority level")
    action_url_template: Optional[str] = Field(None, description="Action URL template")
    metadata_template: Optional[dict] = Field(None, description="Metadata template")

class NotificationStats(BaseModel):
    """Schema for notification statistics."""
    total_notifications: int = Field(..., description="Total notifications created")
    unread_notifications: int = Field(..., description="Unread notifications")
    notifications_by_type: dict = Field(..., description="Notifications grouped by type")
    notifications_by_priority: dict = Field(..., description="Notifications grouped by priority")
    recent_activity: List[NotificationResponse] = Field(..., description="Recent notifications") 