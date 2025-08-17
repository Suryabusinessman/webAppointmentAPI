from fastapi import APIRouter, HTTPException, Depends, status, Header, Request
from sqlalchemy.orm import Session
from app.schemas.LocationModules.locationactivepincode import LocationActivePincodeCreate, LocationActivePincodeUpdate
from app.services.LocationModules.locationactivepincode import LocationActivePincodeService
from app.repositories.LocationModules.locationactivepincode import LocationActivePincodeRepository
from app.core.database import get_db
from app.core.config import config
import logging

# Configure logging
logger = logging.getLogger(__name__)

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
    device_info = request.headers.get("User-Agent", "Unknown Device")
    
    # Get IP address
    ip_address = request.headers.get("X-Forwarded-For")
    if ip_address:
        ip_address = ip_address.split(",")[0].strip()
    else:
        ip_address = request.client.host
    
    return device_info, ip_address

@router.get("/all-locationactivepincode", response_model=dict)
def get_all_pincodes(
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch all pincodes (both active and inactive).
    """
    # Extract device info for logging
    device_info, ip_address = get_device_info_and_ip(request)
    
    service = LocationActivePincodeService(LocationActivePincodeRepository(db), config.SECRET_KEY)
    pincodes = service.get_all_pincodes(secret_key)
    return {
        "status": "success",
        "message": "Pincodes retrieved successfully.",
        "data": pincodes["data"]
    }

@router.get("/active-locationactivepincode", response_model=dict)
def get_active_pincodes(
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch all active pincodes.
    """
    # Extract device info for logging
    device_info, ip_address = get_device_info_and_ip(request)
    
    service = LocationActivePincodeService(LocationActivePincodeRepository(db), config.SECRET_KEY)
    active_pincodes = service.get_active_pincodes(secret_key)
    return {
        "status": "success",
        "message": "Active pincodes retrieved successfully.",
        "data": active_pincodes["data"]
    }

@router.get("/inactive-locationactivepincode", response_model=dict)
def get_inactive_pincodes(
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch all inactive pincodes.
    """
    # Extract device info for logging
    device_info, ip_address = get_device_info_and_ip(request)
    
    service = LocationActivePincodeService(LocationActivePincodeRepository(db), config.SECRET_KEY)
    inactive_pincodes = service.get_inactive_pincodes(secret_key)
    return {
        "status": "success",
        "message": "Inactive pincodes retrieved successfully.",
        "data": inactive_pincodes["data"]
    }

@router.get("/locationactivepincode/{pincode_id}", response_model=dict)
def get_pincode_by_id(
    pincode_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch a pincode by its ID.
    """
    # Extract device info for logging
    device_info, ip_address = get_device_info_and_ip(request)
    
    service = LocationActivePincodeService(LocationActivePincodeRepository(db), config.SECRET_KEY)
    pincode = service.get_pincode_by_id(pincode_id, secret_key)
    return {
        "status": "success",
        "message": "Pincode retrieved successfully.",
        "data": pincode["data"]
    }

@router.post("/add-locationactivepincode", response_model=dict)
def create_pincode(
    pincode_data: LocationActivePincodeCreate,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key),
    # added_by: int = 1  # Assuming a default user ID for demonstration purposes
):
    """
    Create a new pincode.
    """
    # Extract device info for logging
    device_info, ip_address = get_device_info_and_ip(request)
    
    service = LocationActivePincodeService(LocationActivePincodeRepository(db), config.SECRET_KEY)
    new_pincode = service.create_pincode(pincode_data, secret_key, added_by=1)
    return {
        "status": "success",
        "message": "Pincode created successfully.",
        "data": new_pincode["data"]
    }

@router.put("/update-locationactivepincode/{pincode_id}", response_model=dict)
def update_pincode(
    pincode_id: int,
    pincode_data: LocationActivePincodeUpdate,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key),
    # modified_by: int = 1  # Assuming a default user ID for demonstration purposes
):
    """
    Update an existing pincode.
    """
    # Extract device info for logging
    device_info, ip_address = get_device_info_and_ip(request)
    
    service = LocationActivePincodeService(LocationActivePincodeRepository(db), config.SECRET_KEY)
    updated_pincode = service.update_pincode(pincode_id, pincode_data, secret_key, modified_by=1)
    return {
        "status": "success",
        "message": "Pincode updated successfully.",
        "data": updated_pincode["data"]
    }

@router.delete("/delete-locationactivepincode/{pincode_id}", response_model=dict)
def delete_pincode(
    pincode_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key),
    # deleted_by: int = 1  # Assuming a default user ID for demonstration purposes
):
    """
    Delete a pincode by its ID.
    """
    # Extract device info for logging
    device_info, ip_address = get_device_info_and_ip(request)
    
    service = LocationActivePincodeService(LocationActivePincodeRepository(db), config.SECRET_KEY)
    deleted_pincode = service.delete_pincode(pincode_id, secret_key, deleted_by=1)
    return {
        "status": "success",
        "message": "Pincode deleted successfully.",
        "data": deleted_pincode["data"]
    }

@router.patch("/toggle-locationactivepincode-status/{pincode_id}", response_model=dict)
def toggle_pincode_status(
    pincode_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key),
    # modified_by: int = 1  # Assuming a default user ID for demonstration purposes
):
    """
    Toggle the active status of a pincode.
    """
    # Extract device info for logging
    device_info, ip_address = get_device_info_and_ip(request)
    
    service = LocationActivePincodeService(LocationActivePincodeRepository(db), config.SECRET_KEY)
    updated_pincode = service.toggle_pincode_status(pincode_id, secret_key, modified_by=1)
    return {
        "status": "success",
        "message": "Pincode status toggled successfully.",
        "data": updated_pincode["data"]
    }