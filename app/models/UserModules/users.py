from sqlalchemy import Column, Integer, String, DateTime,Date, Boolean, CHAR, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class User(Base):
    __tablename__ = 'users'

    User_Id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # Unique identifier for the user
    Full_Name = Column(String(100), nullable=False)
    Email = Column(String(100), unique=True, index=True, nullable=False)
    Phone = Column(String(15), unique=True, index=True, nullable=True)
    Alt_Phone = Column(String(15), nullable=True)
    Password_Hash = Column(String(255), nullable=False)

    # Forgot password fields
    Forgot_Token = Column(String(255), nullable=True)
    Forgot_Token_Expiry = Column(DateTime, nullable=True)

    # User classification
    User_Type_Id = Column(Integer, ForeignKey('usertypes.User_Type_Id'), nullable=True)  # FK to usertypes table
    # Business_Model = Column(String(10), nullable=True)  # B2B, B2C, C2C, etc.

    # Profile info
    Profile_Image = Column(String(255), nullable=True)
    Background_Image = Column(String(255), nullable=True)
    Bio = Column(Text, nullable=True)
    Website = Column(String(255), nullable=True)
    Social_Links = Column(Text, nullable=True)  # Store as JSON string or key-value text

    # Personal info
    Gender = Column(String(10), nullable=True)
    DOB = Column(Date, nullable=True)
    Occupation = Column(String(100), nullable=True)
    Company_Name = Column(String(100), nullable=True)
    GST_Number = Column(String(50), nullable=True)
    Referral_Code = Column(String(50), nullable=True)

    # Location
    Address = Column(String(255), nullable=True)
    City = Column(String(100), nullable=True)
    State = Column(String(100), nullable=True)
    Country = Column(String(100), nullable=True)
    Postal_Code = Column(String(20), nullable=True)

    # Preferences and status
    Preferred_Language = Column(String(10), default='en', nullable=True)
    Is_Verified = Column(Boolean, default=False, nullable=False)
    Is_Active = Column(CHAR(1), default='Y', nullable=False)
    Is_Deleted = Column(CHAR(1), default='N', nullable=False)

    # Wallet & payments
    Wallet_Balance = Column(Float, default=0.0, nullable=False)
    Currency = Column(String(10), default='INR', nullable=True)
    Last_Transaction_Id = Column(String(100), nullable=True)
    Payment_Mode = Column(String(50), nullable=True)  # wallet, card, upi, etc.
    Is_Wallet_Enabled = Column(Boolean, default=True, nullable=False)

    # Audit fields
    Added_By = Column(Integer, nullable=True)
    Added_On = Column(DateTime, default=datetime.utcnow, nullable=False)
    Modified_By = Column(Integer, nullable=True)
    Modified_On = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    Deleted_By = Column(Integer, nullable=True)
    Deleted_On = Column(DateTime, nullable=True)

    # Relationships
    # role = relationship("UserType", back_populates="users")
    user_type = relationship("UserType", back_populates="users")  # Relationship with UserType model
    sessions = relationship("UserSession", back_populates="user")
    bussinessman_users = relationship("BusinessmanUser", back_populates="user")
    locationuseraddress = relationship("LocationUserAddress", back_populates="user")
    