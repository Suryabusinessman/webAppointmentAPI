from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base

class LocationMaster(Base):
    __tablename__ = 'location_master'

    location_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    location_name = Column(String(100), unique=True, index=True, nullable=False)
    location_city_name = Column(String(100), nullable=False)
    location_dist_name = Column(String(100), nullable=False)
    location_state_name = Column(String(100), nullable=False)
    location_country_name = Column(String(100), nullable=False)
    location_desc = Column(String(255), nullable=True)
    is_active = Column(Enum("Y", "N"), nullable=False, default="Y")
    
    added_by = Column(Integer, nullable=True)
    added_on = Column(DateTime, server_default=func.now(), nullable=False)
    modified_by = Column(Integer, nullable=True)
    modified_on = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_by = Column(Integer, nullable=True)
    deleted_on = Column(DateTime, nullable=True)
    is_deleted = Column(Enum("Y", "N"), nullable=False, default="N")

    location_active_pincodes = relationship("LocationActivePincode", back_populates="location_master")
    location_user_addresses = relationship("LocationUserAddress", back_populates="location_master")