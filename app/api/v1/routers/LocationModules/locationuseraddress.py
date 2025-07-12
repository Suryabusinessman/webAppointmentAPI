from fastapi import APIRouter, HTTPException, Depends, status, Header
from sqlalchemy.orm import Session
from app.schemas.LocationModules.locationuseraddress import LocationUserAddressCreate, LocationUserAddressUpdate
from app.services.LocationModules.locationuseraddress import LocationUserAddressService
from app.repositories.LocationModules.locationuseraddress import LocationUserAddressRepository
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

@router.get("/locationuseraddress", response_model=dict)
def get_all_user_addresses(
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Fetch all user addresses.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = LocationUserAddressService(LocationUserAddressRepository(db), SECURITY_KEY)
    addresses = service.get_all_user_addresses(security_key)
    if not addresses["data"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user addresses found."
        )
    return {
        "status": "success",
        "message": "User addresses retrieved successfully.",
        "data": addresses["data"]
    }

@router.get("/locationuseraddress/{address_id}", response_model=dict)
def get_user_address(
    address_id: int,
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Fetch a user address by its ID.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = LocationUserAddressService(LocationUserAddressRepository(db), SECURITY_KEY)
    address = service.get_user_address_by_id(address_id, security_key)
    if not address["data"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User address with ID {address_id} not found."
        )
    return {
        "status": "success",
        "message": "User address retrieved successfully.",
        "data": address["data"]
    }

@router.post("/locationuseraddress", response_model=dict)
def create_user_address(
    address_data: LocationUserAddressCreate,
    db: Session = Depends(get_db),
    security_key: str = Header(None),  # Accept security key in the request headers
    # added_by: int = 1  # Example user ID for the creator
):
    """
    Create a new user address.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = LocationUserAddressService(LocationUserAddressRepository(db), SECURITY_KEY)
    new_address = service.create_user_address(address_data, security_key, added_by=1)
    if not new_address["data"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user address."
        )
    return {
        "status": "success",
        "message": "User address created successfully.",
        "data": new_address["data"]
    }

@router.put("/locationuseraddress/{address_id}", response_model=dict)
def update_user_address(
    address_id: int,
    address_data: LocationUserAddressUpdate,
    db: Session = Depends(get_db),
    security_key: str = Header(None),  # Accept security key in the request headers
    # modified_by: int = 1  # Example user ID for the modifier
):
    """
    Update an existing user address.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = LocationUserAddressService(LocationUserAddressRepository(db), SECURITY_KEY)
    updated_address = service.update_user_address(address_id, address_data, security_key, modified_by=1)
    if not updated_address["data"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user address."
        )
    return {
        "status": "success",
        "message": "User address updated successfully.",
        "data": updated_address["data"]
    }

@router.delete("/locationuseraddress/{address_id}", response_model=dict)
def delete_user_address(
    address_id: int,
    db: Session = Depends(get_db),
    security_key: str = Header(None),  # Accept security key in the request headers
    # deleted_by: int = 1  # Example user ID for the deleter
):
    """
    Delete a user address by its ID.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = LocationUserAddressService(LocationUserAddressRepository(db), SECURITY_KEY)
    deleted_address = service.delete_user_address(address_id, security_key, deleted_by=1)
    if not deleted_address["data"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User address with ID {address_id} not found."
        )
    return {
        "status": "success",
        "message": "User address deleted successfully.",
        "data": deleted_address["data"]
    }