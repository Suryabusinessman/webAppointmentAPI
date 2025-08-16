from fastapi import APIRouter, HTTPException, Depends, status, Header
from sqlalchemy.orm import Session
from app.schemas.LocationModules.locationmaster import LocationMasterCreate, LocationMasterUpdate
from app.services.LocationModules.locationmaster import LocationMasterService
from app.repositories.LocationModules.locationmaster import LocationMasterRepository
from app.core.database import get_db
from dotenv import load_dotenv
import os

load_dotenv()
SECURITY_KEY = os.getenv("SECRET_KEY")  

router = APIRouter()

def validate_security_key(provided_key: str):
    """Validate the security key for API access."""
    if provided_key != SECURITY_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid security key."
        )
    
@router.get("/all-locationmaster", response_model=dict)
def get_all_locations(
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Fetch all locations.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = LocationMasterService(LocationMasterRepository(db), SECURITY_KEY)
    locations = service.get_all_locations(security_key)
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
@router.get("/locationmaster/{location_id}", response_model=dict)
def get_location(
    location_id: int,
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Fetch a location by its ID.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = LocationMasterService(LocationMasterRepository(db), SECURITY_KEY)
    location = service.get_location_by_id(location_id, security_key)
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
    db: Session = Depends(get_db),
    security_key: str = Header(None),  # Accept security key in the request headers
    # added_by: int = 1  # Placeholder for user ID, replace with actual user ID from authentication
):
    """
    Create a new location.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = LocationMasterService(LocationMasterRepository(db), SECURITY_KEY)
    new_location = service.create_location(location_data, security_key, added_by=1)
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
    db: Session = Depends(get_db),
    security_key: str = Header(None),  # Accept security key in the request headers
    # modified_by: int = 1  # Placeholder for user ID, replace with actual user ID from authentication
):
    """
    Update an existing location.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = LocationMasterService(LocationMasterRepository(db), SECURITY_KEY)
    updated_location = service.update_location(location_id, location_data, security_key, modified_by=1)
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
    db: Session = Depends(get_db),
    security_key: str = Header(None),  # Accept security key in the request headers
    # deleted_by: int = 1  # Placeholder for user ID, replace with actual user ID from authentication
):
    """
    Delete a location by its ID.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = LocationMasterService(LocationMasterRepository(db), SECURITY_KEY)
    deleted_location = service.delete_location(location_id, security_key, deleted_by=1)
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