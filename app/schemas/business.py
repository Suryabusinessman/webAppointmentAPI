from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Business User schemas
class BusinessUserBase(BaseModel):
    user_id: int
    user_type_id: int
    business_type_id: int
    brand_name: str
    business_type_name: str

class BusinessUserCreate(BusinessUserBase):
    business_code: Optional[str] = None
    business_status: Optional[str] = None
    business_logo: Optional[str] = None
    business_banner: Optional[str] = None
    business_description: Optional[str] = None

class BusinessUserUpdate(BaseModel):
    brand_name: Optional[str] = None
    business_type_name: Optional[str] = None
    business_code: Optional[str] = None
    business_status: Optional[str] = None
    business_logo: Optional[str] = None
    business_banner: Optional[str] = None
    business_description: Optional[str] = None
    is_active: Optional[bool] = None

class BusinessUserResponse(BusinessUserBase):
    business_user_id: int
    business_code: Optional[str] = None
    business_status: Optional[str] = None
    business_logo: Optional[str] = None
    business_banner: Optional[str] = None
    business_description: Optional[str] = None
    is_active: bool = True
    is_deleted: bool = False
    added_on: datetime
    modified_on: datetime

    class Config:
        from_attributes = True

# Hostel Management schemas
class RoomBase(BaseModel):
    room_number: str
    room_type: str
    capacity: int
    price_per_night: Optional[float] = None
    amenities: Optional[str] = None
    room_status: str = "Available"
    floor_number: Optional[int] = None

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    room_number: Optional[str] = None
    room_type: Optional[str] = None
    capacity: Optional[int] = None
    price_per_night: Optional[float] = None
    amenities: Optional[str] = None
    room_status: Optional[str] = None
    floor_number: Optional[int] = None
    is_active: Optional[bool] = None

class RoomResponse(RoomBase):
    room_id: int
    business_user_id: int
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True

class CustomerBase(BaseModel):
    full_name: str
    phone: str
    email: Optional[str] = None
    id_proof_type: Optional[str] = None
    id_proof_number: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    id_proof_type: Optional[str] = None
    id_proof_number: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None

class CustomerResponse(CustomerBase):
    customer_id: int
    business_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class BookingBase(BaseModel):
    customer_id: int
    room_id: int
    check_in_date: datetime
    check_out_date: datetime
    total_amount: Optional[float] = None
    payment_status: str = "Pending"
    booking_status: str = "Confirmed"
    special_requests: Optional[str] = None

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    check_in_date: Optional[datetime] = None
    check_out_date: Optional[datetime] = None
    total_amount: Optional[float] = None
    payment_status: Optional[str] = None
    booking_status: Optional[str] = None
    special_requests: Optional[str] = None

class BookingResponse(BookingBase):
    booking_id: int
    business_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True 