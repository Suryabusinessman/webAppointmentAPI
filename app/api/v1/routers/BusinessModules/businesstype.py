from fastapi import APIRouter, Depends, HTTPException, Header, Request, status, Form, File, UploadFile
from sqlalchemy.orm import Session
from app.schemas.BusinessModules.businesstype import BusinessTypeCreate, BusinessTypeUpdate, BusinessTypeResponse
from app.services.BusinessModules.businesstype import BusinessTypeService
from app.repositories.BusinessModules.businesstype import BusinessTypeRepository
from app.services.SecurityModules.security_service import SecurityService
from app.models.SecurityModules.security_events import SecurityEventType, SecurityEventSeverity
from app.core.database import get_db
from app.core.config import config
from typing import Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Define the router
router = APIRouter()

# ---------------------- Utility Function ----------------------

def validate_secret_key(secret_key: str = Header(..., alias="secret-key")):
    """Validate the SECRET_KEY from the request header."""
    if secret_key != config.SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid SECRET_KEY provided."
        )

def get_device_info_and_ip(request: Request):
    """Extract device information and IP address from the request."""
    device_info = request.headers.get("User-Agent", "Unknown Device")
    ip_address = request.headers.get("X-Forwarded-For")
    if ip_address:
        ip_address = ip_address.split(",")[0].strip()
    else:
        ip_address = request.client.host
    return device_info, ip_address

# ---------------------- Get All Business Types ----------------------

@router.get("/all-business-types", response_model=dict)
def get_all_business_types(
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch all business types.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": "/all-business-types", "method": "GET"}
        )
        
        service = BusinessTypeService(BusinessTypeRepository(db), config.SECRET_KEY)
        result = service.get_all_business_types(secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting all business types: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Get Business Type by ID ----------------------

@router.get("/business-types/{business_type_id}", response_model=dict)
def get_business_type_by_id(
    business_type_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch a business type by its ID.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": f"/business-types/{business_type_id}", "method": "GET"}
        )
        
        service = BusinessTypeService(BusinessTypeRepository(db), config.SECRET_KEY)
        result = service.get_business_type_by_id(business_type_id, secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting business type by ID: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Create Business Type ----------------------

@router.post("/add-business-type", response_model=dict)
def create_business_type(
    type_name: str = Form(...),
    description: Optional[str] = Form(None),
    color: Optional[str] = Form(None),
    features: Optional[str] = Form(None),
    is_active: str = Form('Y'),
    business_media: Optional[UploadFile] = File(None),
    icon: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Create a new business type with optional file uploads.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={
                "endpoint": "/add-business-type", 
                "method": "POST",
                "type_name": type_name
            }
        )
        
        service = BusinessTypeService(BusinessTypeRepository(db), config.SECRET_KEY)
        result = service.create_business_type(
            type_name=type_name,
            description=description,
            color=color,
            features=features,
            is_active=is_active,
            business_media=business_media,
            icon=icon,
            secret_key=secret_key,
            added_by=1  # Replace `1` with the actual user ID
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating business type: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Update Business Type ----------------------

@router.put("/update-business-type/{business_type_id}", response_model=dict)
def update_business_type(
    business_type_id: int,
    type_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    color: Optional[str] = Form(None),
    features: Optional[str] = Form(None),
    is_active: Optional[str] = Form(None),
    business_media: Optional[UploadFile] = File(None),
    icon: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Update an existing business type with optional file uploads.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={
                "endpoint": f"/update-business-type/{business_type_id}", 
                "method": "PUT",
                "type_name": type_name if type_name else "unchanged"
            }
        )
        
        service = BusinessTypeService(BusinessTypeRepository(db), config.SECRET_KEY)
        result = service.update_business_type(
            business_type_id=business_type_id,
            type_name=type_name,
            description=description,
            color=color,
            features=features,
            is_active=is_active,
            business_media=business_media,
            icon=icon,
            secret_key=secret_key,
            modified_by=1  # Replace `1` with the actual user ID
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating business type: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Delete Business Type ----------------------

@router.delete("/delete-business-type/{business_type_id}", response_model=dict)
def delete_business_type(
    business_type_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Delete a business type by its ID.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={
                "endpoint": f"/delete-business-type/{business_type_id}", 
                "method": "DELETE"
            }
        )
        
        service = BusinessTypeService(BusinessTypeRepository(db), config.SECRET_KEY)
        result = service.delete_business_type(business_type_id, secret_key, deleted_by=1)  # Replace `1` with the actual user ID
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting business type: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Activate Business Type ----------------------

@router.post("/activate-business-type/{business_type_id}", response_model=dict)
def activate_business_type(
    business_type_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Activate a business type.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={
                "endpoint": f"/activate-business-type/{business_type_id}", 
                "method": "POST"
            }
        )
        
        service = BusinessTypeService(BusinessTypeRepository(db), config.SECRET_KEY)
        result = service.activate_business_type(business_type_id, secret_key, modified_by=1)  # Replace `1` with the actual user ID
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating business type: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Deactivate Business Type ----------------------

@router.post("/deactivate-business-type/{business_type_id}", response_model=dict)
def deactivate_business_type(
    business_type_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Deactivate a business type.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={
                "endpoint": f"/deactivate-business-type/{business_type_id}", 
                "method": "POST"
            }
        )
        
        service = BusinessTypeService(BusinessTypeRepository(db), config.SECRET_KEY)
        result = service.deactivate_business_type(business_type_id, secret_key, modified_by=1)  # Replace `1` with the actual user ID
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating business type: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Get Active Business Types ----------------------

@router.get("/active-business-types", response_model=dict)
def get_active_business_types(
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Get all active business types.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": "/active-business-types", "method": "GET"}
        )
        
        service = BusinessTypeService(BusinessTypeRepository(db), config.SECRET_KEY)
        result = service.get_active_business_types(secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting active business types: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Get Inactive Business Types ----------------------

@router.get("/inactive-business-types", response_model=dict)
def get_inactive_business_types(
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Get all inactive business types.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": "/inactive-business-types", "method": "GET"}
        )
        
        service = BusinessTypeService(BusinessTypeRepository(db), config.SECRET_KEY)
        result = service.get_inactive_business_types(secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting inactive business types: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )