from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserSessionBase(BaseModel):
    User_Id: int
    Token: str
    Device_Info: Optional[str] = None
    IP_Address: Optional[str] = None
    Is_Active: Optional[bool] = True
    Created_At: Optional[datetime] = None
    Expires_At: Optional[datetime] = None
    Login_Timestamp: Optional[datetime] = None
    Logout_Timestamp: Optional[datetime] = None

class UserSessionCreate(UserSessionBase):
    """
    Schema for creating a new user session.
    """
    pass

class UserSessionUpdate(BaseModel):
    """
    Schema for updating an existing user session.
    """
    Logout_Timestamp: Optional[datetime] = None
    Is_Active: Optional[bool] = None

class LogoutRequest(BaseModel):
    token: str

class UserSessionOut(UserSessionBase):
    """
    Schema for returning user session details in responses.
    """
    Session_Id: int
    Added_By: Optional[int] = None
    Added_On: Optional[datetime] = None
    Modified_By: Optional[int] = None
    Modified_On: Optional[datetime] = None
    Deleted_By: Optional[int] = None
    Deleted_On: Optional[datetime] = None
    Is_Deleted: Optional[str] = 'N'

    class Config:
        orm_mode = True