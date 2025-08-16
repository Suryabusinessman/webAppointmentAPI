from fastapi import APIRouter, HTTPException, Depends, status, Header, Request
from sqlalchemy.orm import Session
from app.schemas.UserModules.usertypes import UserTypeCreate, UserTypeUpdate, UserTypeResponse
from app.services.UserModules.usertypes import UserTypeService
from app.repositories.UserModules.usertypes import UserTypeRepository
from app.core.database import get_db
from app.services.SecurityModules.security_service import SecurityService
from app.models.SecurityModules.security_events import SecurityEventType, SecurityEventSeverity
from app.models.SecurityModules.security_blocks import BlockType, BlockReason
from app.core.security import SecurityManager
from app.core.config import config
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Define the router
router = APIRouter()

# ---------------------- Utility Functions ----------------------

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

# ---------------------- API Endpoints ----------------------

@router.get("/test-headers", response_model=dict)
def test_headers(request: Request):
    """Test endpoint to debug header access"""
    all_headers = dict(request.headers)
    logger.info(f"All headers: {all_headers}")
    
    # Try to get secret-key header
    secret_key = request.headers.get("secret-key")
    logger.info(f"secret-key header: {secret_key}")
    
    return {
        "message": "Header test",
        "all_headers": all_headers,
        "secret_key_found": secret_key is not None,
        "secret_key_value": secret_key
    }

@router.get("/all-usertypes", response_model=dict)
def get_all_user_types(
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch all user types with enhanced security logging.
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
                "endpoint": "get_all_user_types",
                "method": "GET"
            },
            db=db
        )
        
        service = UserTypeService(UserTypeRepository(db), config.SECRET_KEY)
        user_types = service.get_all_user_types(secret_key)
        
        # Convert to standardized response format
        user_types_out = []
        for user_type in user_types["data"]:
            user_type_out = UserTypeResponse.from_orm(user_type)
            user_types_out.append(user_type_out)
        
        return {
            "status": "success",
            "message": "User types retrieved successfully.",
            "data": user_types_out,
            "total_count": len(user_types_out)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_all_user_types: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while retrieving user types."
        )

@router.get("/usertypes/{user_type_id}", response_model=dict)
def get_user_type(
    user_type_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch a user type by its ID with enhanced security logging.
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
                "endpoint": "get_user_type",
                "method": "GET",
                "user_type_id": user_type_id
            },
            db=db
        )
        
        service = UserTypeService(UserTypeRepository(db), config.SECRET_KEY)
        user_type = service.get_user_type_by_id(user_type_id, secret_key)
        
        # Convert to standardized response format
        user_type_out = UserTypeResponse.from_orm(user_type["data"])
        
        return {
            "status": "success",
            "message": f"User type with ID {user_type_id} retrieved successfully.",
            "data": user_type_out
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_user_type: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while retrieving user type."
        )

@router.post("/add-usertypes", response_model=dict)
def create_user_type(
    user_type: UserTypeCreate,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Create a new user type with enhanced security logging.
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
                "endpoint": "create_user_type",
                "method": "POST",
                "user_type_name": user_type.type_name
            },
            db=db
        )
        
        service = UserTypeService(UserTypeRepository(db), config.SECRET_KEY)
        new_user_type = service.create_user_type(user_type, secret_key, added_by=1)
        
        # Convert to standardized response format
        user_type_out = UserTypeResponse.from_orm(new_user_type["data"])
        
        return {
            "status": "success",
            "message": "User type created successfully.",
            "data": user_type_out
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_user_type: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while creating user type."
        )

@router.put("/update-usertypes/{user_type_id}", response_model=dict)
def update_user_type(
    user_type_id: int,
    user_type: UserTypeUpdate,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Update an existing user type with enhanced security logging.
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
                "endpoint": "update_user_type",
                "method": "PUT",
                "user_type_id": user_type_id,
                "user_type_name": user_type.type_name
            },
            db=db
        )
        
        service = UserTypeService(UserTypeRepository(db), config.SECRET_KEY)
        updated_user_type = service.update_user_type(user_type_id, user_type, secret_key, modified_by=1)
        
        # Convert to standardized response format
        user_type_out = UserTypeResponse.from_orm(updated_user_type["data"])
        
        return {
            "status": "success",
            "message": "User type updated successfully.",
            "data": user_type_out
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_user_type: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while updating user type."
        )

@router.delete("/delete-usertypes/{user_type_id}", response_model=dict)
def delete_user_type(
    user_type_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Delete a user type with enhanced security logging.
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
                "endpoint": "delete_user_type",
                "method": "DELETE",
                "user_type_id": user_type_id
            },
            db=db
        )
        
        service = UserTypeService(UserTypeRepository(db), config.SECRET_KEY)
        deleted_user_type = service.delete_user_type(user_type_id, secret_key, deleted_by=1)
        
        # Convert to standardized response format
        user_type_out = UserTypeResponse.from_orm(deleted_user_type["data"])
        
        return {
            "status": "success",
            "message": "User type deleted successfully.",
            "data": user_type_out
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_user_type: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while deleting user type."
        )

@router.put("/activate-usertypes/{user_type_id}", response_model=dict)
def activate_user_type(
    user_type_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Activate a user type with enhanced security logging.
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
                "endpoint": "activate_user_type",
                "method": "PUT",
                "user_type_id": user_type_id
            },
            db=db
        )
        
        service = UserTypeService(UserTypeRepository(db), config.SECRET_KEY)
        activated_user_type = service.activate_user_type(user_type_id, secret_key)
        
        # Convert to standardized response format
        user_type_out = UserTypeResponse.from_orm(activated_user_type["data"])
        
        return {
            "status": "success",
            "message": "User type activated successfully.",
            "data": user_type_out
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in activate_user_type: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while activating user type."
        )

@router.put("/deactivate-usertypes/{user_type_id}", response_model=dict)
def deactivate_user_type(
    user_type_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Deactivate a user type with enhanced security logging.
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
                "endpoint": "deactivate_user_type",
                "method": "PUT",
                "user_type_id": user_type_id
            },
            db=db
        )
        
        service = UserTypeService(UserTypeRepository(db), config.SECRET_KEY)
        deactivated_user_type = service.deactivate_user_type(user_type_id, secret_key)
        
        # Convert to standardized response format
        user_type_out = UserTypeResponse.from_orm(deactivated_user_type["data"])
        
        return {
            "status": "success",
            "message": "User type deactivated successfully.",
            "data": user_type_out
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in deactivate_user_type: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while deactivating user type."
        )

@router.get("/active-usertypes", response_model=dict)
def get_active_user_types(
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch all active user types with enhanced security logging.
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
                "endpoint": "get_active_user_types",
                "method": "GET"
            },
            db=db
        )
        
        service = UserTypeService(UserTypeRepository(db), config.SECRET_KEY)
        user_types = service.get_active_user_types(secret_key)
        
        # Convert to standardized response format
        user_types_out = []
        for user_type in user_types["data"]:
            user_type_out = UserTypeResponse.from_orm(user_type)
            user_types_out.append(user_type_out)
        
        return {
            "status": "success",
            "message": "Active user types retrieved successfully.",
            "data": user_types_out,
            "total_count": len(user_types_out)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_active_user_types: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while retrieving active user types."
        )

@router.get("/inactive-usertypes", response_model=dict)
def get_inactive_user_types(
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch all inactive user types with enhanced security logging.
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
                "endpoint": "get_inactive_user_types",
                "method": "GET"
            },
            db=db
        )
        
        service = UserTypeService(UserTypeRepository(db), config.SECRET_KEY)
        user_types = service.get_inactive_user_types(secret_key)
        
        # Convert to standardized response format
        user_types_out = []
        for user_type in user_types["data"]:
            user_type_out = UserTypeResponse.from_orm(user_type)
            user_types_out.append(user_type_out)
        
        return {
            "status": "success",
            "message": "Inactive user types retrieved successfully.",
            "data": user_types_out,
            "total_count": len(user_types_out)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_inactive_user_types: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while retrieving inactive user types."
        )
