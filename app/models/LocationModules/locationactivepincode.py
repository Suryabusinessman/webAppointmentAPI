from sqlalchemy import Column, Integer, String, CHAR, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class LocationActivePincode(Base):
    __tablename__ = 'locationactivepincode'

    Pincode_Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Pincode = Column(String(10), unique=True, index=True, nullable=False)
    Location_Id = Column(Integer,ForeignKey('locationmaster.Location_Id'), nullable=False)
    Location_Status = Column(String(10), nullable=False)
    Is_Active = Column(CHAR(1), nullable=False, default='Y')
    Added_By = Column(Integer, nullable=True)
    Added_On = Column(DateTime, default=datetime.utcnow, nullable=False)

    Modified_By = Column(Integer, nullable=True)
    Modified_On = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    Deleted_By = Column(Integer, nullable=True)
    Deleted_On = Column(DateTime, default=datetime.utcnow, nullable=True)

    Is_Deleted = Column(CHAR(1), nullable=False, default='N')

    LocationMaster = relationship("LocationMaster", back_populates="LocationActivePincode")
    LocationUserAddress = relationship("LocationUserAddress", back_populates="locationactivepincode")