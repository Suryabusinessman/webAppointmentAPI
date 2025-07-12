# models/user_permission.py

from sqlalchemy import Column, Integer, CHAR, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class UserPermission(Base):
    __tablename__ = "userpermissions"

    User_Permission_Id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    User_Type_Id = Column(Integer, ForeignKey("usertypes.User_Type_Id"), nullable=False)
    Page_Id = Column(Integer, ForeignKey("pages.Page_Id"), nullable=False)

    Can_View = Column(CHAR(1), default='N', nullable=False)
    Can_Create = Column(CHAR(1), default='N', nullable=False)
    Can_Update = Column(CHAR(1), default='N', nullable=False)
    Can_Delete = Column(CHAR(1), default='N', nullable=False)

    Added_By = Column(Integer, nullable=True)
    Added_On = Column(DateTime, default=datetime.utcnow, nullable=False)
    Modified_By = Column(Integer, nullable=True)
    Modified_On = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    Is_Deleted = Column(CHAR(1), default='N', nullable=False)
    Deleted_By = Column(Integer, nullable=True)
    Deleted_On = Column(DateTime, nullable=True)

    # ✅ Relationships
    page = relationship("Page", back_populates="user_permissions")
    user_type = relationship("UserType", back_populates="user_permissions")
