from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserStatus(str, Enum):
    ACTIVE = "Y"
    INACTIVE = "N"

class UserType(str, Enum):
    ADMIN = "admin"
    BUSINESS = "business"
    CUSTOMER = "customer"

class UserBase(BaseModel):
    """Base user model"""
    full_name: str = Field(..., description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    phone: Optional[str] = Field(None, description="User's phone number")
    user_type_id: int = Field(..., description="User type ID")
    profile_image: Optional[str] = Field(None, description="Profile image file path")
    background_image: Optional[str] = Field(None, description="Background image file path")
    is_verified: str = Field(default="N", description="Email verification status")
    is_active: str = Field(default="Y", description="Account status")
    alt_phone: Optional[str] = Field(None, description="Alternative phone number")
    bio: Optional[str] = Field(None, description="User bio")
    website: Optional[str] = Field(None, description="User website")
    social_links: Optional[str] = Field(None, description="Social media links")
    gender: Optional[str] = Field(None, description="Gender")
    occupation: Optional[str] = Field(None, description="Occupation")
    company_name: Optional[str] = Field(None, description="Company name")
    gst_number: Optional[str] = Field(None, description="GST number")
    referral_code: Optional[str] = Field(None, description="Referral code")
    address: Optional[str] = Field(None, description="Address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    country: Optional[str] = Field(None, description="Country")
    postal_code: Optional[str] = Field(None, description="Postal code")
    preferred_language: Optional[str] = Field(None, description="Preferred language")
    wallet_balance: Optional[float] = Field(None, description="Wallet balance")
    currency: Optional[str] = Field(None, description="Currency")
    is_wallet_enabled: Optional[str] = Field(None, description="Wallet enabled status")

class UserCreate(UserBase):
    """Create user model"""
    password: str = Field(..., description="User password", min_length=6)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class UserUpdate(BaseModel):
    """Update user model"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    user_type_id: Optional[int] = None
    profile_image: Optional[str] = None
    background_image: Optional[str] = None
    is_verified: Optional[str] = None
    is_active: Optional[str] = None
    alt_phone: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    social_links: Optional[str] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    company_name: Optional[str] = None
    gst_number: Optional[str] = None
    referral_code: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    preferred_language: Optional[str] = None
    wallet_balance: Optional[float] = None
    currency: Optional[str] = None
    is_wallet_enabled: Optional[str] = None

class UserResponse(UserBase):
    """User response model"""
    user_id: int = Field(..., description="User ID")
    added_on: datetime = Field(..., description="Account creation timestamp")
    modified_on: Optional[datetime] = Field(None, description="Last update timestamp")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")

# Enhanced Registration Schemas
class BusinessRegistrationData(BaseModel):
    """Business registration data model"""
    business_name: str = Field(..., description="Business name")
    business_description: Optional[str] = Field(None, description="Business description")
    business_type_ids: List[int] = Field(..., description="List of business type IDs")
    business_phone: Optional[str] = Field(None, description="Business phone number")
    business_email: Optional[str] = Field(None, description="Business email")
    business_address: Optional[str] = Field(None, description="Business address")
    business_website: Optional[str] = Field(None, description="Business website")
    gst_number: Optional[str] = Field(None, description="GST number")
    pan_number: Optional[str] = Field(None, description="PAN number")
    business_license: Optional[str] = Field(None, description="Business license number")

class DynamicRegisterUser(BaseModel):
    """Dynamic user registration model"""
    # Basic user info
    full_name: str = Field(..., description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    phone: Optional[str] = Field(None, description="User's phone number")
    password: str = Field(..., description="User password", min_length=6)
    confirm_password: str = Field(..., description="Confirm password")
    
    # User type selection
    user_type_id: int = Field(..., description="User type ID")
    
    # Dynamic fields based on user type (business data removed for now)
    # business_data: Optional[BusinessRegistrationData] = Field(None, description="Business registration data")
    
    # Additional user fields
    alt_phone: Optional[str] = Field(None, description="Alternative phone number")
    gender: Optional[str] = Field(None, description="Gender")
    address: Optional[str] = Field(None, description="Address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    postal_code: Optional[str] = Field(None, description="Postal code")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v
    
    @validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

    @validator('phone')
    def validate_phone(cls, v):
        if v is None or v == "":
            return v
        digits = ''.join(ch for ch in v if ch.isdigit())
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError('Invalid phone number. Provide 10-15 digits.')
        return v
    
    # @validator('business_data')
    # def validate_business_data(cls, v, values):
    #     if values.get('user_type_id') == 2 and not v:  # Business user type
    #         raise ValueError('Business data is required for business users')
    #     return v

class RegisterUser(BaseModel):
    """User registration model"""
    full_name: str = Field(..., description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    phone: Optional[str] = Field(None, description="User's phone number")
    password: str = Field(..., description="User password", min_length=6)
    user_type_id: int = Field(default=1, description="User type ID")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

    @validator('phone')
    def validate_phone_register(cls, v):
        if v is None or v == "":
            return v
        digits = ''.join(ch for ch in v if ch.isdigit())
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError('Invalid phone number. Provide 10-15 digits.')
        return v

class ChangePassword(BaseModel):
    """Change password model"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., description="New password", min_length=6)
    confirm_password: str = Field(..., description="Confirm new password")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v
    
    @validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class ProfileUpdate(BaseModel):
    """Profile update model"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    profile_image: Optional[str] = None
    background_image: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    social_links: Optional[str] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    company_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None

class ForgotPassword(BaseModel):
    """Forgot password model"""
    email: EmailStr = Field(..., description="User email")

class ResetPassword(BaseModel):
    """Reset password model"""
    email: EmailStr = Field(..., description="User email")
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., description="New password", min_length=6)
    confirm_password: str = Field(..., description="Confirm new password")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v
    
    @validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class UserSession(BaseModel):
    """User session model"""
    user_id: int = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    token: str = Field(..., description="JWT token")
    is_active: bool = Field(default=True, description="Session status")
    created_at: datetime = Field(..., description="Session creation timestamp")
    expires_at: datetime = Field(..., description="Session expiration timestamp")

class UserPermission(BaseModel):
    """User permission model"""
    user_type_id: int = Field(..., description="User type ID")
    page_id: int = Field(..., description="Page ID")
    can_read: bool = Field(default=False, description="Read permission")
    can_create: bool = Field(default=False, description="Create permission")
    can_update: bool = Field(default=False, description="Update permission")
    can_delete: bool = Field(default=False, description="Delete permission")

class UserTypeInfo(BaseModel):
    """User type information model"""
    user_type_id: int = Field(..., description="User type ID")
    type_name: str = Field(..., description="User type name")
    description: Optional[str] = Field(None, description="User type description")
    default_page: Optional[str] = Field(None, description="Default page for user type")
    permissions: Optional[List[str]] = Field(None, description="User type permissions")

class LoginResponse(BaseModel):
    """Login response model"""
    success: bool = Field(..., description="Login success status")
    message: str = Field(..., description="Response message")
    access_token: str = Field(..., description="JWT access token")
    session_id: str = Field(..., description="Session ID")
    user_info: UserResponse = Field(..., description="User information")
    user_type: UserTypeInfo = Field(..., description="User type information")
    permissions: List[str] = Field(..., description="User permissions")

class UserListResponse(BaseModel):
    """User list response model"""
    users: List[UserResponse] = Field(..., description="List of users")
    total_count: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")

class BusinessUserResponse(BaseModel):
    """Business user response model"""
    business_user_id: int = Field(..., description="Business user ID")
    business_name: str = Field(..., description="Business name")
    business_description: Optional[str] = Field(None, description="Business description")
    business_types: List[dict] = Field(..., description="Business types")
    is_verified: str = Field(..., description="Verification status")
    is_featured: str = Field(..., description="Featured status")
    rating: Optional[float] = Field(None, description="Business rating")
    total_reviews: Optional[int] = Field(None, description="Total reviews")
    
    class Config:
        orm_mode = True

class DynamicRegistrationResponse(BaseModel):
    """Dynamic registration response model"""
    user: UserResponse = Field(..., description="User information")
    business_data: Optional[BusinessUserResponse] = Field(None, description="Business data")
    user_type: UserTypeInfo = Field(..., description="User type information")
    permissions: List[str] = Field(..., description="User permissions")
    security_info: dict = Field(..., description="Security information")
    session_info: dict = Field(..., description="Session information")