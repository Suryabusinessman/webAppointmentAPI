from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base

class LocationActivePincode(Base):
    __tablename__ = 'location_active_pincodes'

    pincode_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pincode = Column(String(10), unique=True, index=True, nullable=False)
    location_id = Column(Integer, ForeignKey('location_master.location_id'), nullable=False)
    location_status = Column(String(10), nullable=False)
    is_active = Column(Enum("Y", "N"), nullable=False, default="Y")
    
    added_by = Column(Integer, nullable=True)
    added_on = Column(DateTime, server_default=func.now(), nullable=False)
    modified_by = Column(Integer, nullable=True)
    modified_on = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_by = Column(Integer, nullable=True)
    deleted_on = Column(DateTime, nullable=True)
    is_deleted = Column(Enum("Y", "N"), nullable=False, default="N")

    location_master = relationship("LocationMaster", back_populates="location_active_pincodes")
    location_user_addresses = relationship("LocationUserAddress", back_populates="location_active_pincode")