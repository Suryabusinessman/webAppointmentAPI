from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PageBase(BaseModel):
    page_name: str = Field(..., description="Unique name for the page")
    page_display_text: str = Field(..., description="Display text for the page")
    page_navigation_url: Optional[str] = Field(None, description="URL for navigation")
    page_parent_id: Optional[int] = Field(None, description="Parent page ID for hierarchy")
    is_internal: Optional[str] = Field('Y', description="Whether the page is internal or external")


class PageCreate(PageBase):
    added_by: Optional[int] = Field(None, description="User ID who created the page")


class PageUpdate(BaseModel):
    page_name: Optional[str] = Field(None, description="Unique name for the page")
    page_display_text: Optional[str] = Field(None, description="Display text for the page")
    page_navigation_url: Optional[str] = Field(None, description="URL for navigation")
    page_parent_id: Optional[int] = Field(None, description="Parent page ID for hierarchy")
    is_internal: Optional[str] = Field('Y', description="Whether the page is internal or external")
    modified_by: Optional[int] = Field(None, description="User ID who modified the page")
    is_deleted: Optional[str] = Field('N', description="Soft delete flag")
    deleted_by: Optional[int] = Field(None, description="User ID who deleted the page")
    deleted_on: Optional[datetime] = Field(None, description="Deletion timestamp")


class PageResponse(PageBase):
    page_id: int = Field(..., description="Unique identifier for the page")
    added_by: Optional[int] = Field(None, description="User ID who created the page")
    added_on: datetime = Field(..., description="Creation timestamp")
    modified_by: Optional[int] = Field(None, description="User ID who modified the page")
    modified_on: datetime = Field(..., description="Last modification timestamp")
    deleted_by: Optional[int] = Field(None, description="User ID who deleted the page")
    deleted_on: Optional[datetime] = Field(None, description="Deletion timestamp")
    is_deleted: Optional[str] = Field('N', description="Soft delete flag")

    class Config:
        from_attributes = True
