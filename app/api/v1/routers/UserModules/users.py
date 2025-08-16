from fastapi import APIRouter, HTTPException, status, Depends, Header, Request, Form, File, UploadFile
from sqlalchemy.orm import Session
from typing import Any, Optional
from app.schemas.UserModules.users import (
    UserCreate, UserUpdate, RegisterUser, UserLogin, ForgotPassword, ChangePassword, ProfileUpdate
)
from app.services.UserModules.users import (
    get_all_users,
    get_user_by_id,
    get_users_by_name,
    create_user,
    register_user,
    login_user,
    update_user,
    delete_user,
    forgot_password,
    change_password,
    update_profile,
    activate_user,
    deactivate_user,
    get_active_users,
    get_inactive_users
)
from app.core.database import get_db
from app.services.SecurityModules.security_service import SecurityService
from app.models.SecurityModules.security_events import SecurityEventType
from app.core.config import config
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Define the router
router = APIRouter()

def validate_secret_key(secret_key: str = Header(..., alias="secret-key")):
    """Validate the SECRET_KEY from the request header."""
    if secret_key != config.SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid SECRET_KEY provided."
        )
    return secret_key

def get_device_info_and_ip(request: Request):
    """Extract device information and IP address from the request."""
    # Extract device information from the User-Agent header
    device_info = request.headers.get("User-Agent", "Unknown Device")

    # Extract IP address from X-Forwarded-For or Remote-Addr headers
    ip_address = request.headers.get("X-Forwarded-For")
    if ip_address:
        # X-Forwarded-For may contain multiple IPs, take the first one
        ip_address = ip_address.split(",")[0].strip()
    else:
        ip_address = request.client.host  # Fallback to Remote-Addr

    return device_info, ip_address

def log_security_event(event_type: SecurityEventType, user_id: int = None, ip_address: str = None, 
                      user_agent: str = None, device_fingerprint: str = None, suspicious_score: int = 0,
                      risk_factors: list = None, event_metadata: dict = None, db: Session = None):
    """Helper function to log security events"""
    try:
        if not db:
            db = next(get_db())
        
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            device_fingerprint=device_fingerprint,
            suspicious_score=suspicious_score,
            risk_factors=risk_factors,
            event_metadata=event_metadata,
        )
    except Exception as e:
        logger.error(f"Error logging security event: {str(e)}")

# ---------------------- Get All Users ----------------------

@router.get("/all-users", response_model=Any, status_code=status.HTTP_200_OK)
def get_all_users_request(
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch all users with enhanced security logging.
    """
    try:
        # Extract device info for security logging
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={
                "endpoint": "get_all_users",
                "method": "GET"
            },
            db=db
        )
        
        result = get_all_users(db, secret_key)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting all users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users. Please try again later."
        )

# ---------------------- Get User by ID ----------------------

@router.get("/users/{user_id}", response_model=Any, status_code=status.HTTP_200_OK)
def get_user_by_id_request(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch a user by their ID with enhanced security logging.
    """
    try:
        # Extract device info for security logging
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={
                "endpoint": f"get_user_by_id_{user_id}",
                "method": "GET"
            },
            db=db
        )
        
        result = get_user_by_id(db, user_id, secret_key)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user by ID: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information. Please try again later."
        )

# ---------------------- Get Users by Name ----------------------

@router.get("/users/name/{name}", response_model=Any, status_code=status.HTTP_200_OK)
def get_users_by_name_request(
    name: str,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch users by their name (partial match) with enhanced security logging.
    """
    try:
        # Extract device info for security logging
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={
                "endpoint": f"get_users_by_name_{name}",
                "method": "GET"
            },
            db=db
        )
        
        result = get_users_by_name(db, name, secret_key)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting users by name: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search users by name. Please try again later."
        )

# ---------------------- Create User ----------------------

@router.post("/add-users", response_model=Any, status_code=status.HTTP_201_CREATED)
def create_new_user(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    user_type_id: int = Form(...),
    password: str = Form(...),
    alt_phone: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    social_links: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    occupation: Optional[str] = Form(None),
    company_name: Optional[str] = Form(None),
    gst_number: Optional[str] = Form(None),
    referral_code: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    postal_code: Optional[str] = Form(None),
    preferred_language: Optional[str] = Form(None),
    wallet_balance: Optional[float] = Form(None),
    currency: Optional[str] = Form(None),
    is_wallet_enabled: Optional[str] = Form(None),
    is_verified: str = Form("N"),
    is_active: str = Form("Y"),
    profile_image: Optional[UploadFile] = File(None),
    background_image: Optional[UploadFile] = File(None),
    request: Request = None,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Create a new user with file upload support and enhanced security logging.
    """
    try:
        # Extract device info for security logging
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={
                "endpoint": "create_new_user",
                "method": "POST",
                "email": email,
                "full_name": full_name
            },
            db=db
        )
        
        # Handle file uploads - make them optional and flexible
        profile_image_file = None
        background_image_file = None
        
        # Check if files are actually UploadFile objects
        if profile_image and hasattr(profile_image, 'filename'):
            profile_image_file = profile_image
        if background_image and hasattr(background_image, 'filename'):
            background_image_file = background_image
        
        # Create user data
        user_data = UserCreate(
            full_name=full_name,
            email=email,
            phone=phone,
            user_type_id=user_type_id,
            password=password,
            alt_phone=alt_phone,
            bio=bio,
            website=website,
            social_links=social_links,
            gender=gender,
            occupation=occupation,
            company_name=company_name,
            gst_number=gst_number,
            referral_code=referral_code,
            address=address,
            city=city,
            state=state,
            country=country,
            postal_code=postal_code,
            preferred_language=preferred_language,
            wallet_balance=wallet_balance,
            currency=currency,
            is_wallet_enabled=is_wallet_enabled,
            is_verified=is_verified,
            is_active=is_active
        )
        
        result = create_user(db, user_data, secret_key, profile_image_file, background_image_file)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user. Please check your data and try again."
        )

# ---------------------- Register User ----------------------

@router.post("/users/register", response_model=Any, status_code=status.HTTP_201_CREATED)
def register_new_user(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    password: str = Form(...),
    user_type_id: int = Form(default=1),
    alt_phone: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    postal_code: Optional[str] = Form(None),
    profile_image: Optional[UploadFile] = File(None),
    background_image: Optional[UploadFile] = File(None),
    request: Request = None,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Register a new user with file upload support and enhanced security logging.
    """
    try:
        # Extract device info for security logging
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={
                "endpoint": "register_new_user",
                "method": "POST",
                "email": email,
                "full_name": full_name
            },
            db=db
        )
        
        # Handle file uploads - make them optional and flexible
        profile_image_file = None
        background_image_file = None
        
        # Check if files are actually UploadFile objects
        if profile_image and hasattr(profile_image, 'filename'):
            profile_image_file = profile_image
        if background_image and hasattr(background_image, 'filename'):
            background_image_file = background_image
        
        # Create user data
        user_data = RegisterUser(
            full_name=full_name,
            email=email,
            phone=phone,
            password=password,
            user_type_id=user_type_id,
            alt_phone=alt_phone,
            gender=gender,
            address=address,
            city=city,
            state=state,
            postal_code=postal_code
        )
        
        result = register_user(db, user_data, secret_key, profile_image_file, background_image_file)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user. Please check your data and try again."
        )

# ---------------------- Login User ----------------------

@router.post("/users/login", response_model=Any, status_code=status.HTTP_200_OK)
def login_user_request(
    user_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Login a user with enhanced security logging.
    """
    try:
        # Extract device info for security logging
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={
                "endpoint": "login_user",
                "method": "POST",
                "email": user_data.email
            },
            db=db
        )
        
        result = login_user(db, user_data, secret_key)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please check your credentials and try again."
        )

# ---------------------- Update User ----------------------

@router.put("/update-user/{user_id}", response_model=Any, status_code=status.HTTP_200_OK)
def update_user_request(
    user_id: int,
    full_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    user_type_id: Optional[int] = Form(None),
    alt_phone: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    social_links: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    occupation: Optional[str] = Form(None),
    company_name: Optional[str] = Form(None),
    gst_number: Optional[str] = Form(None),
    referral_code: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    postal_code: Optional[str] = Form(None),
    preferred_language: Optional[str] = Form(None),
    wallet_balance: Optional[float] = Form(None),
    currency: Optional[str] = Form(None),
    is_wallet_enabled: Optional[str] = Form(None),
    is_verified: Optional[str] = Form(None),
    is_active: Optional[str] = Form(None),
    profile_image: Optional[UploadFile] = File(None),
    background_image: Optional[UploadFile] = File(None),
    request: Request = None,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Update an existing user with file upload support and enhanced security logging.
    """
    try:
        # Extract device info for security logging
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={
                "endpoint": f"update_user_{user_id}",
                "method": "PUT"
            },
            db=db
        )
        
        # Handle file uploads - make them optional and flexible
        profile_image_file = None
        background_image_file = None
        
        # Check if files are actually UploadFile objects
        if profile_image and hasattr(profile_image, 'filename'):
            profile_image_file = profile_image
        if background_image and hasattr(background_image, 'filename'):
            background_image_file = background_image
        
        # Create update data
        user_data = UserUpdate(
            full_name=full_name,
            email=email,
            phone=phone,
            user_type_id=user_type_id,
            alt_phone=alt_phone,
            bio=bio,
            website=website,
            social_links=social_links,
            gender=gender,
            occupation=occupation,
            company_name=company_name,
            gst_number=gst_number,
            referral_code=referral_code,
            address=address,
            city=city,
            state=state,
            country=country,
            postal_code=postal_code,
            preferred_language=preferred_language,
            wallet_balance=wallet_balance,
            currency=currency,
            is_wallet_enabled=is_wallet_enabled,
            is_verified=is_verified,
            is_active=is_active
        )
        
        result = update_user(db, user_id, user_data, secret_key, profile_image_file, background_image_file)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user. Please check your data and try again."
        )

# ---------------------- Delete User ----------------------

@router.delete("/delete-users/{user_id}", response_model=Any, status_code=status.HTTP_200_OK)
def delete_user_request(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Delete a user with enhanced security logging.
    """
    try:
        # Extract device info for security logging
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={
                "endpoint": f"delete_user_{user_id}",
                "method": "DELETE"
            },
            db=db
        )
        
        result = delete_user(db, user_id, secret_key)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user. Please try again later."
        )

# ---------------------- Forgot Password ----------------------

@router.post("/users/forgot-password", response_model=Any, status_code=status.HTTP_200_OK)
def forgot_password_request(
    forgot_data: ForgotPassword,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Handle forgot password with enhanced security logging.
    """
    try:
        # Extract device info for security logging
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={
                "endpoint": "forgot_password",
                "method": "POST",
                "email": forgot_data.email
            },
            db=db
        )
        
        result = forgot_password(db, forgot_data, secret_key)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing forgot password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process password reset. Please try again later."
        )

# ---------------------- Change Password ----------------------

@router.put("/users/change-password/{user_id}", response_model=Any, status_code=status.HTTP_200_OK)
def change_password_request(
    user_id: int,
    change_data: ChangePassword,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Change user password with enhanced security logging.
    """
    try:
        # Extract device info for security logging
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={
                "endpoint": f"change_password_{user_id}",
                "method": "PUT"
            },
            db=db
        )
        
        result = change_password(db, user_id, change_data, secret_key)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password. Please check your current password and try again."
        )

# ---------------------- Update Profile ----------------------

@router.put("/users/{user_id}/profile", response_model=Any, status_code=status.HTTP_200_OK)
def update_user_profile(
    user_id: int,
    full_name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    alt_phone: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    social_links: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    occupation: Optional[str] = Form(None),
    company_name: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    postal_code: Optional[str] = Form(None),
    profile_image: Optional[UploadFile] = File(None),
    background_image: Optional[UploadFile] = File(None),
    request: Request = None,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Update user profile with file upload support and enhanced security logging.
    """
    try:
        # Extract device info for security logging
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={
                "endpoint": f"update_profile_{user_id}",
                "method": "PUT"
            },
            db=db
        )
        
        # Handle file uploads - make them optional and flexible
        profile_image_file = None
        background_image_file = None
        
        # Check if files are actually UploadFile objects
        if profile_image and hasattr(profile_image, 'filename'):
            profile_image_file = profile_image
        if background_image and hasattr(background_image, 'filename'):
            background_image_file = background_image
        
        # Create profile data
        profile_data = ProfileUpdate(
            full_name=full_name,
            phone=phone,
            alt_phone=alt_phone,
            bio=bio,
            website=website,
            social_links=social_links,
            gender=gender,
            occupation=occupation,
            company_name=company_name,
            address=address,
            city=city,
            state=state,
            postal_code=postal_code
        )
        
        result = update_profile(db, user_id, profile_data, secret_key, profile_image_file, background_image_file)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile. Please check your data and try again."
        )

# ---------------------- Activate User ----------------------

@router.put("/activate-users/{user_id}", response_model=Any, status_code=status.HTTP_200_OK)
def activate_user_request(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Activate a user with enhanced security logging.
    """
    try:
        # Extract device info for security logging
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={
                "endpoint": f"activate_user_{user_id}",
                "method": "PUT"
            },
            db=db
        )
        
        result = activate_user(db, user_id, secret_key)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate user. Please try again later."
        )

# ---------------------- Deactivate User ----------------------

@router.put("/deactivate-users/{user_id}", response_model=Any, status_code=status.HTTP_200_OK)
def deactivate_user_request(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Deactivate a user with enhanced security logging.
    """
    try:
        # Extract device info for security logging
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={
                "endpoint": f"deactivate_user_{user_id}",
                "method": "PUT"
            },
            db=db
        )
        
        result = deactivate_user(db, user_id, secret_key)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate user. Please try again later."
        )

# ---------------------- Get Active Users ----------------------

@router.get("/active-users", response_model=Any, status_code=status.HTTP_200_OK)
def get_active_users_request(
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Get all active users with enhanced security logging.
    """
    try:
        # Extract device info for security logging
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={
                "endpoint": "get_active_users",
                "method": "GET"
            },
            db=db
        )
        
        result = get_active_users(db, secret_key)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting active users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve active users. Please try again later."
        )

# ---------------------- Get Inactive Users ----------------------

@router.get("/inactive-users", response_model=Any, status_code=status.HTTP_200_OK)
def get_inactive_users_request(
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Get all inactive users with enhanced security logging.
    """
    try:
        # Extract device info for security logging
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={
                "endpoint": "get_inactive_users",
                "method": "GET"
            },
            db=db
        )
        
        result = get_inactive_users(db, secret_key)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting inactive users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve inactive users. Please try again later."
        )
