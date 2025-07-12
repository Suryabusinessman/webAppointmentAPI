from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ----------- Base Schema -----------

class BusinessUserBase(BaseModel):
    User_Id: int
    User_Type_Id: int
    Business_Type_Id: int
    Brand_Name: str
    Business_Type_Name: str
    Is_Active: Optional[str] = 'Y'
    Business_Code: Optional[str]
    Business_Status: Optional[str]
    Bussiness_Logo: Optional[str]
    Bussiness_Banner: Optional[str]
    Bussiness_Description: Optional[str]

    Added_By: Optional[int]
    Modified_By: Optional[int]
    Deleted_By: Optional[int]
    Is_Deleted: Optional[str] = 'N'

# ----------- Create Schema -----------

class BusinessmanUserCreate(BusinessUserBase):
    # pass
     Added_By: Optional[int]

# ----------- Update Schema -----------

class BusinessmanUserUpdate(BaseModel):
    User_Id: int
    User_Type_Id: int
    Business_Type_Id: int
    Brand_Name: str
    Business_Type_Name: str
    Is_Active: Optional[str] = 'Y'
    Business_Code: Optional[str]
    Business_Status: Optional[str]
    Bussiness_Logo: Optional[str]
    Bussiness_Banner: Optional[str]
    Bussiness_Description: Optional[str]
    Modified_By: Optional[int]
    Modified_On: Optional[datetime] = datetime.utcnow()
    Is_Deleted: Optional[str] = 'N'
    Deleted_By: Optional[int]

# ----------- Output Schema -----------

class BusinessUserOut(BusinessUserBase):
    Business_User_Id: int
    Added_On: datetime
    Modified_On: Optional[datetime]= datetime.utcnow()
    Deleted_On: Optional[datetime]= datetime.utcnow()

    class Config:
        orm_mode = True