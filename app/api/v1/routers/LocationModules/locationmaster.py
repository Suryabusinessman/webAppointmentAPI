from fastapi import APIRouter, HTTPException, Depends, status, Header, Request
from sqlalchemy.orm import Session
from app.schemas.LocationModules.locationmaster import LocationMasterCreate, LocationMasterUpdate
from app.services.LocationModules.locationmaster import LocationMasterService
from app.repositories.LocationModules.locationmaster import LocationMasterRepository
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
    
@router.get("/all-locationmaster", response_model=dict)
def get_all_locations(
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch all locations.
    """
    # Extract device info for logging
    device_info, ip_address = get_device_info_and_ip(request)
    
    service = LocationMasterService(LocationMasterRepository(db), config.SECRET_KEY)
    locations = service.get_all_locations(secret_key)
    if not locations["data"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No locations found."
        )
    return {
        "status": "success",
        "message": "Locations retrieved successfully.",
        "data": locations["data"]
    }

@router.get("/active-locationmaster", response_model=dict)
def get_active_locations(
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch all active locations.
    """
    # Extract device info for logging
    device_info, ip_address = get_device_info_and_ip(request)
    
    service = LocationMasterService(LocationMasterRepository(db), config.SECRET_KEY)
    locations = service.get_active_locations(secret_key)
    if not locations["data"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active locations found."
        )
    return {
        "status": "success",
        "message": "Active locations retrieved successfully.",
        "data": locations["data"]
    }

@router.get("/inactive-locationmaster", response_model=dict)
def get_inactive_locations(
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch all inactive locations.
    """
    # Extract device info for logging
    device_info, ip_address = get_device_info_and_ip(request)
    
    service = LocationMasterService(LocationMasterRepository(db), config.SECRET_KEY)
    locations = service.get_inactive_locations(secret_key)
    if not locations["data"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No inactive locations found."
        )
    return {
        "status": "success",
        "message": "Inactive locations retrieved successfully.",
        "data": locations["data"]
    }

@router.patch("/toggle-locationmaster-status/{location_id}", response_model=dict)
def toggle_location_status(
    location_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key),
    # modified_by: int = 1  # Placeholder for user ID, replace with actual user ID from authentication
):
    """
    Toggle the active status of a location.
    """
    # Extract device info for logging
    device_info, ip_address = get_device_info_and_ip(request)
    
    service = LocationMasterService(LocationMasterRepository(db), config.SECRET_KEY)
    updated_location = service.toggle_location_status(location_id, secret_key, modified_by=1)
    if not updated_location["data"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to toggle location status."
        )
    return {
        "status": "success",
        "message": "Location status toggled successfully.",
        "data": updated_location["data"]
    }

@router.get("/locationmaster/{location_id}", response_model=dict)
def get_location(
    location_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch a location by its ID.
    """
    # Extract device info for logging
    device_info, ip_address = get_device_info_and_ip(request)
    
    service = LocationMasterService(LocationMasterRepository(db), config.SECRET_KEY)
    location = service.get_location_by_id(location_id, secret_key)
    if not location["data"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with ID {location_id} not found."
        )
    return {
        "status": "success",
        "message": "Location retrieved successfully.",
        "data": location["data"]
    }
@router.post("/add-locationmaster", response_model=dict)
def create_location(
    location_data: LocationMasterCreate,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key),
    # added_by: int = 1  # Placeholder for user ID, replace with actual user ID from authentication
):
    """
    Create a new location.
    """
    # Extract device info for logging
    device_info, ip_address = get_device_info_and_ip(request)
    
    service = LocationMasterService(LocationMasterRepository(db), config.SECRET_KEY)
    new_location = service.create_location(location_data, secret_key, added_by=1)
    if not new_location["data"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create location."
        )
    return {
        "status": "success",
        "message": "Location created successfully.",
        "data": new_location["data"]
    }
@router.put("/update-locationmaster/{location_id}", response_model=dict)
def update_location(
    location_id: int,
    location_data: LocationMasterUpdate,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key),
    # modified_by: int = 1  # Placeholder for user ID, replace with actual user ID from authentication
):
    """
    Update an existing location.
    """
    # Extract device info for logging
    device_info, ip_address = get_device_info_and_ip(request)
    
    service = LocationMasterService(LocationMasterRepository(db), config.SECRET_KEY)
    updated_location = service.update_location(location_id, location_data, secret_key, modified_by=1)
    if not updated_location["data"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update location."
        )
    if not updated_location["data"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with ID {location_id} not found."
        )
    return {
        "status": "success",
        "message": "Location updated successfully.",
        "data": updated_location["data"]
    }
@router.delete("/delete-locationmaster/{location_id}", response_model=dict)
def delete_location(
    location_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key),
    # deleted_by: int = 1  # Placeholder for user ID, replace with actual user ID from authentication
):
    """
    Delete a location by its ID.
    """
    # Extract device info for logging
    device_info, ip_address = get_device_info_and_ip(request)
    
    service = LocationMasterService(LocationMasterRepository(db), config.SECRET_KEY)
    deleted_location = service.delete_location(location_id, secret_key, deleted_by=1)
    if not deleted_location["data"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found."
        )
    if not deleted_location["data"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location is already deleted."
        )
    return {
        "status": "success",
        "message": "Location deleted successfully.",
        "data": deleted_location["data"]
    }