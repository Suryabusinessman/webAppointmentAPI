from fastapi import APIRouter, HTTPException, Depends, status, Header
from sqlalchemy.orm import Session
from app.schemas.UserModules.usertypes import UserTypeCreate, UserTypeUpdate
from app.services.UserModules.usertypes import UserTypeService
from app.repositories.UserModules.usertypes import UserTypeRepository
from app.core.database import get_db
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get the security key from the .env file
SECURITY_KEY = os.getenv("SECRET_KEY")

# Define the router
router = APIRouter()

def validate_security_key(provided_key: str):
    """Validate the security key for API access."""
    if provided_key != SECURITY_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid security key."
        )

# ---------------------- Get All User Types ----------------------

@router.get("/all-usertypes", response_model=dict)
def get_all_user_types(
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Fetch all user types.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = UserTypeService(UserTypeRepository(db), SECURITY_KEY)
    user_types = service.get_all_user_types(security_key)
    return {
        "status": "success",
        "message": "User types retrieved successfully.",
        "data": user_types["data"]
    }

# ---------------------- Get User Type by ID ----------------------

@router.get("/usertypes/{user_type_id}", response_model=dict)
def get_user_type(
    user_type_id: int,
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Fetch a user type by its ID.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = UserTypeService(UserTypeRepository(db), SECURITY_KEY)
    user_type = service.get_user_type_by_id(user_type_id, security_key)
    return {
        "status": "success",
        "message": f"User type with ID {user_type_id} retrieved successfully.",
        "data": user_type["data"]
    }

# ---------------------- Create User Type ----------------------

@router.post("/add-usertypes", response_model=dict)
def create_user_type(
    user_type: UserTypeCreate,
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Create a new user type.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = UserTypeService(UserTypeRepository(db), SECURITY_KEY)
    new_user_type = service.create_user_type(user_type, security_key, added_by=1)  # Replace `1` with the actual user ID
    return {
        "status": "success",
        "color":"success",
        "message": "User type created successfully.",
        "data": new_user_type["data"]
    }

# ---------------------- Update User Type ----------------------

@router.put("/update-usertypes/{user_type_id}", response_model=dict)
def update_user_type(
    user_type_id: int,
    user_type: UserTypeUpdate,
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Update an existing user type.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = UserTypeService(UserTypeRepository(db), SECURITY_KEY)
    updated_user_type = service.update_user_type(user_type_id, user_type, security_key, modified_by=1)  # Replace `1` with the actual user ID
    return {
        "status": "success",
        "color":"success",
        "message": f"User type with ID {user_type.User_Type_Name} updated successfully.",
        "data": updated_user_type["data"]
    }

# ---------------------- Delete User Type ----------------------

@router.delete("/delete-usertypes/{user_type_id}", response_model=dict)
def delete_user_type(
    user_type_id: int,
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Delete a user type by its ID.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = UserTypeService(UserTypeRepository(db), SECURITY_KEY)
    service.delete_user_type(user_type_id, security_key, deleted_by=1)  # Replace `1` with the actual user ID
    return {
        "status": "success",
        "color":"success",
        "message": f"User type with ID {user_type_id} deleted successfully."
    }
