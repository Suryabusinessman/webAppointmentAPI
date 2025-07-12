from sqlalchemy import Column, Integer, CHAR, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class UserSession(Base):
    __tablename__ = "usersessions"

    Session_Id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # Unique identifier for the session
    User_Id = Column(Integer, ForeignKey("users.User_Id"), nullable=False)
    Token = Column(String(255), unique=True, nullable=False)  # Specify length for VARCHAR
    Device_Info = Column(String(255), nullable=True)  # Specify length for VARCHAR
    IP_Address = Column(String(45), nullable=True)  # Length for IPv4/IPv6 addresses
    Is_Active = Column(Boolean, default=True)
    Created_At = Column(DateTime, default=datetime.utcnow)
    Expires_At = Column(DateTime, nullable=True)
    Login_Timestamp = Column(DateTime, default=datetime.utcnow)
    Logout_Timestamp = Column(DateTime, nullable=True)

    # Audit fields
    Added_By = Column(Integer, nullable=True)
    Added_On = Column(DateTime, default=datetime.utcnow, nullable=False)
    Modified_By = Column(Integer, nullable=True)
    Modified_On = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    Deleted_By = Column(Integer, nullable=True)
    Deleted_On = Column(DateTime, nullable=True)
    Is_Deleted = Column(CHAR(1), default='N', nullable=False)

    # Relationship with the User table
    user = relationship("User", back_populates="sessions")