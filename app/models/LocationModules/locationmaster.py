from sqlalchemy import Column, Integer, String, CHAR, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class LocationMaster(Base):
    __tablename__ = 'locationmaster'

    Location_Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Location_Name = Column(String(100), unique=True, index=True, nullable=False)
    Location_City_Name = Column(String(100), nullable=False)
    Location_Dist_Name = Column(String(100), nullable=False)
    Location_State_Name = Column(String(100), nullable=False)
    Location_Country_Name = Column(String(100), nullable=False)
    Location_Desc = Column(String(255), nullable=True)
    Is_Active = Column(CHAR(1), nullable=False, default='Y')
    Added_By = Column(Integer, nullable=True)
    Added_On = Column(DateTime, default=datetime.utcnow, nullable=False)

    Modified_By = Column(Integer, nullable=True)
    Modified_On = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    Deleted_By = Column(Integer, nullable=True)
    Deleted_On = Column(DateTime, default=datetime.utcnow, nullable=True)

    Is_Deleted = Column(CHAR(1), nullable=False, default='N')


    LocationActivePincode = relationship("LocationActivePincode", back_populates="LocationMaster")
    LocationUserAddress = relationship("LocationUserAddress", back_populates="LocationMaster")