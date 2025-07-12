from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Base schema for LocationActivePincode
class LocationActivePincodeBase(BaseModel):
    Pincode: str
    Location_Id: int
    Location_Status: Optional[str]
    Is_Active: Optional[str] = 'Y'
    Is_Deleted: Optional[str] = 'N'
    Added_By: Optional[int] 
    Added_On: Optional[datetime] = datetime.utcnow()

class LocationActivePincodeCreate(LocationActivePincodeBase):
    # pass
    Added_By: Optional[int]
    Added_On: Optional[datetime] = datetime.utcnow()

class LocationActivePincodeUpdate(LocationActivePincodeBase):
    Modified_By: Optional[int]
    Modified_On: Optional[datetime] = datetime.utcnow()

class LocationActivePincodeOut(LocationActivePincodeBase):
    Pincode_Id: int
    Modified_By: Optional[int]
    Modified_On: Optional[datetime]
    Deleted_By: Optional[int]
    Deleted_On: Optional[datetime]

    class Config:
        orm_mode = True