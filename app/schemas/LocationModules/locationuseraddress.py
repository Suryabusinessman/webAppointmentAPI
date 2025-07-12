from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Base schema for LocationUserAddress
class LocationUserAddressBase(BaseModel):
    User_Id: int
    Location_Id: int
    Pincode_Id: int
    Address_Line1: str
    Address_Line2: Optional[str]
    City: str
    Pincode: str
    Longitude: str
    Latitude: str
    Map_Location_Url: Optional[str]
    Address_Type: str  # e.g., Home, Office, etc.
    Is_Default: str = 'N'
    Is_Active: str = 'Y'
    Added_By: Optional[int]
    Added_On: datetime = datetime.utcnow()

class LocationUserAddressCreate(LocationUserAddressBase):
    pass 

class LocationUserAddressUpdate(LocationUserAddressBase):
    User_Address_Id: int
    Modified_By: Optional[int]
    Modified_On: datetime = datetime.utcnow()
class LocationUserAddressOut(LocationUserAddressBase):
    User_Address_Id: int
    Modified_By: Optional[int]
    Modified_On: Optional[datetime]
    Deleted_By: Optional[int]
    Deleted_On: Optional[datetime]

    class Config:
        orm_mode = True
