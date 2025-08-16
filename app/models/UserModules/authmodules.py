from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base

class UserSession(Base):
    __tablename__ = "user_sessions"

    session_id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # Unique identifier for the session
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)  # Specify length for VARCHAR
    device_info = Column(String(255), nullable=True)  # Specify length for VARCHAR
    ip_address = Column(String(45), nullable=True)  # Length for IPv4/IPv6 addresses
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)
    login_timestamp = Column(DateTime, server_default=func.now())
    logout_timestamp = Column(DateTime, nullable=True)

    # Audit fields
    added_by = Column(Integer, nullable=True)
    added_on = Column(DateTime, server_default=func.now(), nullable=False)
    modified_by = Column(Integer, nullable=True)
    modified_on = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_by = Column(Integer, nullable=True)
    deleted_on = Column(DateTime, nullable=True)
    is_deleted = Column(Enum("Y", "N"), default="N", nullable=False)

    # Relationship with the User table
    user = relationship("User", back_populates="sessions")


class EmailOTP(Base):
    __tablename__ = "email_otps"

    otp_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    email = Column(String(255), index=True, nullable=False)
    otp_hash = Column(String(255), nullable=False)
    purpose = Column(String(50), default="EMAIL_VERIFICATION", nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)

    # Optional rate limiting metadata
    last_sent_at = Column(DateTime, nullable=True)
    send_count = Column(Integer, default=0, nullable=False)