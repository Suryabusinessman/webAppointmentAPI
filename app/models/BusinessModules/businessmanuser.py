from sqlalchemy import Column,String, Integer, CHAR, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class BusinessmanUser(Base):
    __tablename__ = "businessmanusers"

    Businessman_User_Id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    User_Id= Column(Integer, ForeignKey("users.User_Id"), nullable=False)
    User_Type_Id = Column(Integer, ForeignKey("usertypes.User_Type_Id"), nullable=False)
    Business_Type_Id = Column(Integer, ForeignKey("businesstypes.Business_Type_Id"), nullable=False)
    Brand_Name = Column(String(100), nullable=False)
    Business_Type_Name = Column(String(100), nullable=False)
    Is_Active = Column(CHAR(1), nullable=False, default='Y')
    Business_Code = Column(String(100), nullable=True)
    Business_Status = Column(String(50), nullable=True)
    Bussiness_Logo = Column(String(500), nullable=True)
    Bussiness_Banner = Column(String(500), nullable=True)
    Bussiness_Description = Column(String(500), nullable=True)

    Added_By = Column(Integer, nullable=True)
    Added_On = Column(DateTime, default=datetime.utcnow, nullable=False)
    Modified_By = Column(Integer, nullable=True)
    Modified_On = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    Is_Deleted = Column(CHAR(1), default='N', nullable=False)
    Deleted_By = Column(Integer, nullable=True)
    Deleted_On = Column(DateTime, nullable=True)

    # ✅ Relationships
    # businessman = relationship("Businessman", back_populates="businessmanuser", lazy="joined")
    user = relationship("User", back_populates="bussinessman_users")
    user_type = relationship("UserType", back_populates="bussinessman_users")
    businesstype = relationship("BusinessType", back_populates="bussinessman_users")