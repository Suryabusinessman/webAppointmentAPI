from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Base Schema (shared)
class UserPermissionBase(BaseModel):
    User_Type_Id: int
    Page_Id: int
    Can_View: Optional[str] = "N"
    Can_Create: Optional[str] = "N"
    Can_Update: Optional[str] = "N"
    Can_Delete: Optional[str] = "N"


# Create Schema
class UserPermissionCreate(UserPermissionBase):
    Added_By: Optional[int] 


# Update Schema
class UserPermissionUpdate(BaseModel):
    User_Type_Id: int
    Page_Id: int
    Can_View: Optional[str] = "N"
    Can_Create: Optional[str] = "N"
    Can_Update: Optional[str] = "N"
    Can_Delete: Optional[str] = "N"
    Modified_By: Optional[int] 
    Is_Deleted: Optional[str] = 'N'
    Deleted_By: Optional[int] 
    Deleted_On: Optional[datetime] 


# Output Schema
class UserPermissionOut(UserPermissionBase):
    User_Permission_Id: int
    Added_By: Optional[int]
    Added_On: datetime
    Modified_By: Optional[int]
    Modified_On: datetime
    Is_Deleted: Optional[str] = 'N'
    Deleted_By: Optional[int]
    Deleted_On: Optional[datetime]

    class Config:
        orm_mode = True
