from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Base schema for LocationMaster
class LocationMasterBase(BaseModel):
    location_name: str = Field(..., description="Location name")
    location_city_name: str = Field(..., description="City name")
    location_dist_name: Optional[str] = Field(None, description="District name")
    location_state_name: Optional[str] = Field(None, description="State name")
    location_country_name: Optional[str] = Field(None, description="Country name")
    location_desc: Optional[str] = Field(None, description="Location description")
    is_active: str = Field(default="Y", description="Active status")
    is_deleted: str = Field(default="N", description="Deleted status")

class LocationMasterCreate(LocationMasterBase):
    pass

class LocationMasterUpdate(BaseModel):
    location_name: Optional[str] = Field(None, description="Location name")
    location_city_name: Optional[str] = Field(None, description="City name")
    location_dist_name: Optional[str] = Field(None, description="District name")
    location_state_name: Optional[str] = Field(None, description="State name")
    location_country_name: Optional[str] = Field(None, description="Country name")
    location_desc: Optional[str] = Field(None, description="Location description")
    is_active: Optional[str] = Field(None, description="Active status")

class LocationMasterResponse(LocationMasterBase):
    location_id: int = Field(..., description="Location ID")
    added_by: Optional[int] = Field(None, description="Added by user ID")
    added_on: datetime = Field(..., description="Creation timestamp")
    modified_by: Optional[int] = Field(None, description="Modified by user ID")
    modified_on: Optional[datetime] = Field(None, description="Last update timestamp")
    deleted_by: Optional[int] = Field(None, description="Deleted by user ID")
    deleted_on: Optional[datetime] = Field(None, description="Deletion timestamp")

    class Config:
        orm_mode = True