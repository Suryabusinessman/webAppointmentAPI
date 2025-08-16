from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base

class BusinessCategory(Base):
    __tablename__ = "business_categories"

    business_category_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    business_type_id = Column(Integer, ForeignKey("business_types.business_type_id"), nullable=False)
    business_category_name = Column(String(100), nullable=False)
    business_category_short_name = Column(String(300), nullable=False)
    business_category_code = Column(String(100), nullable=True)
    is_active = Column(Enum("Y", "N"), nullable=False, default="Y")
    business_category_media = Column(String(500), nullable=True)
    icon = Column(String(500), nullable=True)
    business_category_description = Column(Text, nullable=True)

    added_by = Column(Integer, nullable=True)
    added_on = Column(DateTime, server_default=func.now(), nullable=False)
    modified_by = Column(Integer, nullable=True)
    modified_on = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(Enum("Y", "N"), default="N", nullable=False)
    deleted_by = Column(Integer, nullable=True)
    deleted_on = Column(DateTime, nullable=True)

    # ✅ Relationships
    business_type = relationship("BusinessType", back_populates="business_categories")