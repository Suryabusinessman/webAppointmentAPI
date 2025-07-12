from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PageBase(BaseModel):
    Page_Name: str
    Page_Display_Text: str
    Page_Navigation_URL: Optional[str]
    Page_Parent_Id: Optional[int]
    Is_Internal: Optional[str] = 'Y'


class PageCreate(PageBase):
    Added_By: Optional[int]


class PageUpdate(BaseModel):
    Page_Name: Optional[str]
    Page_Display_Text: Optional[str]
    Page_Navigation_URL: Optional[str]
    Page_Parent_Id: Optional[int]
    Is_Internal: Optional[str] = 'Y'
    Modified_By: Optional[int]
    Is_Deleted: Optional[str]
    Deleted_By: Optional[int]
    Deleted_On: Optional[datetime]= datetime.utcnow()


class PageOut(PageBase):
    Page_Id: int
    Added_By: Optional[int]
    Added_On: datetime
    Modified_By: Optional[int]
    Modified_On: datetime
    Deleted_By: Optional[int]
    Deleted_On: Optional[datetime]
    Is_Deleted: Optional[str] = 'N'

    class Config:
        orm_mode = True
