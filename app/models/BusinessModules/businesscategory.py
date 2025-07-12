from sqlalchemy import Column,String, Integer, CHAR, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class BusinessCategory(Base):
    __tablename__ = "businesscategories"

    Business_Category_Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Business_Type_Id = Column(Integer, ForeignKey("businesstypes.Business_Type_Id"), nullable=False)
    Business_Category_Name = Column(String(100), nullable=False)
    Business_Category_Short_Name = Column(String(300), nullable=False)
    Business_Category_Code = Column(String(100), nullable=True)
    Is_Active = Column(CHAR(1), nullable=False, default='Y')
    Business_Category_Media = Column(String(500), nullable=True)
    Business_Category_Description = Column(String(500), nullable=True)

    Added_By = Column(Integer, nullable=True)
    Added_On = Column(DateTime, default=datetime.utcnow, nullable=False)
    Modified_By = Column(Integer, nullable=True)
    Modified_On = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    Is_Deleted = Column(CHAR(1), default='N', nullable=False)
    Deleted_By = Column(Integer, nullable=True)
    Deleted_On = Column(DateTime, nullable=True)

    # ✅ Relationships
    businesstype = relationship("BusinessType", back_populates="businesscategory")