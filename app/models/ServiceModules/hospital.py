from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, DECIMAL, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Patient(Base):
    __tablename__ = "patients"
    
    patient_id = Column(Integer, primary_key=True, index=True)
    business_user_id = Column(Integer, ForeignKey("business_users.business_user_id"), nullable=False)
    patient_number = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    date_of_birth = Column(Date)
    gender = Column(Enum("Male", "Female", "Other", name="patient_gender_enum"))
    blood_group = Column(String(10))
    phone = Column(String(20))
    email = Column(String(255))
    address = Column(Text)
    emergency_contact = Column(String(20))
    emergency_contact_name = Column(String(255))
    medical_history = Column(Text)
    allergies = Column(Text)
    insurance_provider = Column(String(100))
    insurance_number = Column(String(100))
    insurance_validity = Column(Date)
    patient_type = Column(Enum("Outpatient", "Inpatient", "Emergency", name="patient_type_enum"))
    is_active = Column(Enum("Y", "N"), default="Y")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    business_user = relationship("BusinessUser", back_populates="patients")
    appointments = relationship("Appointment", back_populates="patient")

class Appointment(Base):
    __tablename__ = "appointments"
    
    appointment_id = Column(Integer, primary_key=True, index=True)
    business_user_id = Column(Integer, ForeignKey("business_users.business_user_id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("staff.staff_id"), nullable=False)
    appointment_number = Column(String(50), unique=True, nullable=False)
    appointment_date = Column(Date)
    appointment_time = Column(DateTime)
    appointment_type = Column(Enum("Consultation", "Follow-up", "Emergency", "Surgery", "Checkup", name="appointment_type_enum"))
    appointment_status = Column(Enum("Scheduled", "Confirmed", "Completed", "Cancelled", "No-show", name="appointment_status_enum"))
    symptoms = Column(Text)
    diagnosis = Column(Text)
    prescription = Column(Text)
    notes = Column(Text)
    consultation_fee = Column(DECIMAL(10,2))
    payment_status = Column(Enum("Pending", "Paid", "Partial", name="payment_status_enum"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    business_user = relationship("BusinessUser", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Staff", back_populates="appointments") 