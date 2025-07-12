from fastapi import APIRouter, HTTPException, Depends, status, Header
from sqlalchemy.orm import Session
from app.schemas.LocationModules.locationactivepincode import LocationActivePincodeCreate, LocationActivePincodeUpdate
from app.services.LocationModules.locationactivepincode import LocationActivePincodeService
from app.repositories.LocationModules.locationactivepincode import LocationActivePincodeRepository
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

@router.get("/all-locationactivepincode", response_model=dict)
def get_all_active_pincodes(
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Fetch all active pincodes.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = LocationActivePincodeService(LocationActivePincodeRepository(db), SECURITY_KEY)
    location_active_pincodes = service.get_all_active_pincodes(security_key)
    if not location_active_pincodes["data"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active pincodes found."
        )
    return {
        "status": "success",
        "message": "Active pincodes retrieved successfully.",
        "data": location_active_pincodes["data"]
    }

@router.get("/locationactivepincode/{location_id}", response_model=dict)
def get_location_active_pincode(
    location_id: int,
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Fetch an active pincode by its ID.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = LocationActivePincodeService(LocationActivePincodeRepository(db), SECURITY_KEY)
    location_active_pincode = service.get_active_pincode_by_id(location_id, security_key)
    if not location_active_pincode["data"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active pincode not found."
        )
    return {
        "status": "success",
        "message": "Active pincode retrieved successfully.",
        "data": location_active_pincode["data"]
    }
@router.post("/add-locationactivepincode", response_model=dict)
def create_location_active_pincode(
    pincode_data: LocationActivePincodeCreate,
    db: Session = Depends(get_db),
    security_key: str = Header(None),  # Accept security key in the request headers
    # added_by: int = 1  # Assuming a default user ID for demonstration purposes
):
    """
    Create a new active pincode.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = LocationActivePincodeService(LocationActivePincodeRepository(db), SECURITY_KEY)
    location_active_pincode = service.create_active_pincode(pincode_data, security_key, added_by=1)

    return {
        "status": "success",
        "message": "Active pincode created successfully.",
        "data": location_active_pincode["data"]
    }

@router.put("/update-locationactivepincode/{location_id}", response_model=dict)
def update_location_active_pincode(
    location_id: int,
    pincode_data: LocationActivePincodeUpdate,
    db: Session = Depends(get_db),
    security_key: str = Header(None),  # Accept security key in the request headers
    # modified_by: int = 1  # Assuming a default user ID for demonstration purposes
):
    """
    Update an existing active pincode.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = LocationActivePincodeService(LocationActivePincodeRepository(db), SECURITY_KEY)
    location_active_pincode = service.update_active_pincode(location_id, pincode_data, security_key, modified_by=1)
    if not location_active_pincode["data"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update active pincode."
        )
    return {
        "status": "success",
        "message": "Active pincode updated successfully.",
        "data": location_active_pincode["data"]
    }

@router.delete("/delete-locationactivepincode/{location_id}", response_model=dict)
def delete_location_active_pincode(
    location_id: int,
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Delete an active pincode by its ID.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = LocationActivePincodeService(LocationActivePincodeRepository(db), SECURITY_KEY)
    location_active_pincode = service.delete_active_pincode(location_id, security_key,deleted_by=1)
    if not location_active_pincode["data"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active pincode not found."
        )
    return {
        "status": "success",
        "message": "Active pincode deleted successfully.",
        "data": location_active_pincode["data"]
    }