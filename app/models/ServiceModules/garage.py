from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, DECIMAL, Date, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    vehicle_id = Column(Integer, primary_key=True, index=True)
    business_user_id = Column(Integer, ForeignKey("business_users.business_user_id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    vehicle_number = Column(String(20), nullable=False)
    vehicle_type = Column(String(50))
    make = Column(String(100))
    model = Column(String(100))
    year = Column(Integer)
    color = Column(String(50))
    engine_number = Column(String(100))
    chassis_number = Column(String(100))
    fuel_type = Column(Enum("Petrol", "Diesel", "Electric", "Hybrid", "CNG", name="fuel_type_enum"))
    registration_date = Column(Date)
    insurance_expiry = Column(Date)
    fitness_expiry = Column(Date)
    vehicle_condition = Column(Text)
    is_active = Column(Enum("Y", "N"), default="Y")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    business_user = relationship("BusinessUser", back_populates="vehicles")
    customer = relationship("Customer", back_populates="vehicles")
    garage_bookings = relationship("GarageBooking", back_populates="vehicle")

class Service(Base):
    __tablename__ = "services"
    
    service_id = Column(Integer, primary_key=True, index=True)
    business_user_id = Column(Integer, ForeignKey("business_users.business_user_id"), nullable=False)
    service_name = Column(String(255), nullable=False)
    service_description = Column(Text)
    service_category = Column(String(100))
    price = Column(DECIMAL(10,2))
    duration_minutes = Column(Integer)
    service_features = Column(JSON)  # JSON string
    is_active = Column(Enum("Y", "N"), default="Y")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    business_user = relationship("BusinessUser", back_populates="services")
    garage_bookings = relationship("GarageBooking", back_populates="service")

class GarageBooking(Base):
    __tablename__ = "garage_bookings"
    
    booking_id = Column(Integer, primary_key=True, index=True)
    business_user_id = Column(Integer, ForeignKey("business_users.business_user_id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.vehicle_id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.service_id"), nullable=False)
    booking_number = Column(String(50), unique=True, nullable=False)
    booking_date = Column(Date)
    booking_time = Column(DateTime)
    estimated_duration = Column(Integer)
    total_amount = Column(DECIMAL(10,2))
    status = Column(Enum("Scheduled", "In Progress", "Completed", "Cancelled", name="garage_booking_status_enum"))
    notes = Column(Text)
    technician_id = Column(Integer, ForeignKey("staff.staff_id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    business_user = relationship("BusinessUser", back_populates="garage_bookings")
    customer = relationship("Customer", back_populates="garage_bookings")
    vehicle = relationship("Vehicle", back_populates="garage_bookings")
    service = relationship("Service", back_populates="garage_bookings")
    technician = relationship("Staff") 