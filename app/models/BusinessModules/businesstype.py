from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base

class BusinessType(Base):
    __tablename__ = "business_types"

    business_type_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type_name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # Original Business_Media field (restored)
    business_media = Column(String(500), nullable=True)
    
    # New fields for enhanced functionality
    icon = Column(String(100), nullable=True)
    color = Column(String(7), nullable=True)
    features = Column(Text, nullable=True)  # JSON string
    
    is_active = Column(Enum("Y", "N"), default="Y", nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    business_users = relationship("BusinessUser", back_populates="business_type")
    business_categories = relationship("BusinessCategory", back_populates="business_type")

    