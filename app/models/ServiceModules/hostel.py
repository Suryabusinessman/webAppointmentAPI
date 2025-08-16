from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, DECIMAL, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Room(Base):
    __tablename__ = "rooms"
    
    room_id = Column(Integer, primary_key=True, index=True)
    business_user_id = Column(Integer, ForeignKey("business_users.business_user_id"), nullable=False)
    room_number = Column(String(50), nullable=False)
    room_type = Column(Enum("Single", "Double", "Triple", "Dormitory", "Suite", "Deluxe", name="room_type_enum"))
    capacity = Column(Integer, nullable=False)
    price_per_night = Column(DECIMAL(10,2))
    amenities = Column(JSON)  # JSON string
    room_status = Column(Enum("Available", "Occupied", "Maintenance", "Reserved", "Cleaning", name="room_status_enum"))
    floor_number = Column(Integer)
    room_features = Column(JSON)  # JSON string
    is_active = Column(Enum("Y", "N"), default="Y")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    business_user = relationship("BusinessUser", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room")

class Customer(Base):
    __tablename__ = "customers"
    
    customer_id = Column(Integer, primary_key=True, index=True)
    business_user_id = Column(Integer, ForeignKey("business_users.business_user_id"), nullable=False)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(20), nullable=False)
    id_proof_type = Column(String(50))
    id_proof_number = Column(String(100))
    address = Column(Text)
    emergency_contact = Column(String(20))
    emergency_contact_name = Column(String(255))
    customer_type = Column(Enum("Regular", "VIP", "Student", "Corporate", name="customer_type_enum"))
    total_bookings = Column(Integer, default=0)
    total_spent = Column(DECIMAL(10,2), default=0.00)
    last_visit_date = Column(DateTime)
    is_active = Column(Enum("Y", "N"), default="Y")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    business_user = relationship("BusinessUser", back_populates="customers")
    bookings = relationship("Booking", back_populates="customer")
    payment_transactions = relationship("PaymentTransaction", back_populates="customer")
    vehicles = relationship("Vehicle", back_populates="customer")
    garage_bookings = relationship("GarageBooking", back_populates="customer")
    catering_orders = relationship("CateringOrder", back_populates="customer")

class Booking(Base):
    __tablename__ = "bookings"
    
    booking_id = Column(Integer, primary_key=True, index=True)
    business_user_id = Column(Integer, ForeignKey("business_users.business_user_id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.room_id"), nullable=False)
    booking_number = Column(String(50), unique=True, nullable=False)
    check_in_date = Column(DateTime, nullable=False)
    check_out_date = Column(DateTime, nullable=False)
    check_in_time = Column(DateTime)
    check_out_time = Column(DateTime)
    total_nights = Column(Integer)
    total_amount = Column(DECIMAL(10,2))
    advance_amount = Column(DECIMAL(10,2), default=0.00)
    payment_status = Column(Enum("Pending", "Paid", "Partial", "Refunded", name="payment_status_enum"))
    booking_status = Column(Enum("Confirmed", "Cancelled", "Completed", "No-show", "Checked-in", "Checked-out", name="booking_status_enum"))
    special_requests = Column(Text)
    cancellation_reason = Column(Text)
    cancelled_by = Column(Integer, ForeignKey("users.user_id"))
    cancelled_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    business_user = relationship("BusinessUser", back_populates="bookings")
    customer = relationship("Customer", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
    cancelled_by_user = relationship("User") 