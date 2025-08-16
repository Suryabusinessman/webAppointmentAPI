from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from sqlalchemy.orm import Session
from app.schemas.UserModules.userpermissions import UserPermissionCreate, UserPermissionUpdate, UserPermissionResponse
from app.services.UserModules.userpermissions import UserPermissionService
from app.repositories.UserModules.userpermissions import UserPermissionRepository
from app.services.SecurityModules.security_service import SecurityService
from app.models.SecurityModules.security_events import SecurityEventType, SecurityEventSeverity
from app.core.database import get_db
from app.core.config import config
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

# ---------------------- Get All User Permissions ----------------------

@router.get("/all-user-permissions", response_model=dict)
def get_all_user_permissions(
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch all user permissions.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": "/all-user-permissions", "method": "GET"}
        )
        
        service = UserPermissionService(UserPermissionRepository(db), config.SECRET_KEY)
        result = service.get_all_user_permissions(secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting all user permissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Get User Permission by ID ----------------------

@router.get("/user-permissions/{user_permission_id}", response_model=dict)
def get_user_permission_by_id(
    user_permission_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch a user permission by its ID.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": f"/user-permissions/{user_permission_id}", "method": "GET"}
        )
        
        service = UserPermissionService(UserPermissionRepository(db), config.SECRET_KEY)
        result = service.get_user_permission_by_id(user_permission_id, secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user permission by ID: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Get User Permissions by User Type ----------------------

@router.get("/user-permissions/by-user-type/{user_type_id}", response_model=dict)
def get_user_permissions_by_user_type(
    user_type_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch all user permissions for a given user type ID.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": f"/user-permissions/by-user-type/{user_type_id}", "method": "GET"}
        )
        
        service = UserPermissionService(UserPermissionRepository(db), config.SECRET_KEY)
        result = service.get_by_user_type(user_type_id, secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user permissions by user type: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Get User Permissions with Pages ----------------------

@router.get("/user-permissions/with-pages/{user_type_id}", response_model=dict)
def get_user_permissions_with_pages(
    user_type_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch all user permissions with their corresponding page names for a given user type ID.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": f"/user-permissions/with-pages/{user_type_id}", "method": "GET"}
        )
        
        service = UserPermissionService(UserPermissionRepository(db), config.SECRET_KEY)
        result = service.get_user_permissions_with_pages(user_type_id, secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user permissions with pages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Create User Permission ----------------------

@router.post("/add-user-permission", response_model=dict)
def create_user_permission(
    user_permission_data: UserPermissionCreate,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Create a new user permission.
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
                "endpoint": "/add-user-permission", 
                "method": "POST",
                "user_type_id": user_permission_data.user_type_id,
                "page_id": user_permission_data.page_id
            }
        )
        
        service = UserPermissionService(UserPermissionRepository(db), config.SECRET_KEY)
        result = service.create_user_permission(user_permission_data, secret_key, added_by=1)  # Replace `1` with the actual user ID
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user permission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Update User Permission ----------------------

@router.put("/update-user-permission/{user_permission_id}", response_model=dict)
def update_user_permission(
    user_permission_id: int,
    user_permission_data: UserPermissionUpdate,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Update an existing user permission.
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
                "endpoint": f"/update-user-permission/{user_permission_id}", 
                "method": "PUT"
            }
        )
        
        service = UserPermissionService(UserPermissionRepository(db), config.SECRET_KEY)
        result = service.update_user_permission(user_permission_id, user_permission_data, secret_key, modified_by=1)  # Replace `1` with the actual user ID
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user permission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Delete User Permission ----------------------

@router.delete("/delete-user-permission/{user_permission_id}", response_model=dict)
def delete_user_permission(
    user_permission_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Delete a user permission by its ID.
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
                "endpoint": f"/delete-user-permission/{user_permission_id}", 
                "method": "DELETE"
            }
        )
        
        service = UserPermissionService(UserPermissionRepository(db), config.SECRET_KEY)
        result = service.delete_user_permission(user_permission_id, secret_key, deleted_by=1)  # Replace `1` with the actual user ID
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user permission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Activate User Permission ----------------------

@router.post("/activate-user-permission/{user_permission_id}", response_model=dict)
def activate_user_permission(
    user_permission_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Activate a user permission.
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
                "endpoint": f"/activate-user-permission/{user_permission_id}", 
                "method": "POST"
            }
        )
        
        service = UserPermissionService(UserPermissionRepository(db), config.SECRET_KEY)
        result = service.activate_user_permission(user_permission_id, secret_key, modified_by=1)  # Replace `1` with the actual user ID
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating user permission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Deactivate User Permission ----------------------

@router.post("/deactivate-user-permission/{user_permission_id}", response_model=dict)
def deactivate_user_permission(
    user_permission_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Deactivate a user permission.
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
                "endpoint": f"/deactivate-user-permission/{user_permission_id}", 
                "method": "POST"
            }
        )
        
        service = UserPermissionService(UserPermissionRepository(db), config.SECRET_KEY)
        result = service.deactivate_user_permission(user_permission_id, secret_key, modified_by=1)  # Replace `1` with the actual user ID
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating user permission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Get Active User Permissions ----------------------

@router.get("/active-user-permissions", response_model=dict)
def get_active_user_permissions(
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Get all active user permissions.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": "/active-user-permissions", "method": "GET"}
        )
        
        service = UserPermissionService(UserPermissionRepository(db), config.SECRET_KEY)
        result = service.get_active_user_permissions(secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting active user permissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Get Inactive User Permissions ----------------------

@router.get("/inactive-user-permissions", response_model=dict)
def get_inactive_user_permissions(
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Get all inactive user permissions.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": "/inactive-user-permissions", "method": "GET"}
        )
        
        service = UserPermissionService(UserPermissionRepository(db), config.SECRET_KEY)
        result = service.get_inactive_user_permissions(secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting inactive user permissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
