# models/user_permission.py

from sqlalchemy import Column, Integer, CHAR, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base


class UserPermission(Base):
    __tablename__ = "user_permissions"

    user_permission_id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    user_type_id = Column(Integer, ForeignKey("user_types.user_type_id"), nullable=False)
    page_id = Column(Integer, ForeignKey("pages.page_id"), nullable=False)

    can_view = Column(Enum("Y", "N"), default="N", nullable=False)
    can_create = Column(Enum("Y", "N"), default="N", nullable=False)
    can_update = Column(Enum("Y", "N"), default="N", nullable=False)
    can_delete = Column(Enum("Y", "N"), default="N", nullable=False)

    added_by = Column(Integer, nullable=True)
    added_on = Column(DateTime, server_default=func.now(), nullable=False)
    modified_by = Column(Integer, nullable=True)
    modified_on = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(Enum("Y", "N"), default="N", nullable=False)
    deleted_by = Column(Integer, nullable=True)
    deleted_on = Column(DateTime, nullable=True)

    # ✅ Relationships
    page = relationship("Page", back_populates="user_permissions")
    user_type = relationship("UserType", back_populates="user_permissions")
