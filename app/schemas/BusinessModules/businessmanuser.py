from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ----------- Base Schema -----------

class BusinessUserBase(BaseModel):
    user_id: int = Field(..., description="User ID")
    business_type_id: int = Field(..., description="Business type ID")
    business_name: str = Field(..., description="Business name")
    business_description: Optional[str] = Field(None, description="Business description")
    business_logo: Optional[str] = Field(None, description="Business logo file path")
    business_banner: Optional[str] = Field(None, description="Business banner file path")
    business_address: Optional[str] = Field(None, description="Business address")
    business_phone: Optional[str] = Field(None, description="Business phone number")
    business_email: Optional[str] = Field(None, description="Business email")
    business_website: Optional[str] = Field(None, description="Business website")
    gst_number: Optional[str] = Field(None, description="GST number")
    pan_number: Optional[str] = Field(None, description="PAN number")
    business_license: Optional[str] = Field(None, description="Business license")
    subscription_plan: str = Field(default="FREE", description="Subscription plan")
    subscription_status: str = Field(default="Active", description="Subscription status")
    subscription_start_date: Optional[datetime] = Field(None, description="Subscription start date")
    subscription_end_date: Optional[datetime] = Field(None, description="Subscription end date")
    monthly_limit: Optional[int] = Field(None, description="Monthly usage limit")
    current_month_usage: int = Field(default=0, description="Current month usage")
    is_verified: str = Field(default="N", description="Verification status")
    is_active: str = Field(default="Y", description="Active status")
    is_featured: str = Field(default="N", description="Featured status")
    rating: float = Field(default=0.0, description="Business rating")
    total_reviews: int = Field(default=0, description="Total reviews")

# ----------- Create Schema -----------

class BusinessUserCreate(BusinessUserBase):
    pass

# ----------- Multiple Business Types Create Schema -----------

class BusinessUserCreateMultiple(BaseModel):
    user_id: int = Field(..., description="User ID")
    business_type_ids: List[int] = Field(..., description="List of business type IDs")
    business_name: str = Field(..., description="Business name")
    business_description: Optional[str] = Field(None, description="Business description")
    business_address: Optional[str] = Field(None, description="Business address")
    business_phone: Optional[str] = Field(None, description="Business phone number")
    business_email: Optional[str] = Field(None, description="Business email")
    business_website: Optional[str] = Field(None, description="Business website")
    gst_number: Optional[str] = Field(None, description="GST number")
    pan_number: Optional[str] = Field(None, description="PAN number")
    business_license: Optional[str] = Field(None, description="Business license")
    subscription_plan: str = Field(default="FREE", description="Subscription plan")
    subscription_status: str = Field(default="Active", description="Subscription status")
    subscription_start_date: Optional[datetime] = Field(None, description="Subscription start date")
    subscription_end_date: Optional[datetime] = Field(None, description="Subscription end date")
    monthly_limit: Optional[int] = Field(None, description="Monthly usage limit")
    current_month_usage: int = Field(default=0, description="Current month usage")
    is_verified: str = Field(default="N", description="Verification status")
    is_active: str = Field(default="Y", description="Active status")
    is_featured: str = Field(default="N", description="Featured status")
    rating: float = Field(default=0.0, description="Business rating")
    total_reviews: int = Field(default=0, description="Total reviews")

# ----------- Update Schema -----------

class BusinessUserUpdate(BaseModel):
    user_id: Optional[int] = Field(None, description="User ID")
    business_type_id: Optional[int] = Field(None, description="Business type ID")
    business_name: Optional[str] = Field(None, description="Business name")
    business_description: Optional[str] = Field(None, description="Business description")
    business_logo: Optional[str] = Field(None, description="Business logo file path")
    business_banner: Optional[str] = Field(None, description="Business banner file path")
    business_address: Optional[str] = Field(None, description="Business address")
    business_phone: Optional[str] = Field(None, description="Business phone number")
    business_email: Optional[str] = Field(None, description="Business email")
    business_website: Optional[str] = Field(None, description="Business website")
    gst_number: Optional[str] = Field(None, description="GST number")
    pan_number: Optional[str] = Field(None, description="PAN number")
    business_license: Optional[str] = Field(None, description="Business license")
    subscription_plan: Optional[str] = Field(None, description="Subscription plan")
    subscription_status: Optional[str] = Field(None, description="Subscription status")
    subscription_start_date: Optional[datetime] = Field(None, description="Subscription start date")
    subscription_end_date: Optional[datetime] = Field(None, description="Subscription end date")
    monthly_limit: Optional[int] = Field(None, description="Monthly usage limit")
    current_month_usage: Optional[int] = Field(None, description="Current month usage")
    is_verified: Optional[str] = Field(None, description="Verification status")
    is_active: Optional[str] = Field(None, description="Active status")
    is_featured: Optional[str] = Field(None, description="Featured status")
    rating: Optional[float] = Field(None, description="Business rating")
    total_reviews: Optional[int] = Field(None, description="Total reviews")

# ----------- Output Schema -----------

class BusinessUserResponse(BusinessUserBase):
    business_user_id: int = Field(..., description="Business user ID")
    # User information
    user_full_name: Optional[str] = Field(None, description="User's full name")
    user_first_name: Optional[str] = Field(None, description="User's first name")
    user_last_name: Optional[str] = Field(None, description="User's last name")
    # Business type information
    business_type_name: Optional[str] = Field(None, description="Business type name")
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True