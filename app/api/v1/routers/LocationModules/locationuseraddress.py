from fastapi import APIRouter, HTTPException, Depends, status, Header, Request
from sqlalchemy.orm import Session
from app.schemas.LocationModules.locationuseraddress import LocationUserAddressCreate, LocationUserAddressUpdate
from app.services.LocationModules.locationuseraddress import LocationUserAddressService
from app.repositories.LocationModules.locationuseraddress import LocationUserAddressRepository
from app.core.database import get_db
from app.core.config import config

router = APIRouter()

def validate_secret_key(secret_key: str = Header(..., alias="secret-key")):
    """Validate the secret key for API access."""
    if secret_key != config.SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid secret key."
        )
    return secret_key

def get_device_info_and_ip(request: Request):
    """Extract device information and IP address for security logging."""
    client_host = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    return {"client_host": client_host, "user_agent": user_agent}

@router.get("/all-locationuseraddress", response_model=dict)
def get_all_user_addresses(
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch all user addresses with related information (user names, location names, pincode values).
    """
    # Log device info for security
    device_info = get_device_info_and_ip(request)
    service = LocationUserAddressService(LocationUserAddressRepository(db), config.SECRET_KEY)
    return service.get_all_user_addresses(secret_key)

@router.get("/locationuseraddress", response_model=dict)
def get_all_user_addresses_default(
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Default endpoint for getting all user addresses (alias for /all-locationuseraddress).
    This maintains backward compatibility with existing frontend calls.
    """
    # Log device info for security
    device_info = get_device_info_and_ip(request)
    service = LocationUserAddressService(LocationUserAddressRepository(db), config.SECRET_KEY)
    return service.get_all_user_addresses(secret_key)

@router.get("/locationuseraddress/{address_id}", response_model=dict)
def get_user_address(
    address_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch a user address by its ID with related information.
    """
    # Log device info for security
    device_info = get_device_info_and_ip(request)
    service = LocationUserAddressService(LocationUserAddressRepository(db), config.SECRET_KEY)
    return service.get_user_address_by_id(address_id, secret_key)

@router.post("/add-locationuseraddress", response_model=dict)
def create_user_address(
    address_data: LocationUserAddressCreate,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Create a new user address.
    """
    # Log device info for security
    device_info = get_device_info_and_ip(request)
    service = LocationUserAddressService(LocationUserAddressRepository(db), config.SECRET_KEY)
    # Automatically set added_by to the same user_id from the request
    return service.create_user_address(address_data, secret_key)

@router.post("/locationuseraddress", response_model=dict)
def create_user_address_default(
    address_data: LocationUserAddressCreate,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Default endpoint for creating user addresses (alias for /add-locationuseraddress).
    This maintains backward compatibility with existing frontend calls.
    """
    # Log device info for security
    device_info = get_device_info_and_ip(request)
    service = LocationUserAddressService(LocationUserAddressRepository(db), config.SECRET_KEY)
    # Automatically set added_by to the same user_id from the request
    return service.create_user_address(address_data, secret_key)

@router.put("/update-locationuseraddress/{address_id}", response_model=dict)
def update_user_address(
    address_id: int,
    address_data: LocationUserAddressUpdate,
    modified_by: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Update an existing user address.
    """
    # Log device info for security
    device_info = get_device_info_and_ip(request)
    service = LocationUserAddressService(LocationUserAddressRepository(db), config.SECRET_KEY)
    return service.update_user_address(address_id, address_data, secret_key, modified_by)

@router.put("/locationuseraddress", response_model=dict)
def update_user_address_default(
    address_data: LocationUserAddressUpdate,
    modified_by: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Default endpoint for updating user addresses (alias for /update-locationuseraddress/{address_id}).
    This maintains backward compatibility with existing frontend calls.
    Note: address_id should be included in the request body for this endpoint.
    """
    # Log device info for security
    device_info = get_device_info_and_ip(request)
    service = LocationUserAddressService(LocationUserAddressRepository(db), config.SECRET_KEY)
    
    # Extract address_id from the request body if it exists
    if hasattr(address_data, 'user_address_id') and address_data.user_address_id:
        return service.update_user_address(address_data.user_address_id, address_data, secret_key, modified_by)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_address_id is required in request body for this endpoint"
        )

@router.delete("/delete-locationuseraddress/{address_id}", response_model=dict)
def delete_user_address(
    address_id: int,
    deleted_by: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Delete a user address by its ID.
    """
    # Log device info for security
    device_info = get_device_info_and_ip(request)
    service = LocationUserAddressService(LocationUserAddressRepository(db), config.SECRET_KEY)
    return service.delete_user_address(address_id, secret_key, deleted_by)

@router.delete("/locationuseraddress", response_model=dict)
def delete_user_address_default(
    deleted_by: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Default endpoint for deleting user addresses (alias for /delete-locationuseraddress/{address_id}).
    This maintains backward compatibility with existing frontend calls.
    Note: address_id is required for this endpoint.
    """
    # Log device info for security
    device_info = get_device_info_and_ip(request)
    service = LocationUserAddressService(LocationUserAddressRepository(db), config.SECRET_KEY)
    
    # For DELETE requests, we need to get the address_id from query parameters or request body
    # This is a limitation of the default endpoint approach
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Please use /delete-locationuseraddress/{address_id} endpoint for deletion. address_id is required in the URL path."
    )

@router.get("/active-locationuseraddress", response_model=dict)
def get_active_user_addresses(
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch all active user addresses.
    """
    # Log device info for security
    device_info = get_device_info_and_ip(request)
    service = LocationUserAddressService(LocationUserAddressRepository(db), config.SECRET_KEY)
    return service.get_active_user_addresses(secret_key)

@router.get("/inactive-locationuseraddress", response_model=dict)
def get_inactive_user_addresses(
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch all inactive user addresses.
    """
    # Log device info for security
    device_info = get_device_info_and_ip(request)
    service = LocationUserAddressService(LocationUserAddressRepository(db), config.SECRET_KEY)
    return service.get_inactive_user_addresses(secret_key)

@router.get("/locationuseraddress-by-user/{user_id}", response_model=dict)
def get_user_addresses_by_user_id(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch all addresses for a specific user.
    """
    # Log device info for security
    device_info = get_device_info_and_ip(request)
    service = LocationUserAddressService(LocationUserAddressRepository(db), config.SECRET_KEY)
    return service.get_user_addresses_by_user_id(user_id, secret_key)

@router.patch("/toggle-locationuseraddress-active-status/{address_id}", response_model=dict)
def toggle_user_address_active_status(
    address_id: int,
    modified_by: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Toggle the active status of a user address.
    """
    # Log device info for security
    device_info = get_device_info_and_ip(request)
    service = LocationUserAddressService(LocationUserAddressRepository(db), config.SECRET_KEY)
    return service.toggle_user_address_active_status(address_id, secret_key, modified_by)

@router.patch("/toggle-locationuseraddress-default-status/{address_id}", response_model=dict)
def toggle_user_address_default_status(
    address_id: int,
    modified_by: int,
    request: Request,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Toggle the default status of a user address.
    """
    # Log device info for security
    device_info = get_device_info_and_ip(request)
    service = LocationUserAddressService(LocationUserAddressRepository(db), config.SECRET_KEY)
    return service.toggle_user_address_default_status(address_id, secret_key, modified_by)