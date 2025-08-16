from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Union
from datetime import datetime

class BusinessTypeBase(BaseModel):
    """Base business type model"""
    type_name: str = Field(..., description="Business type name")
    description: Optional[str] = Field(None, description="Business type description")
    icon: Optional[str] = Field(None, description="Icon for business type")
    color: Optional[str] = Field(None, description="Color code for business type")
    features: Optional[Union[Dict[str, Any], str]] = Field(None, description="Features available for this business type (JSON object or string)")
    business_media: Optional[str] = Field(None, description="Business media file path")
    is_active: str = Field(default="Y", description="Active status")

class BusinessTypeCreate(BusinessTypeBase):
    """Create business type model"""
    pass

class BusinessTypeUpdate(BaseModel):
    """Update business type model"""
    type_name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    features: Optional[Union[Dict[str, Any], str]] = None
    business_media: Optional[str] = None
    is_active: Optional[str] = None

class BusinessTypeResponse(BusinessTypeBase):
    """Business type response model"""
    business_type_id: int = Field(..., description="Business type ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True
