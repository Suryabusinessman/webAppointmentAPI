from fastapi import APIRouter, HTTPException, Depends, status, Header, Request, Form, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.BusinessModules.businessmanuser import BusinessUserCreate, BusinessUserUpdate, BusinessUserResponse
from app.services.BusinessModules.businessmanuser import BusinessmanUserService
from app.repositories.BusinessModules.businessmanuser import BusinessmanUserRepository
from app.core.database import get_db
from app.services.SecurityModules.security_service import SecurityService
from app.models.SecurityModules.security_events import SecurityEventType, SecurityEventSeverity
from app.models.SecurityModules.security_blocks import BlockType, BlockReason
from app.core.security import SecurityManager
from app.core.config import config
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------- Utility Functions ----------------------

def validate_secret_key(secret_key: str = Header(..., alias="secret-key")):
    """Validate the SECRET_KEY from the request header."""
    if secret_key != config.SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid SECRET_KEY provided."
        )

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

# ---------------------- API Endpoints ----------------------

@router.get("/all-businessmanusers", response_model=dict)
def get_all_businessman_users(
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch all business users with enhanced security logging.
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
                "endpoint": "get_all_businessman_users",
                "method": "GET"
            },
            db=db
        )
        
        service = BusinessmanUserService(BusinessmanUserRepository(db), config.SECRET_KEY)
        result = service.get_all_businessman_users(secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting all business users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/businessmanusers/{businessman_user_id}", response_model=dict)
def get_businessman_user(
    businessman_user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch a business user by its ID with enhanced security logging.
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
                "endpoint": f"get_businessman_user_{businessman_user_id}",
                "method": "GET"
            },
            db=db
        )
        
        service = BusinessmanUserService(BusinessmanUserRepository(db), config.SECRET_KEY)
        result = service.get_businessman_user_by_id(businessman_user_id, secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting business user by ID: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/add-businessmanusers", response_model=dict)
def create_businessman_user(
    user_id: int = Form(...),
    business_type_id: int = Form(...),
    business_name: str = Form(...),
    business_description: Optional[str] = Form(None),
    business_address: Optional[str] = Form(None),
    business_phone: Optional[str] = Form(None),
    business_email: Optional[str] = Form(None),
    business_website: Optional[str] = Form(None),
    gst_number: Optional[str] = Form(None),
    pan_number: Optional[str] = Form(None),
    business_license: Optional[str] = Form(None),
    subscription_plan: str = Form("FREE"),
    subscription_status: str = Form("Active"),
    subscription_start_date: Optional[datetime] = Form(None),
    subscription_end_date: Optional[datetime] = Form(None),
    monthly_limit: Optional[int] = Form(None),
    current_month_usage: int = Form(0),
    is_verified: str = Form("N"),
    is_active: str = Form("Y"),
    is_featured: str = Form("N"),
    rating: float = Form(0.0),
    total_reviews: int = Form(0),
    business_logo: Optional[UploadFile] = File(None),
    business_banner: Optional[UploadFile] = File(None),
    request: Request = None,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Create a new business user with optional file uploads.
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
                "endpoint": "create_businessman_user",
                "method": "POST",
                "business_name": business_name
            },
            db=db
        )
        
        service = BusinessmanUserService(BusinessmanUserRepository(db), config.SECRET_KEY)
        result = service.create_businessman_user(
            user_id=user_id,
            business_type_id=business_type_id,
            business_name=business_name,
            business_description=business_description,
            business_address=business_address,
            business_phone=business_phone,
            business_email=business_email,
            business_website=business_website,
            gst_number=gst_number,
            pan_number=pan_number,
            business_license=business_license,
            subscription_plan=subscription_plan,
            subscription_status=subscription_status,
            subscription_start_date=subscription_start_date,
            subscription_end_date=subscription_end_date,
            monthly_limit=monthly_limit,
            current_month_usage=current_month_usage,
            is_verified=is_verified,
            is_active=is_active,
            is_featured=is_featured,
            rating=rating,
            total_reviews=total_reviews,
            business_logo=business_logo,
            business_banner=business_banner,
            secret_key=secret_key,
            added_by=1  # Replace with actual user ID
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating business user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/add-multiplebusinessmanusers", response_model=dict)
def create_multiple_businessman_users(
    businessman_user_data: List[BusinessUserCreate],
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Create multiple business users with enhanced security logging.
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
                "endpoint": "create_multiple_businessman_users",
                "method": "POST",
                "count": len(businessman_user_data)
            },
            db=db
        )
        
        service = BusinessmanUserService(BusinessmanUserRepository(db), config.SECRET_KEY)
        result = service.create_multiple_businessman_users(
            users_data=businessman_user_data,
            security_key=secret_key,
            added_by=1
        )
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_multiple_businessman_users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while creating business users."
        )

@router.post("/add-businessmanusers-multiple", response_model=dict)
def create_multiple_business_users_by_types(
    user_id: int = Form(...),
    business_type_ids: str = Form(...),  # Will be comma-separated string like "1,2,3"
    business_name: str = Form(...),
    business_description: Optional[str] = Form(None),
    business_address: Optional[str] = Form(None),
    business_phone: Optional[str] = Form(None),
    business_email: Optional[str] = Form(None),
    business_website: Optional[str] = Form(None),
    gst_number: Optional[str] = Form(None),
    pan_number: Optional[str] = Form(None),
    business_license: Optional[str] = Form(None),
    subscription_plan: str = Form("FREE"),
    subscription_status: str = Form("Active"),
    subscription_start_date: Optional[datetime] = Form(None),
    subscription_end_date: Optional[datetime] = Form(None),
    monthly_limit: Optional[int] = Form(None),
    current_month_usage: int = Form(0),
    is_verified: str = Form("N"),
    is_active: str = Form("Y"),
    is_featured: str = Form("N"),
    rating: float = Form(0.0),
    total_reviews: int = Form(0),
    business_logo: Optional[UploadFile] = File(None),
    business_banner: Optional[UploadFile] = File(None),
    request: Request = None,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Create multiple business users for multiple business types.
    business_type_ids should be comma-separated string like "1,2,3"
    """
    try:
        # Parse business_type_ids from comma-separated string
        try:
            business_type_ids_list = [int(x.strip()) for x in business_type_ids.split(",")]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid business_type_ids format. Use comma-separated integers like '1,2,3'"
            )

        # Extract device info for security logging
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={
                "endpoint": "create_multiple_business_users_by_types",
                "method": "POST",
                "business_name": business_name,
                "business_type_ids": business_type_ids_list
            },
            db=db
        )
        
        service = BusinessmanUserService(BusinessmanUserRepository(db), config.SECRET_KEY)
        result = service.create_multiple_business_users_by_types(
            user_id=user_id,
            business_type_ids=business_type_ids_list,
            business_name=business_name,
            business_description=business_description,
            business_address=business_address,
            business_phone=business_phone,
            business_email=business_email,
            business_website=business_website,
            gst_number=gst_number,
            pan_number=pan_number,
            business_license=business_license,
            subscription_plan=subscription_plan,
            subscription_status=subscription_status,
            subscription_start_date=subscription_start_date,
            subscription_end_date=subscription_end_date,
            monthly_limit=monthly_limit,
            current_month_usage=current_month_usage,
            is_verified=is_verified,
            is_active=is_active,
            is_featured=is_featured,
            rating=rating,
            total_reviews=total_reviews,
            business_logo=business_logo,
            business_banner=business_banner,
            secret_key=secret_key,
            added_by=1  # Replace with actual user ID
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating multiple business users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/update-businessmanusers/{businessman_user_id}", response_model=dict)
def update_businessman_user(
    businessman_user_id: int,
    user_id: Optional[int] = Form(None),
    business_type_id: Optional[int] = Form(None),
    business_name: Optional[str] = Form(None),
    business_description: Optional[str] = Form(None),
    business_address: Optional[str] = Form(None),
    business_phone: Optional[str] = Form(None),
    business_email: Optional[str] = Form(None),
    business_website: Optional[str] = Form(None),
    gst_number: Optional[str] = Form(None),
    pan_number: Optional[str] = Form(None),
    business_license: Optional[str] = Form(None),
    subscription_plan: Optional[str] = Form(None),
    subscription_status: Optional[str] = Form(None),
    subscription_start_date: Optional[datetime] = Form(None),
    subscription_end_date: Optional[datetime] = Form(None),
    monthly_limit: Optional[int] = Form(None),
    current_month_usage: Optional[int] = Form(None),
    is_verified: Optional[str] = Form(None),
    is_active: Optional[str] = Form(None),
    is_featured: Optional[str] = Form(None),
    rating: Optional[float] = Form(None),
    total_reviews: Optional[int] = Form(None),
    business_logo: Optional[UploadFile] = File(None),
    business_banner: Optional[UploadFile] = File(None),
    request: Request = None,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Update an existing business user with optional file uploads.
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
                "endpoint": f"update_businessman_user_{businessman_user_id}",
                "method": "PUT",
                "business_name": business_name if business_name else "unchanged"
            },
            db=db
        )
        
        service = BusinessmanUserService(BusinessmanUserRepository(db), config.SECRET_KEY)
        result = service.update_businessman_user(
            businessman_user_id=businessman_user_id,
            user_id=user_id,
            business_type_id=business_type_id,
            business_name=business_name,
            business_description=business_description,
            business_address=business_address,
            business_phone=business_phone,
            business_email=business_email,
            business_website=business_website,
            gst_number=gst_number,
            pan_number=pan_number,
            business_license=business_license,
            subscription_plan=subscription_plan,
            subscription_status=subscription_status,
            subscription_start_date=subscription_start_date,
            subscription_end_date=subscription_end_date,
            monthly_limit=monthly_limit,
            current_month_usage=current_month_usage,
            is_verified=is_verified,
            is_active=is_active,
            is_featured=is_featured,
            rating=rating,
            total_reviews=total_reviews,
            business_logo=business_logo,
            business_banner=business_banner,
            secret_key=secret_key,
            updated_by=1  # Replace with actual user ID
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating business user: {str(e)}")
        # Check if it's a database connection error
        if "Can't connect to MySQL server" in str(e) or "Connection refused" in str(e):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection failed. Please ensure MySQL server is running."
            )
        elif "Access denied" in str(e):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database access denied. Please check database credentials."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update business user: {str(e)}"
            )

@router.delete("/delete-businessmanusers/{businessman_user_id}", response_model=dict)
def delete_businessman_user(
    businessman_user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Delete a business user with enhanced security logging.
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
                "endpoint": f"delete_businessman_user_{businessman_user_id}",
                "method": "DELETE"
            },
            db=db
        )
        
        service = BusinessmanUserService(BusinessmanUserRepository(db), config.SECRET_KEY)
        result = service.delete_businessman_user(businessman_user_id, secret_key, deleted_by=1)  # Replace with actual user ID
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting business user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/activate-businessmanusers/{businessman_user_id}", response_model=dict)
def activate_businessman_user(
    businessman_user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Activate a business user.
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
                "endpoint": f"activate_businessman_user_{businessman_user_id}",
                "method": "PUT"
            },
            db=db
        )
        
        service = BusinessmanUserService(BusinessmanUserRepository(db), config.SECRET_KEY)
        result = service.activate_businessman_user(businessman_user_id, secret_key, modified_by=1)  # Replace with actual user ID
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating business user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/deactivate-businessmanusers/{businessman_user_id}", response_model=dict)
def deactivate_businessman_user(
    businessman_user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Deactivate a business user.
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
                "endpoint": f"deactivate_businessman_user_{businessman_user_id}",
                "method": "PUT"
            },
            db=db
        )
        
        service = BusinessmanUserService(BusinessmanUserRepository(db), config.SECRET_KEY)
        result = service.deactivate_businessman_user(businessman_user_id, secret_key, modified_by=1)  # Replace with actual user ID
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating business user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/verify-businessmanusers/{businessman_user_id}", response_model=dict)
def verify_businessman_user(
    businessman_user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Verify a business user (toggle verification status).
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
                "endpoint": f"verify_businessman_user_{businessman_user_id}",
                "method": "PUT"
            },
            db=db
        )
        
        service = BusinessmanUserService(BusinessmanUserRepository(db), config.SECRET_KEY)
        result = service.verify_businessman_user(businessman_user_id, secret_key, modified_by=1)  # Replace with actual user ID
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying business user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/unverify-businessmanusers/{businessman_user_id}", response_model=dict)
def unverify_businessman_user(
    businessman_user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Unverify a business user (toggle verification status).
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
                "endpoint": f"unverify_businessman_user_{businessman_user_id}",
                "method": "PUT"
            },
            db=db
        )
        
        service = BusinessmanUserService(BusinessmanUserRepository(db), config.SECRET_KEY)
        result = service.unverify_businessman_user(businessman_user_id, secret_key, modified_by=1)  # Replace with actual user ID
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unverifying business user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/feature-businessmanusers/{businessman_user_id}", response_model=dict)
def feature_businessman_user(
    businessman_user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Feature a business user (toggle featured status).
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
                "endpoint": f"feature_businessman_user_{businessman_user_id}",
                "method": "PUT"
            },
            db=db
        )
        
        service = BusinessmanUserService(BusinessmanUserRepository(db), config.SECRET_KEY)
        result = service.feature_businessman_user(businessman_user_id, secret_key, modified_by=1)  # Replace with actual user ID
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error featuring business user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/unfeature-businessmanusers/{businessman_user_id}", response_model=dict)
def unfeature_businessman_user(
    businessman_user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Unfeature a business user (toggle featured status).
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
                "endpoint": f"unfeature_businessman_user_{businessman_user_id}",
                "method": "PUT"
            },
            db=db
        )
        
        service = BusinessmanUserService(BusinessmanUserRepository(db), config.SECRET_KEY)
        result = service.unfeature_businessman_user(businessman_user_id, secret_key, modified_by=1)  # Replace with actual user ID
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unfeaturing business user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/active-businessmanusers", response_model=dict)
def get_active_businessman_users(
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Get all active business users.
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
                "endpoint": "get_active_businessman_users",
                "method": "GET"
            },
            db=db
        )
        
        service = BusinessmanUserService(BusinessmanUserRepository(db), config.SECRET_KEY)
        result = service.get_active_businessman_users(secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting active business users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/inactive-businessmanusers", response_model=dict)
def get_inactive_businessman_users(
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Get all inactive business users.
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
                "endpoint": "get_inactive_businessman_users",
                "method": "GET"
            },
            db=db
        )
        
        service = BusinessmanUserService(BusinessmanUserRepository(db), config.SECRET_KEY)
        result = service.get_inactive_businessman_users(secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting inactive business users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

