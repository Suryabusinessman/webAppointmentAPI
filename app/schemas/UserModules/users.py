from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date

# from schemas.roles import RoleOut


# Base User fields
class UserBase(BaseModel):
    Full_Name: Optional[str]
    Email: Optional[EmailStr]
    Phone: Optional[str]
    Alt_Phone: Optional[str]
    # Business_Model: Optional[str]
    Gender: Optional[str]
    DOB: Optional[date]
    Occupation: Optional[str]
    Company_Name: Optional[str]
    GST_Number: Optional[str]
    Referral_Code: Optional[str]
    Address: Optional[str]
    City: Optional[str]
    State: Optional[str]
    Country: Optional[str]
    Postal_Code: Optional[str]
    Preferred_Language: Optional[str] = 'en'
    Profile_Image: Optional[str]
    Background_Image: Optional[str]
    Bio: Optional[str]
    Website: Optional[str]
    Social_Links: Optional[str]

    Wallet_Balance: Optional[float] = 0.0
    Currency: Optional[str] = "INR"
    Last_Transaction_Id: Optional[str]
    Payment_Mode: Optional[str]
    Is_Wallet_Enabled: Optional[bool] = True


# Create
class UserCreate(UserBase):
    Email: EmailStr
    Full_Name: str
    Password: str
    User_Type_Id: Optional[int]


# Register
class RegisterUser(UserCreate):
    Confirm_Password: str = Field(..., example="Confirm your password")


# Update
class UserUpdate(UserBase):
    Password: Optional[str]
    User_Type_Id: Optional[int]
    Is_Active: Optional[str]
    Is_Verified: Optional[bool]


# Login
class UserLogin(BaseModel):
    Email: EmailStr
    Password: str


# Change Password
class ChangePassword(BaseModel):
    Current_Password: str
    New_Password: str
    Confirm_Password: str


# Forgot Password
class ForgotPassword(BaseModel):
    Email: EmailStr


# Profile update
class ProfileUpdate(UserBase):
    Full_Name: Optional[str]
    Phone: Optional[str]
    Alt_Phone: Optional[str]
    Address: Optional[str]
    City: Optional[str]
    State: Optional[str]
    Country: Optional[str]
    Postal_Code: Optional[str]
    Profile_Image: Optional[str]
    Background_Image: Optional[str]
    Bio: Optional[str]


# ORM response
class UserOut(UserBase):
    User_Id: int
    Email: EmailStr
    User_Type_Id: Optional[int]
    # role: Optional[RoleOut]
    Is_Verified: bool
    Is_Active: str
    Is_Deleted: str
    Added_By: Optional[int]
    Added_On: Optional[datetime]
    Modified_By: Optional[int]
    Modified_On: Optional[datetime]
    Deleted_By: Optional[int]
    Deleted_On: Optional[datetime]

    class Config:
        orm_mode = True


# Internal DB model
class UserInDB(UserOut):
    Password_Hash: str


# General API Response
class UserResponse(BaseModel):
    status: str
    message: Optional[str]
    data: Optional[UserOut]
# User schema for output
class User(BaseModel):
    User_Id: int
    Full_Name: str
    Email: EmailStr

    class Config:
        orm_mode = True