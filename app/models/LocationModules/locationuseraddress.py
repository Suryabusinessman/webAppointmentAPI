from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base

class LocationUserAddress(Base):
    __tablename__ = 'location_user_addresses'

    user_address_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)  # FK to users table
    location_id = Column(Integer, ForeignKey('location_master.location_id'), nullable=False)  # FK to locationmaster table
    pincode_id = Column(Integer, ForeignKey('location_active_pincodes.pincode_id'), nullable=False)  # FK to locationactivepincode table
    address_line1 = Column(String(255), unique=True, index=True, nullable=False)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    pincode = Column(String(10), nullable=False)
    longitude = Column(String(20), nullable=False)
    latitude = Column(String(20), nullable=False)
    map_location_url = Column(String(255), nullable=True)
    address_type = Column(String(50), nullable=False)  # e.g., Home, Office, etc.
    is_default = Column(Enum("Y", "N"), nullable=False, default="N")
    is_active = Column(Enum("Y", "N"), nullable=False, default="Y")
    
    added_by = Column(Integer, nullable=True)
    added_on = Column(DateTime, server_default=func.now(), nullable=False)
    modified_by = Column(Integer, nullable=True)
    modified_on = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_by = Column(Integer, nullable=True)
    deleted_on = Column(DateTime, nullable=True)
    is_deleted = Column(Enum("Y", "N"), nullable=False, default="N")

    location_master = relationship("LocationMaster", back_populates="location_user_addresses")
    location_active_pincode = relationship("LocationActivePincode", back_populates="location_user_addresses")
    user = relationship("User", back_populates="locationuseraddress")