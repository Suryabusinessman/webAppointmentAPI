# Import all models to ensure they are registered with SQLAlchemy
# This ensures all relationships are properly established

# Import Base first
from app.core.database import Base

# Import User Modules
from app.models.UserModules.users import User
from app.models.UserModules.usertypes import UserType
from app.models.UserModules.userpermissions import UserPermission
from app.models.UserModules.pages import Page
from app.models.UserModules.authmodules import UserSession

# Import Business Modules
from app.models.BusinessModules.businesstype import BusinessType
from app.models.BusinessModules.businesscategory import BusinessCategory

# Import Location Modules
from app.models.LocationModules.locationmaster import LocationMaster
from app.models.LocationModules.locationactivepincode import LocationActivePincode
from app.models.LocationModules.locationuseraddress import LocationUserAddress

# Import Common Models
from app.models.common import AuditLog, Notification, PaymentTransaction, Staff

# Import Service Modules (import these BEFORE BusinessUser)
from app.models.ServiceModules.hostel import Room, Customer, Booking
from app.models.ServiceModules.hospital import Patient, Appointment
from app.models.ServiceModules.garage import Vehicle, Service, GarageBooking
from app.models.ServiceModules.catering import MenuItem, CateringOrder, OrderItem

# Import BusinessUser AFTER Customer model
from app.models.BusinessModules.businessmanuser import BusinessUser

# Import Security Modules
from app.models.SecurityModules.security_events import SecurityEvent, SecurityEventType, SecurityEventSeverity
from app.models.SecurityModules.security_sessions import SecuritySession, SessionStatus
from app.models.SecurityModules.security_blocks import SecurityBlock, BlockType, BlockReason, BlockStatus

# This ensures all models are imported and registered with SQLAlchemy
__all__ = [
    "Base",
    "User", "UserType", "UserPermission", "Page", "UserSession",
    "BusinessType", "BusinessCategory", "BusinessUser",
    "LocationMaster", "LocationActivePincode", "LocationUserAddress",
    "AuditLog", "Notification", "PaymentTransaction", "Staff",
    "Room", "Customer", "Booking",
    "Patient", "Appointment",
    "Vehicle", "Service", "GarageBooking",
    "MenuItem", "CateringOrder", "OrderItem",
    "SecurityEvent", "SecurityEventType", "SecurityEventSeverity",
    "SecuritySession", "SessionStatus",
    "SecurityBlock", "BlockType", "BlockReason", "BlockStatus"
] 