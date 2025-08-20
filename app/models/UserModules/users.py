from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Text, ForeignKey, DECIMAL, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base
from app.models.UserModules.usertypes import UserType

class User(Base):
    __tablename__ = 'users'

    # Primary key and basic info
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    alt_phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)

    # User classification
    user_type_id = Column(Integer, ForeignKey('user_types.user_type_id'), nullable=False)

    # Profile info
    profile_image = Column(String(500), nullable=True)
    background_image = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    social_links = Column(Text, nullable=True)  # Store as JSON string

    # Personal info
    gender = Column(Enum("Male", "Female", "Other", name="gender_enum"), nullable=True)
    dob = Column(Date, nullable=True)
    occupation = Column(String(100), nullable=True)
    company_name = Column(String(255), nullable=True)
    gst_number = Column(String(20), nullable=True)
    referral_code = Column(String(50), nullable=True)

    # Location
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default="India", nullable=True)
    postal_code = Column(String(20), nullable=True)

    # Preferences and status
    preferred_language = Column(String(50), default='en', nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Enum("Y", "N"), default="N", nullable=False)
    is_deleted = Column(Enum("Y", "N"), default="N", nullable=False)

    # Wallet & payments
    wallet_balance = Column(DECIMAL(10,2), default=0.00, nullable=False)
    currency = Column(String(10), default='INR', nullable=True)
    last_transaction_id = Column(String(100), nullable=True)
    payment_mode = Column(String(50), nullable=True)  # wallet, card, upi, etc.
    is_wallet_enabled = Column(Boolean, default=False, nullable=False)

    # Security fields
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    account_locked_until = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    last_login_ip = Column(String(45), nullable=True)
    security_questions = Column(Text, nullable=True)  # JSON string
    two_factor_enabled = Column(Boolean, default=False, nullable=False)
    two_factor_secret = Column(String(255), nullable=True)
    
    # Password reset fields
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)

    # Audit fields
    added_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    added_on = Column(DateTime, server_default=func.now(), nullable=False)
    modified_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    modified_on = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    deleted_on = Column(DateTime, nullable=True)

    # Relationships
    user_type = relationship("UserType", back_populates="users")
    business_users = relationship("BusinessUser", back_populates="user")
    
    # Session and location tracking (restored)
    sessions = relationship("UserSession", back_populates="user")
    locationuseraddress = relationship("LocationUserAddress", back_populates="user")
    
    # New relationships for target schema
    audit_logs = relationship("AuditLog", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    
    # Security relationships
    security_events = relationship("SecurityEvent", back_populates="user")
    security_sessions = relationship("SecuritySession", back_populates="user")
    security_blocks = relationship("SecurityBlock", foreign_keys="SecurityBlock.user_id", back_populates="user")
    created_blocks = relationship("SecurityBlock", foreign_keys="SecurityBlock.created_by_user_id", back_populates="created_by_user")
    
    # News relationships
    news_posts = relationship("NewsPost", foreign_keys="NewsPost.author_id", back_populates="author")
    added_news_posts = relationship("NewsPost", foreign_keys="NewsPost.added_by", back_populates="added_by_user")
    updated_news_posts = relationship("NewsPost", foreign_keys="NewsPost.updated_by", back_populates="updated_by_user")
    