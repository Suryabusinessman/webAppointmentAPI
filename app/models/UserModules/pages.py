from sqlalchemy import Column, Integer, CHAR, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base

class Page(Base):
    __tablename__ = "pages"

    # Primary Key
    page_id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # Unique identifier for the page

    # Page Details
    page_name = Column(String(255), nullable=False, unique=True)  # Unique name for the page
    page_display_text = Column(String(255), nullable=False)  # Display text for the page
    page_navigation_url = Column(Text, nullable=True)  # URL for navigation
    page_parent_id = Column(Integer, nullable=True)  # Parent page ID for hierarchy
    is_internal = Column(Enum("Y", "N"), nullable=False, default="Y")  # Whether the page is internal or external

    # Audit Fields
    added_by = Column(Integer, nullable=True)
    added_on = Column(DateTime, server_default=func.now(), nullable=False)
    modified_by = Column(Integer, nullable=True)
    modified_on = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_by = Column(Integer, nullable=True)
    deleted_on = Column(DateTime, nullable=True)
    is_deleted = Column(Enum("Y", "N"), default="N", nullable=False)

    # Relationships
    # parent_page = relationship("Page", remote_side=[page_id], backref="child_pages")
    user_permissions = relationship("UserPermission", back_populates="page")