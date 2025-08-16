from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Base schema for LocationActivePincode
class LocationActivePincodeBase(BaseModel):
    pincode: str = Field(..., description="Pincode")
    location_id: int = Field(..., description="Location ID")
    location_status: Optional[str] = Field(None, description="Location status")
    is_active: str = Field(default="Y", description="Active status")
    is_deleted: str = Field(default="N", description="Deleted status")

class LocationActivePincodeCreate(LocationActivePincodeBase):
    pass

class LocationActivePincodeUpdate(BaseModel):
    pincode: Optional[str] = Field(None, description="Pincode")
    location_id: Optional[int] = Field(None, description="Location ID")
    location_status: Optional[str] = Field(None, description="Location status")
    is_active: Optional[str] = Field(None, description="Active status")

class LocationActivePincodeResponse(LocationActivePincodeBase):
    pincode_id: int = Field(..., description="Pincode ID")
    added_by: Optional[int] = Field(None, description="Added by user ID")
    added_on: datetime = Field(..., description="Creation timestamp")
    modified_by: Optional[int] = Field(None, description="Modified by user ID")
    modified_on: Optional[datetime] = Field(None, description="Last update timestamp")
    deleted_by: Optional[int] = Field(None, description="Deleted by user ID")
    deleted_on: Optional[datetime] = Field(None, description="Deletion timestamp")

    class Config:
        orm_mode = True