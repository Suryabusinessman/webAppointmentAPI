from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# Base Schema (shared)
class UserPermissionBase(BaseModel):
    user_type_id: int = Field(..., description="User type ID")
    page_id: int = Field(..., description="Page ID")
    can_view: Optional[str] = Field("N", description="Can view permission")
    can_create: Optional[str] = Field("N", description="Can create permission")
    can_update: Optional[str] = Field("N", description="Can update permission")
    can_delete: Optional[str] = Field("N", description="Can delete permission")


# Create Schema
class UserPermissionCreate(UserPermissionBase):
    added_by: Optional[int] = Field(None, description="User ID who created the permission")


# Update Schema
class UserPermissionUpdate(BaseModel):
    user_type_id: Optional[int] = Field(None, description="User type ID")
    page_id: Optional[int] = Field(None, description="Page ID")
    can_view: Optional[str] = Field("N", description="Can view permission")
    can_create: Optional[str] = Field("N", description="Can create permission")
    can_update: Optional[str] = Field("N", description="Can update permission")
    can_delete: Optional[str] = Field("N", description="Can delete permission")
    modified_by: Optional[int] = Field(None, description="User ID who modified the permission")
    is_deleted: Optional[str] = Field('N', description="Soft delete flag")
    deleted_by: Optional[int] = Field(None, description="User ID who deleted the permission")
    deleted_on: Optional[datetime] = Field(None, description="Deletion timestamp")


# Response Schema
class UserPermissionResponse(UserPermissionBase):
    user_permission_id: int = Field(..., description="Unique identifier for the user permission")
    added_by: Optional[int] = Field(None, description="User ID who created the permission")
    added_on: datetime = Field(..., description="Creation timestamp")
    modified_by: Optional[int] = Field(None, description="User ID who modified the permission")
    modified_on: datetime = Field(..., description="Last modification timestamp")
    is_deleted: Optional[str] = Field('N', description="Soft delete flag")
    deleted_by: Optional[int] = Field(None, description="User ID who deleted the permission")
    deleted_on: Optional[datetime] = Field(None, description="Deletion timestamp")

    class Config:
        from_attributes = True
