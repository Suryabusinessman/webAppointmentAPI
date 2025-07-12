from sqlalchemy import Column, Integer, String, CHAR, DateTime,ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class LocationUserAddress(Base):
    __tablename__ = 'locationuseraddress'

    User_Address_Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    User_Id = Column(Integer, ForeignKey('users.User_Id'), nullable=False)  # FK to users table
    Location_Id = Column(Integer, ForeignKey('locationmaster.Location_Id'), nullable=False)  # FK to locationmaster table
    Pincode_Id = Column(Integer, ForeignKey('locationactivepincode.Pincode_Id'), nullable=False)  # FK to locationactivepincode table
    Address_Line1 = Column(String(255),unique=True, index=True, nullable=False)
    Address_Line2 = Column(String(255), nullable=True)
    City = Column(String(100), nullable=False)
    Pincode = Column(String(10), nullable=False)
    Longitude = Column(String(20), nullable=False)
    Latitude = Column(String(20), nullable=False)
    Map_Location_Url = Column(String(255), nullable=True)
    Address_Type = Column(String(50), nullable=False)  # e.g., Home, Office, etc.
    Is_Default = Column(CHAR(1), nullable=False, default='N')
    Is_Active = Column(CHAR(1), nullable=False, default='Y')
    Added_By = Column(Integer, nullable=True)
    Added_On = Column(DateTime, default=datetime.utcnow, nullable=False)

    Modified_By = Column(Integer, nullable=True)
    Modified_On = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    Deleted_By = Column(Integer, nullable=True)
    Deleted_On = Column(DateTime, default=datetime.utcnow, nullable=True)

    Is_Deleted = Column(CHAR(1), nullable=False, default='N')

    LocationMaster = relationship("LocationMaster", back_populates="LocationUserAddress")
    locationactivepincode = relationship("LocationActivePincode", back_populates="LocationUserAddress")
    user = relationship("User", back_populates="locationuseraddress")