from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ----------- Base Schema -----------
class BusinessCategoryBase(BaseModel):
    business_type_id: int = Field(..., description="Business type ID")
    business_category_name: str = Field(..., description="Business category name")
    business_category_short_name: str = Field(..., description="Business category short name")
    business_category_code: Optional[str] = Field(None, description="Business category code")
    is_active: str = Field(default="Y", description="Active status")
    business_category_media: Optional[str] = Field(None, description="Business category media file path")
    icon: Optional[str] = Field(None, description="Icon file path for business category")
    business_category_description: Optional[str] = Field(None, description="Business category description")

class BusinessCategoryCreate(BusinessCategoryBase):
    pass

# ----------- Update Schema ----------
class BusinessCategoryUpdate(BaseModel):
    business_type_id: Optional[int] = Field(None, description="Business type ID")
    business_category_name: Optional[str] = Field(None, description="Business category name")
    business_category_short_name: Optional[str] = Field(None, description="Business category short name")
    business_category_code: Optional[str] = Field(None, description="Business category code")
    is_active: Optional[str] = Field(None, description="Active status")
    business_category_media: Optional[str] = Field(None, description="Business category media file path")
    icon: Optional[str] = Field(None, description="Icon file path for business category")
    business_category_description: Optional[str] = Field(None, description="Business category description")

# ----------- Output Schema ----------
class BusinessCategoryResponse(BusinessCategoryBase):
    business_category_id: int = Field(..., description="Business category ID")
    business_type_name: Optional[str] = Field(None, description="Business type name")
    added_by: Optional[int] = Field(None, description="Added by user ID")
    added_on: datetime = Field(..., description="Creation timestamp")
    modified_by: Optional[int] = Field(None, description="Modified by user ID")
    modified_on: Optional[datetime] = Field(None, description="Last update timestamp")
    is_deleted: str = Field(default="N", description="Deleted status")
    deleted_by: Optional[int] = Field(None, description="Deleted by user ID")
    deleted_on: Optional[datetime] = Field(None, description="Deletion timestamp")

    class Config:
        orm_mode = True
