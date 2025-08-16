from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Text, DECIMAL, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base

class BusinessUser(Base):
    __tablename__ = "business_users"

    business_user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    business_type_id = Column(Integer, ForeignKey("business_types.business_type_id"), nullable=False)
    business_name = Column(String(255), nullable=False)
    business_description = Column(Text, nullable=True)
    business_logo = Column(String(500), nullable=True)
    business_banner = Column(String(500), nullable=True)
    business_address = Column(Text, nullable=True)
    business_phone = Column(String(20), nullable=True)
    business_email = Column(String(255), nullable=True)
    business_website = Column(String(255), nullable=True)
    gst_number = Column(String(20), nullable=True)
    pan_number = Column(String(20), nullable=True)
    business_license = Column(String(100), nullable=True)
    
    # Subscription details
    subscription_plan = Column(Enum("FREE", "BASIC", "PREMIUM", "ENTERPRISE"), nullable=True)
    subscription_status = Column(Enum("Active", "Inactive", "Expired", "Suspended"), nullable=True)
    subscription_start_date = Column(DateTime, nullable=True)
    subscription_end_date = Column(DateTime, nullable=True)
    monthly_limit = Column(Integer, default=1000, nullable=True)
    current_month_usage = Column(Integer, default=0, nullable=True)
    
    # Status and ratings
    is_verified = Column(Enum("Y", "N"), default="N", nullable=False)
    is_active = Column(Enum("Y", "N"), default="Y", nullable=False)
    is_featured = Column(Enum("Y", "N"), default="N", nullable=False)
    rating = Column(DECIMAL(3,2), default=0.00, nullable=True)
    total_reviews = Column(Integer, default=0, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="business_users")
    business_type = relationship("BusinessType", back_populates="business_users")
    
    # New relationships for target schema
    audit_logs = relationship("AuditLog", back_populates="business_user")
    notifications = relationship("Notification", back_populates="business_user")
    payment_transactions = relationship("PaymentTransaction", back_populates="business_user")
    
    # Business-specific relationships
    customers = relationship("Customer", back_populates="business_user")
    staff = relationship("Staff", back_populates="business_user")
    rooms = relationship("Room", back_populates="business_user")
    bookings = relationship("Booking", back_populates="business_user")
    patients = relationship("Patient", back_populates="business_user")
    appointments = relationship("Appointment", back_populates="business_user")
    vehicles = relationship("Vehicle", back_populates="business_user")
    services = relationship("Service", back_populates="business_user")
    garage_bookings = relationship("GarageBooking", back_populates="business_user")
    menu_items = relationship("MenuItem", back_populates="business_user")
    catering_orders = relationship("CateringOrder", back_populates="business_user")