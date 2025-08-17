from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Base schema for LocationUserAddress
class LocationUserAddressBase(BaseModel):
    user_id: int = Field(..., description="User ID")
    location_id: int = Field(..., description="Location ID")
    pincode_id: int = Field(..., description="Pincode ID")
    address_line1: str = Field(..., description="Address line 1")
    address_line2: Optional[str] = Field(None, description="Address line 2")
    city: str = Field(..., description="City")
    pincode: str = Field(..., description="Pincode")
    longitude: str = Field(..., description="Longitude")
    latitude: str = Field(..., description="Latitude")
    map_location_url: Optional[str] = Field(None, description="Map location URL")
    address_type: str = Field(..., description="Address type (Home, Office, etc.)")
    is_default: str = Field(default="N", description="Default address status")
    is_active: str = Field(default="Y", description="Active status")

class LocationUserAddressCreate(LocationUserAddressBase):
    pass 

class LocationUserAddressUpdate(BaseModel):
    user_id: Optional[int] = Field(None, description="User ID")
    location_id: Optional[int] = Field(None, description="Location ID")
    pincode_id: Optional[int] = Field(None, description="Pincode ID")
    address_line1: Optional[str] = Field(None, description="Address line 1")
    address_line2: Optional[str] = Field(None, description="Address line 2")
    city: Optional[str] = Field(None, description="City")
    pincode: Optional[str] = Field(None, description="Pincode")
    longitude: Optional[str] = Field(None, description="Longitude")
    latitude: Optional[str] = Field(None, description="Latitude")
    map_location_url: Optional[str] = Field(None, description="Map location URL")
    address_type: Optional[str] = Field(None, description="Address type")
    is_default: Optional[str] = Field(None, description="Default address status")
    is_active: Optional[str] = Field(None, description="Active status")

class LocationUserAddressResponse(LocationUserAddressBase):
    user_address_id: int = Field(..., description="User address ID")
    user_name: Optional[str] = Field(None, description="User name")
    location_name: Optional[str] = Field(None, description="Location name")
    pincode_value: Optional[str] = Field(None, description="Pincode value")
    added_by: Optional[int] = Field(None, description="Added by user ID")
    added_on: datetime = Field(..., description="Creation timestamp")
    modified_by: Optional[int] = Field(None, description="Modified by user ID")
    modified_on: Optional[datetime] = Field(None, description="Last update timestamp")
    deleted_by: Optional[int] = Field(None, description="Deleted by user ID")
    deleted_on: Optional[datetime] = Field(None, description="Deletion timestamp")
    is_deleted: str = Field(..., description="Soft delete status")

    class Config:
        orm_mode = True
