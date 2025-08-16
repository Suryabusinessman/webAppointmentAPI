from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date

# Patient schemas
class PatientBase(BaseModel):
    full_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_number: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_number: Optional[str] = None
    is_active: Optional[bool] = None

class PatientResponse(PatientBase):
    patient_id: int
    business_user_id: int
    patient_number: Optional[str] = None
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True

# Staff schemas
class StaffBase(BaseModel):
    full_name: str
    designation: Optional[str] = None
    specialization: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    qualification: Optional[str] = None
    experience_years: Optional[int] = None

class StaffCreate(StaffBase):
    pass

class StaffUpdate(BaseModel):
    full_name: Optional[str] = None
    designation: Optional[str] = None
    specialization: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    qualification: Optional[str] = None
    experience_years: Optional[int] = None
    is_active: Optional[bool] = None

class StaffResponse(StaffBase):
    staff_id: int
    business_user_id: int
    staff_number: Optional[str] = None
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True

# Appointment schemas
class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: Optional[date] = None
    appointment_time: Optional[datetime] = None
    appointment_type: str = "Consultation"
    symptoms: Optional[str] = None
    diagnosis: Optional[str] = None
    prescription: Optional[str] = None
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    patient_id: Optional[int] = None
    doctor_id: Optional[int] = None
    appointment_date: Optional[date] = None
    appointment_time: Optional[datetime] = None
    appointment_type: Optional[str] = None
    status: Optional[str] = None
    symptoms: Optional[str] = None
    diagnosis: Optional[str] = None
    prescription: Optional[str] = None
    notes: Optional[str] = None

class AppointmentResponse(AppointmentBase):
    appointment_id: int
    business_user_id: int
    status: str = "Scheduled"
    created_at: datetime

    class Config:
        from_attributes = True 