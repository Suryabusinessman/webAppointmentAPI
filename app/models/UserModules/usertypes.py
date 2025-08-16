from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base
from app.models.UserModules.userpermissions import UserPermission

class UserType(Base):
    __tablename__ = 'user_types'

    user_type_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type_name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    default_page = Column(String(255), nullable=True)  # Added default_page field
    permissions = Column(Text, nullable=True)  # JSON string
    is_active = Column(Enum("Y", "N"), default="Y", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    users = relationship("User", back_populates="user_type")
    user_permissions = relationship("UserPermission", back_populates="user_type")
    