from sqlalchemy import Column, Integer,CHAR, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Page(Base):
    __tablename__ = "pages"

    # Primary Key
    Page_Id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # Unique identifier for the page

    # Page Details
    Page_Name = Column(String(255), nullable=False, unique=True)  # Unique name for the page
    Page_Display_Text = Column(String(255), nullable=False)  # Display text for the page
    Page_Navigation_URL = Column(Text, nullable=True)  # URL for navigation
    Page_Parent_Id = Column(Integer, nullable=True)  # Parent page ID for hierarchy
    Is_Internal = Column(CHAR(1), nullable=False, default='Y')  # Whether the page is internal or external

    # Audit Fields
    Added_By = Column(Integer, nullable=True)
    Added_On = Column(DateTime, default=datetime.utcnow, nullable=False)
    Modified_By = Column(Integer, nullable=True)
    Modified_On = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    Deleted_By = Column(Integer, nullable=True)
    Deleted_On = Column(DateTime, nullable=True)
    Is_Deleted = Column(CHAR(1), default='N', nullable=False)

    # Relationships
    # parent_page = relationship("Page", remote_side=[Page_Id], backref="child_pages")
    user_permissions = relationship("UserPermission", back_populates="page")