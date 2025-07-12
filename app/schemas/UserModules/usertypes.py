from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Base schema for UserType
class UserTypeBase(BaseModel):
    User_Type_Name: str
    User_Type_Desc: Optional[str]
    Default_Page: Optional[str]
    Is_Member: Optional[str] = 'Y'
    Is_Active: Optional[str] = 'Y'
    Is_Deleted: Optional[str] = 'N'

# Schema for creating a new UserType
class UserTypeCreate(UserTypeBase):
    Added_By: Optional[int]

# Schema for updating an existing UserType
class UserTypeUpdate(UserTypeBase):
    User_Type_Name: str
    User_Type_Desc: Optional[str]
    Default_Page: Optional[str]
    Is_Member: Optional[str] = 'Y'
    Is_Active: Optional[str] = 'Y'
    Modified_By: Optional[int]
    Modified_On: Optional[datetime] = datetime.utcnow()

# Schema for outputting UserType data
class UserTypeOut(UserTypeBase):
    User_Type_Id: int
    Added_By: Optional[int]
    Added_On: datetime
    Modified_By: Optional[int]
    Modified_On: Optional[datetime]
    Deleted_By: Optional[int]
    Deleted_On: Optional[datetime]

    class Config:
        orm_mode = True