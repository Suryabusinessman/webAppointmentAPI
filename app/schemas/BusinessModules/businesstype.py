from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ----------- Base Schema -----------

class BusinessTypeBase(BaseModel):
    Business_Type_Name: str
    Business_Type_Desc: Optional[str]
    Business_Code: Optional[str]
    Business_Status: Optional[str]
    Is_Active: Optional[str] = 'Y'
    Business_Media: Optional[str]
    Added_By: Optional[int]
    Modified_By: Optional[int]
    Deleted_By: Optional[int]
    Is_Deleted: Optional[str] = 'N'

# ----------- Create Schema -----------

class BusinessTypeCreate(BusinessTypeBase):
    # pass
     Added_By: Optional[int]

# ----------- Update Schema -----------

class BusinessTypeUpdate(BaseModel):
    Business_Type_Name: Optional[str]
    Business_Type_Desc: Optional[str]
    Business_Code: Optional[str]
    Business_Status: Optional[str]
    Is_Active: Optional[str] = 'Y'
    Business_Media: Optional[str]
    Modified_By: Optional[int]
    Modified_On: Optional[datetime] = datetime.utcnow()
    Is_Deleted: Optional[str]
    Deleted_By: Optional[int]

# ----------- Output Schema -----------

class BusinessTypeOut(BusinessTypeBase):
    Business_Type_Id: int
    Added_On: datetime
    Modified_On: Optional[datetime]= datetime.utcnow()
    Deleted_On: Optional[datetime]= datetime.utcnow()

    class Config:
        orm_mode = True
