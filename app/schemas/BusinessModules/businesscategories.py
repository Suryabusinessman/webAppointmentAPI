from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ----------- Base Schema -----------
class BusinessCategoryBase(BaseModel):
    Business_Type_Id: int
    Business_Category_Name: str
    Business_Category_Short_Name: str
    Business_Category_Code: Optional[str]
    Is_Active: Optional[str] = 'Y'
    Business_Category_Media: Optional[str]
    Business_Category_Description: Optional[str]
    Added_By: Optional[int]
    Added_On: Optional[datetime] = datetime.utcnow()
    Is_Deleted: Optional[str] = 'N'

class BusinessCategoryCreate(BusinessCategoryBase):
    # pass
    Added_By: Optional[int]
    Added_On: Optional[datetime] = datetime.utcnow()

# ----------- Update Schema ----------

class BusinessCategoryUpdate(BaseModel):
    Business_Type_Id: Optional[int]
    Business_Category_Name: Optional[str]
    Business_Category_Short_Name: Optional[str]
    Business_Category_Code: Optional[str]
    Is_Active: Optional[str] = 'Y'
    Business_Category_Media: Optional[str]
    Business_Category_Description: Optional[str]
    Modified_By: Optional[int]
    Modified_On: Optional[datetime] = datetime.utcnow()
    Is_Deleted: Optional[str] = 'N'


# ----------- Output Schema ----------
class BusinessCategoryOut(BusinessCategoryBase):
    Business_Category_Id: int
    Added_On: datetime
    Modified_On: Optional[datetime] = datetime.utcnow()
    Deleted_On: Optional[datetime] = datetime.utcnow()

    class Config:
        orm_mode = True
