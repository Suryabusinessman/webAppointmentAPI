from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Generic, TypeVar
from datetime import datetime
from enum import Enum

# Generic type for data
T = TypeVar('T')

class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"

class BaseResponse(BaseModel):
    """Base response model for all API endpoints"""
    status: ResponseStatus = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

class SuccessResponse(BaseResponse):
    """Success response model"""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Success status")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")

class ErrorResponse(BaseResponse):
    """Error response model"""
    status: ResponseStatus = Field(default=ResponseStatus.ERROR, description="Error status")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")

class PaginatedResponse(BaseResponse, Generic[T]):
    """Paginated response model"""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Success status")
    data: List[T] = Field(..., description="List of items")
    pagination: Dict[str, Any] = Field(..., description="Pagination information")
    total_count: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")

class AuditLogBase(BaseModel):
    """Base audit log model"""
    action_type: str = Field(..., description="Type of action performed")
    table_name: str = Field(..., description="Database table affected")
    record_id: int = Field(..., description="ID of the affected record")
    old_values: Optional[Dict[str, Any]] = Field(None, description="Previous values")
    new_values: Optional[Dict[str, Any]] = Field(None, description="New values")
    user_id: Optional[int] = Field(None, description="User who performed the action")
    session_id: Optional[str] = Field(None, description="Session ID")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")

class AuditLogCreate(AuditLogBase):
    """Create audit log model"""
    pass

class AuditLogUpdate(BaseModel):
    """Update audit log model"""
    action_type: Optional[str] = None
    table_name: Optional[str] = None
    record_id: Optional[int] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class AuditLogResponse(AuditLogBase):
    """Audit log response model"""
    audit_log_id: int = Field(..., description="Audit log ID")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        orm_mode = True

class NotificationBase(BaseModel):
    """Base notification model"""
    notification_type: str = Field(..., description="Type of notification")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    recipient_id: int = Field(..., description="Recipient user ID")
    sender_id: Optional[int] = Field(None, description="Sender user ID")
    priority: str = Field(default="normal", description="Notification priority")
    action_data: Optional[Dict[str, Any]] = Field(None, description="Action data")
    is_read: str = Field(default="N", description="Read status")

class NotificationCreate(NotificationBase):
    """Create notification model"""
    pass

class NotificationUpdate(BaseModel):
    """Update notification model"""
    notification_type: Optional[str] = None
    title: Optional[str] = None
    message: Optional[str] = None
    recipient_id: Optional[int] = None
    sender_id: Optional[int] = None
    priority: Optional[str] = None
    action_data: Optional[Dict[str, Any]] = None
    is_read: Optional[str] = None

class NotificationResponse(NotificationBase):
    """Notification response model"""
    notification_id: int = Field(..., description="Notification ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        orm_mode = True

class PaymentTransactionBase(BaseModel):
    """Base payment transaction model"""
    business_user_id: int = Field(..., description="Business user ID")
    customer_id: Optional[int] = Field(None, description="Customer ID")
    booking_id: Optional[int] = Field(None, description="Booking ID")
    transaction_type: str = Field(..., description="Transaction type")
    payment_method: str = Field(..., description="Payment method")
    amount: float = Field(..., description="Transaction amount")
    currency: str = Field(default="INR", description="Currency")
    transaction_status: str = Field(..., description="Transaction status")
    gateway_transaction_id: Optional[str] = Field(None, description="Gateway transaction ID")
    gateway_response: Optional[Dict[str, Any]] = Field(None, description="Gateway response")
    description: Optional[str] = Field(None, description="Transaction description")

class PaymentTransactionCreate(PaymentTransactionBase):
    """Create payment transaction model"""
    pass

class PaymentTransactionUpdate(BaseModel):
    """Update payment transaction model"""
    business_user_id: Optional[int] = None
    customer_id: Optional[int] = None
    booking_id: Optional[int] = None
    transaction_type: Optional[str] = None
    payment_method: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    transaction_status: Optional[str] = None
    gateway_transaction_id: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = None
    description: Optional[str] = None

class PaymentTransactionResponse(PaymentTransactionBase):
    """Payment transaction response model"""
    transaction_id: int = Field(..., description="Transaction ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        orm_mode = True

class StaffBase(BaseModel):
    """Base staff model"""
    business_user_id: int = Field(..., description="Business user ID")
    full_name: str = Field(..., description="Staff full name")
    specialization: Optional[str] = Field(None, description="Staff specialization")
    phone: str = Field(..., description="Phone number")
    email: Optional[str] = Field(None, description="Email address")
    address: Optional[str] = Field(None, description="Address")
    qualification: Optional[str] = Field(None, description="Qualification")
    experience_years: Optional[int] = Field(None, description="Years of experience")
    staff_type: str = Field(..., description="Staff type")
    is_active: str = Field(default="Y", description="Active status")

class StaffCreate(StaffBase):
    """Create staff model"""
    pass

class StaffUpdate(BaseModel):
    """Update staff model"""
    business_user_id: Optional[int] = None
    full_name: Optional[str] = None
    specialization: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    qualification: Optional[str] = None
    experience_years: Optional[int] = None
    staff_type: Optional[str] = None
    is_active: Optional[str] = None

class StaffResponse(StaffBase):
    """Staff response model"""
    staff_id: int = Field(..., description="Staff ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        orm_mode = True

# API Response Models
class APIResponse(BaseModel):
    """Standard API response model"""
    success: bool = Field(..., description="Success status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    errors: Optional[List[str]] = Field(None, description="Error messages")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=10, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: Optional[str] = Field(default="asc", description="Sort order (asc/desc)")

class FilterParams(BaseModel):
    """Filter parameters"""
    search: Optional[str] = Field(None, description="Search term")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filter criteria")
    date_from: Optional[datetime] = Field(None, description="Start date")
    date_to: Optional[datetime] = Field(None, description="End date")

class QueryParams(PaginationParams, FilterParams):
    """Combined query parameters"""
    pass 