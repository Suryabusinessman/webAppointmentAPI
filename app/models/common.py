from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, JSON, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    audit_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    business_user_id = Column(Integer, ForeignKey("business_users.business_user_id"))
    action_type = Column(Enum("CREATE", "UPDATE", "DELETE", "LOGIN", "LOGOUT", "EXPORT", "IMPORT", "PAYMENT", "BOOKING", "CANCELLATION", name="action_type_enum"))
    table_name = Column(String(100))
    record_id = Column(Integer)
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    session_id = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    business_user = relationship("BusinessUser", back_populates="audit_logs")

class Notification(Base):
    __tablename__ = "notifications"
    
    notification_id = Column(Integer, primary_key=True, index=True)
    business_user_id = Column(Integer, ForeignKey("business_users.business_user_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(Enum("INFO", "SUCCESS", "WARNING", "ERROR", "SECURITY", "BOOKING", "PAYMENT", "SYSTEM", "PROMOTION", name="notification_type_enum"))
    priority = Column(Enum("LOW", "MEDIUM", "HIGH", "URGENT"), default="MEDIUM")
    is_read = Column(Enum("Y", "N"), default="N")
    read_at = Column(DateTime)
    action_url = Column(String(500))
    action_data = Column(JSON)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    business_user = relationship("BusinessUser", back_populates="notifications")

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    
    transaction_id = Column(Integer, primary_key=True, index=True)
    business_user_id = Column(Integer, ForeignKey("business_users.business_user_id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    booking_id = Column(Integer, nullable=True)
    transaction_type = Column(Enum("PAYMENT", "REFUND", "WITHDRAWAL", "DEPOSIT", "COMMISSION", name="transaction_type_enum"))
    payment_method = Column(Enum("CASH", "CARD", "UPI", "NET_BANKING", "WALLET", "CHEQUE", "BANK_TRANSFER", name="payment_method_enum"))
    amount = Column(DECIMAL(10,2), nullable=False)
    currency = Column(String(10), default="INR")
    transaction_status = Column(Enum("PENDING", "SUCCESS", "FAILED", "CANCELLED", "REFUNDED", "DISPUTED", name="transaction_status_enum"))
    gateway_transaction_id = Column(String(255))
    gateway_response = Column(JSON)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    business_user = relationship("BusinessUser", back_populates="payment_transactions")
    customer = relationship("Customer", back_populates="payment_transactions")

class Staff(Base):
    __tablename__ = "staff"
    
    staff_id = Column(Integer, primary_key=True, index=True)
    business_user_id = Column(Integer, ForeignKey("business_users.business_user_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    staff_code = Column(String(50), unique=True)
    full_name = Column(String(255), nullable=False)
    designation = Column(String(100))
    department = Column(String(100))
    specialization = Column(String(100))  # For doctors, technicians, etc.
    phone = Column(String(20))
    email = Column(String(255))
    address = Column(Text)
    qualification = Column(String(100))
    experience_years = Column(Integer)
    salary = Column(DECIMAL(10,2))
    joining_date = Column(DateTime)
    work_schedule = Column(JSON)  # JSON string for flexible schedules
    permissions = Column(JSON)  # JSON string for role-based access
    staff_type = Column(Enum("DOCTOR", "NURSE", "TECHNICIAN", "RECEPTIONIST", "MANAGER", "CLEANER", "SECURITY", "COOK", "WAITER", "DRIVER", "GENERAL", name="staff_type_enum"))
    is_active = Column(Enum("Y", "N"), default="Y")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    business_user = relationship("BusinessUser", back_populates="staff")
    user = relationship("User")
    
    # Business-specific relationships
    appointments = relationship("Appointment", back_populates="doctor")
    garage_bookings = relationship("GarageBooking", back_populates="technician") 