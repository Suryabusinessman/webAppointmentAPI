from fastapi import APIRouter, HTTPException, Depends, status, Header, Request, Form, File, UploadFile
from sqlalchemy.orm import Session
from app.schemas.BusinessModules.businesscategories import BusinessCategoryCreate, BusinessCategoryUpdate, BusinessCategoryResponse
from app.services.BusinessModules.businesscategories import BusinessCategoryService
from app.repositories.BusinessModules.businesscategories import BusinessCategoryRepository
from app.core.database import get_db
from app.services.SecurityModules.security_service import SecurityService
from app.models.SecurityModules.security_events import SecurityEventType, SecurityEventSeverity
from app.models.SecurityModules.security_blocks import BlockType, BlockReason
from app.core.security import SecurityManager
from app.core.config import config
from typing import Optional
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

@router.get("/all-businesscategories", response_model=dict)
def get_all_business_categories(
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch all business categories with enhanced security logging.
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
                "endpoint": "get_all_business_categories",
                "method": "GET"
            },
            db=db
        )
        
        service = BusinessCategoryService(BusinessCategoryRepository(db), config.SECRET_KEY)
        result = service.get_all_business_categories(secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting all business categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/businesscategories/{business_category_id}", response_model=dict)
def get_business_category(
    business_category_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch a business category by its ID with enhanced security logging.
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
                "endpoint": f"get_business_category_{business_category_id}",
                "method": "GET"
            },
            db=db
        )
        
        service = BusinessCategoryService(BusinessCategoryRepository(db), config.SECRET_KEY)
        result = service.get_business_category_by_id(business_category_id, secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting business category by ID: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/add-businesscategories", response_model=dict)
def create_business_category(
    business_type_id: int = Form(...),
    business_category_name: str = Form(...),
    business_category_short_name: str = Form(...),
    business_category_code: Optional[str] = Form(None),
    is_active: str = Form('Y'),
    business_category_description: Optional[str] = Form(None),
    business_category_media: Optional[UploadFile] = File(None),
    icon: Optional[UploadFile] = File(None),
    request: Request = None,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Create a new business category with optional file uploads.
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
                "endpoint": "create_business_category",
                "method": "POST",
                "business_category_name": business_category_name
            },
            db=db
        )
        
        service = BusinessCategoryService(BusinessCategoryRepository(db), config.SECRET_KEY)
        result = service.create_business_category(
            business_type_id=business_type_id,
            business_category_name=business_category_name,
            business_category_short_name=business_category_short_name,
            business_category_code=business_category_code,
            is_active=is_active,
            business_category_description=business_category_description,
            business_category_media=business_category_media,
            icon=icon,
            secret_key=secret_key,
            added_by=1  # Replace with actual user ID
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating business category: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/update-businesscategories/{business_category_id}", response_model=dict)
def update_business_category(
    business_category_id: int,
    business_type_id: Optional[int] = Form(None),
    business_category_name: Optional[str] = Form(None),
    business_category_short_name: Optional[str] = Form(None),
    business_category_code: Optional[str] = Form(None),
    is_active: Optional[str] = Form(None),
    business_category_description: Optional[str] = Form(None),
    business_category_media: Optional[UploadFile] = File(None),
    icon: Optional[UploadFile] = File(None),
    request: Request = None,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Update an existing business category with optional file uploads.
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
                "endpoint": f"update_business_category_{business_category_id}",
                "method": "PUT",
                "business_category_name": business_category_name if business_category_name else "unchanged"
            },
            db=db
        )
        
        service = BusinessCategoryService(BusinessCategoryRepository(db), config.SECRET_KEY)
        result = service.update_business_category(
            business_category_id=business_category_id,
            business_type_id=business_type_id,
            business_category_name=business_category_name,
            business_category_short_name=business_category_short_name,
            business_category_code=business_category_code,
            is_active=is_active,
            business_category_description=business_category_description,
            business_category_media=business_category_media,
            icon=icon,
            secret_key=secret_key,
            modified_by=1  # Replace with actual user ID
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating business category: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/delete-businesscategories/{business_category_id}", response_model=dict)
def delete_business_category(
    business_category_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Delete a business category with enhanced security logging.
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
                "endpoint": f"delete_business_category_{business_category_id}",
                "method": "DELETE"
            },
            db=db
        )
        
        service = BusinessCategoryService(BusinessCategoryRepository(db), config.SECRET_KEY)
        result = service.delete_business_category(business_category_id, secret_key, deleted_by=1)  # Replace with actual user ID
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting business category: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/activate-businesscategories/{business_category_id}", response_model=dict)
def activate_business_category(
    business_category_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Activate a business category.
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
                "endpoint": f"activate_business_category_{business_category_id}",
                "method": "PUT"
            },
            db=db
        )
        
        service = BusinessCategoryService(BusinessCategoryRepository(db), config.SECRET_KEY)
        result = service.activate_business_category(business_category_id, secret_key, modified_by=1)  # Replace with actual user ID
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating business category: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/deactivate-businesscategories/{business_category_id}", response_model=dict)
def deactivate_business_category(
    business_category_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Deactivate a business category.
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
                "endpoint": f"deactivate_business_category_{business_category_id}",
                "method": "PUT"
            },
            db=db
        )
        
        service = BusinessCategoryService(BusinessCategoryRepository(db), config.SECRET_KEY)
        result = service.deactivate_business_category(business_category_id, secret_key, modified_by=1)  # Replace with actual user ID
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating business category: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/active-businesscategories", response_model=dict)
def get_active_business_categories(
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Get all active business categories.
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
                "endpoint": "get_active_business_categories",
                "method": "GET"
            },
            db=db
        )
        
        service = BusinessCategoryService(BusinessCategoryRepository(db), config.SECRET_KEY)
        result = service.get_active_business_categories(secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting active business categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/inactive-businesscategories", response_model=dict)
def get_inactive_business_categories(
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Get all inactive business categories.
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
                "endpoint": "get_inactive_business_categories",
                "method": "GET"
            },
            db=db
        )
        
        service = BusinessCategoryService(BusinessCategoryRepository(db), config.SECRET_KEY)
        result = service.get_inactive_business_categories(secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting inactive business categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )