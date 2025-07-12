from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Base schema for LocationMaster
class LocationMasterBase(BaseModel):
    Location_Name: str
    Location_City_Name: str
    Location_Dist_Name: Optional[str]
    Location_State_Name: Optional[str]
    Location_Country_Name: Optional[str]
    Location_Desc: Optional[str]
    Is_Active: Optional[str] = 'Y'
    Is_Deleted: Optional[str] = 'N'
    Added_By: Optional[int] 
    Added_On: Optional[datetime] = datetime.utcnow()

class LocationMasterCreate(LocationMasterBase):
    # pass
    Added_By: Optional[int]
    Added_On: Optional[datetime] = datetime.utcnow()

class LocationMasterUpdate(LocationMasterBase):
    Modified_By: Optional[int]
    Modified_On: Optional[datetime] = datetime.utcnow()

class LocationMasterOut(LocationMasterBase):
    Location_Id: int
    Modified_By: Optional[int]
    Modified_On: Optional[datetime]
    Deleted_By: Optional[int]
    Deleted_On: Optional[datetime]

    class Config:
        orm_mode = True