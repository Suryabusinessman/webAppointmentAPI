from sqlalchemy import Column, Integer, String, CHAR, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class BusinessType(Base):
    __tablename__ = 'businesstypes'

    Business_Type_Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Business_Type_Name = Column(String(100), unique=True, index=True, nullable=False)
    Business_Type_Desc = Column(String(255), nullable=True)
    Business_Code = Column(String(100), nullable=True)
    Business_Status = Column(String(50), nullable=True)
    Is_Active = Column(CHAR(1), nullable=False, default='Y')
    Business_Media = Column(String(500), nullable=True)
    Added_By = Column(Integer, nullable=True)
    Added_On = Column(DateTime, default=datetime.utcnow, nullable=False)

    Modified_By = Column(Integer, nullable=True)
    Modified_On = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    Deleted_By = Column(Integer, nullable=True)
    Deleted_On = Column(DateTime, default=datetime.utcnow, nullable=True)

    Is_Deleted = Column(CHAR(1), nullable=False, default='N')

    # Define the relationship to the BusinessmanUser model
    bussinessman_users = relationship("BusinessmanUser", back_populates="businesstype")
    # Define the relationship to the BusinessCategory model
    businesscategory = relationship("BusinessCategory", back_populates="businesstype")

    