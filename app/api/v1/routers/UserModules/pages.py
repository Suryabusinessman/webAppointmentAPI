from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from sqlalchemy.orm import Session
from app.schemas.UserModules.pages import PageCreate, PageUpdate, PageResponse
from app.services.UserModules.pages import PageService
from app.repositories.UserModules.pages import PageRepository
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

# ---------------------- Get All Pages ----------------------

@router.get("/all-pages", response_model=dict)
def get_all_pages(
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch all pages.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": "/all-pages", "method": "GET"}
        )
        
        service = PageService(PageRepository(db), config.SECRET_KEY)
        result = service.get_all_pages(secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting all pages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Get Page by ID ----------------------

@router.get("/pages/{page_id}", response_model=dict)
def get_page_by_id(
    page_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch a page by its ID.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": f"/pages/{page_id}", "method": "GET"}
        )
        
        service = PageService(PageRepository(db), config.SECRET_KEY)
        result = service.get_page_by_id(page_id, secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting page by ID: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Create Page ----------------------

@router.post("/add-pages", response_model=dict)
def create_page(
    page_data: PageCreate,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Create a new page.
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
                "endpoint": "/add-pages", 
                "method": "POST",
                "page_name": page_data.page_name
            }
        )
        
        service = PageService(PageRepository(db), config.SECRET_KEY)
        result = service.create_page(page_data, secret_key, added_by=1)  # Replace `1` with the actual user ID
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating page: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Update Page ----------------------

@router.put("/update-pages/{page_id}", response_model=dict)
def update_page(
    page_id: int,
    page_data: PageUpdate,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Update an existing page.
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
                "endpoint": f"/update-pages/{page_id}", 
                "method": "PUT",
                "page_name": page_data.page_name if page_data.page_name else "unchanged"
            }
        )
        
        service = PageService(PageRepository(db), config.SECRET_KEY)
        result = service.update_page(page_id, page_data, secret_key, modified_by=1)  # Replace `1` with the actual user ID
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating page: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Delete Page ----------------------

@router.delete("/delete-pages/{page_id}", response_model=dict)
def delete_page(
    page_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Delete a page by its ID.
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
                "endpoint": f"/delete-pages/{page_id}", 
                "method": "DELETE"
            }
        )
        
        service = PageService(PageRepository(db), config.SECRET_KEY)
        result = service.delete_page(page_id, secret_key, deleted_by=1)  # Replace `1` with the actual user ID
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting page: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Activate Page ----------------------

@router.post("/activate-pages/{page_id}", response_model=dict)
def activate_page(
    page_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Activate a page.
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
                "endpoint": f"/activate-pages/{page_id}", 
                "method": "POST"
            }
        )
        
        service = PageService(PageRepository(db), config.SECRET_KEY)
        result = service.activate_page(page_id, secret_key, modified_by=1)  # Replace `1` with the actual user ID
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating page: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Deactivate Page ----------------------

@router.post("/deactivate-pages/{page_id}", response_model=dict)
def deactivate_page(
    page_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Deactivate a page.
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
                "endpoint": f"/deactivate-pages/{page_id}", 
                "method": "POST"
            }
        )
        
        service = PageService(PageRepository(db), config.SECRET_KEY)
        result = service.deactivate_page(page_id, secret_key, modified_by=1)  # Replace `1` with the actual user ID
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating page: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Get Active Pages ----------------------

@router.get("/active-pages", response_model=dict)
def get_active_pages(
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Get all active pages.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": "/active-pages", "method": "GET"}
        )
        
        service = PageService(PageRepository(db), config.SECRET_KEY)
        result = service.get_active_pages(secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting active pages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Get Inactive Pages ----------------------

@router.get("/inactive-pages", response_model=dict)
def get_inactive_pages(
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Get all inactive pages.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": "/inactive-pages", "method": "GET"}
        )
        
        service = PageService(PageRepository(db), config.SECRET_KEY)
        result = service.get_inactive_pages(secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting inactive pages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
