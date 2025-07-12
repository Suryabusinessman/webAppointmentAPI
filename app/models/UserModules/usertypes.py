from sqlalchemy import Column, Integer, String, CHAR, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class UserType(Base):
    __tablename__ = 'usertypes'

    User_Type_Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    User_Type_Name = Column(String(100), unique=True, index=True, nullable=False)
    User_Type_Desc = Column(String(255), nullable=True)
    Default_Page = Column(String(255), nullable=True)
    Is_Member = Column(CHAR(1), nullable=False, default='Y')
    Is_Active = Column(CHAR(1), nullable=False, default='Y')
    Added_By = Column(Integer, nullable=True)
    Added_On = Column(DateTime, default=datetime.utcnow, nullable=False)

    Modified_By = Column(Integer, nullable=True)
    Modified_On = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    Deleted_By = Column(Integer, nullable=True)
    Deleted_On = Column(DateTime, default=datetime.utcnow, nullable=True)

    Is_Deleted = Column(CHAR(1), nullable=False, default='N')
        # Define the relationship to the User model
    # users = relationship("User", back_populates="usertypes")
    users = relationship("User", back_populates="user_type")
    user_permissions = relationship("UserPermission", back_populates="user_type")
    bussinessman_users = relationship("BusinessmanUser", back_populates="user_type")
    