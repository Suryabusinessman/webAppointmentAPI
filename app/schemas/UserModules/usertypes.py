from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Base schema for UserType
class UserTypeBase(BaseModel):
    type_name: str = Field(..., description="User type name")
    description: Optional[str] = Field(None, description="User type description")
    default_page: Optional[str] = Field(None, description="Default page for user type")
    permissions: Optional[str] = Field(None, description="User type permissions")
    is_active: str = Field(default="Y", description="Active status")

# Schema for creating a new UserType
class UserTypeCreate(UserTypeBase):
    pass

# Schema for updating an existing UserType
class UserTypeUpdate(BaseModel):
    type_name: Optional[str] = Field(None, description="User type name")
    description: Optional[str] = Field(None, description="User type description")
    default_page: Optional[str] = Field(None, description="Default page for user type")
    permissions: Optional[str] = Field(None, description="User type permissions")
    is_active: Optional[str] = Field(None, description="Active status")

# Schema for outputting UserType data
class UserTypeResponse(UserTypeBase):
    user_type_id: int = Field(..., description="User type ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        orm_mode = True