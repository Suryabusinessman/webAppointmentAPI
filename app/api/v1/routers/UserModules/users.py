from fastapi import APIRouter, HTTPException, status, Depends, Header
from sqlalchemy.orm import Session
from typing import Any
from app.schemas.UserModules.users import (
    UserCreate, RegisterUser, UserLogin, ForgotPassword, ChangePassword, ProfileUpdate
)
from app.services.UserModules.users import (
    get_all_users,
    get_user_by_id,
    get_users_by_name,
    create_user,
    register_user,
    login_user,
    update_user,
    delete_user,
    forgot_password,
    change_password,
    update_profile
)
from app.core.database import get_db
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get the security key from the .env file
SECRET_KEY = os.getenv("SECRET_KEY")

# Define the router
router = APIRouter()

def validate_security_key(provided_key: str):
    """Validate the security key for API access."""
    if provided_key != SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid security key."
        )

# ---------------------- Get All Users ----------------------

@router.get("/all-users", response_model=Any, status_code=status.HTTP_200_OK)
def get_all_users_request(
    db: Session = Depends(get_db),
    security_key: str = Header(None)
):
    """
    Fetch all users without pagination.
    """
    validate_security_key(security_key)
    try:
        users = get_all_users(db, security_key)
        return {"status": "success", "message": "Users retrieved successfully", "data": users}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------------------- Get User by ID ----------------------

@router.get("/users/{user_id}", response_model=Any, status_code=status.HTTP_200_OK)
def get_user_by_id_request(
    user_id: int,
    db: Session = Depends(get_db),
    security_key: str = Header(None)
):
    """
    Fetch a user by their ID.
    """
    validate_security_key(security_key)
    try:
        user = get_user_by_id(db, user_id, security_key)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"status": "success", "message": "User retrieved successfully", "data": user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------------------- Get Users by Name ----------------------

@router.get("/users/name/{name}", response_model=Any, status_code=status.HTTP_200_OK)
def get_users_by_name_request(
    name: str,
    db: Session = Depends(get_db),
    security_key: str = Header(None)
):
    """
    Fetch users by their name (partial match).
    """
    validate_security_key(security_key)
    try:
        users = get_users_by_name(db, name, security_key)
        return {"status": "success", "message": "Users retrieved successfully", "data": users}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------------------- Create User ----------------------

@router.post("/add-users", response_model=Any, status_code=status.HTTP_201_CREATED)
def create_new_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    security_key: str = Header(None)
):
    """
    Create a new user.
    """
    validate_security_key(security_key)
    try:
        user = create_user(db, user_data, security_key)
        return {"status": "success", "message": "User created successfully", "data": user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------------------- Register User ----------------------

@router.post("/users/register", response_model=Any, status_code=status.HTTP_201_CREATED)
def register_new_user(
    user_data: RegisterUser,
    db: Session = Depends(get_db),
    security_key: str = Header(None)
):
    """
    Register a new user.
    """
    validate_security_key(security_key)
    try:
        user = register_user(db, user_data, security_key)
        return {"status": "success", "message": "User registered successfully", "data": user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------------------- Login User ----------------------

@router.post("/users/login", response_model=Any, status_code=status.HTTP_200_OK)
def login_user_request(
    user_data: UserLogin,
    db: Session = Depends(get_db),
    security_key: str = Header(None)
):
    """
    Authenticate a user and return a JWT token.
    """
    validate_security_key(security_key)
    try:
        login_response = login_user(db, user_data, security_key)
        return {"status": "success", "message": "Login successful", "data": login_response}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# ---------------------- Update User ----------------------

@router.put("/update-user/{user_id}", response_model=Any, status_code=status.HTTP_200_OK)
def update_user_request(
    user_id: int,
    user_data: UserCreate,
    db: Session = Depends(get_db),
    security_key: str = Header(None)
):
    """
    Update an existing user.
    """
    validate_security_key(security_key)
    try:
        updated_user = update_user(db, user_id, user_data, security_key)
        return {"status": "success", "message": "User updated successfully", "data": updated_user}
    except Exception as e:
        raise HTTPException(status_code=404, detail="User not found")

# ---------------------- Delete User ----------------------

@router.delete("/delete-users/{user_id}", response_model=Any, status_code=status.HTTP_200_OK)
def delete_user_request(
    user_id: int,
    db: Session = Depends(get_db),
    security_key: str = Header(None)
):
    """
    Soft delete a user by their ID.
    """
    validate_security_key(security_key)
    try:
        delete_user(db, user_id, security_key)
        return {"status": "success", "message": "User deleted successfully", "data": {"user_id": user_id}}
    except Exception as e:
        raise HTTPException(status_code=404, detail="User not found")

# ---------------------- Forgot Password ----------------------

@router.post("/users/forgot-password", response_model=Any, status_code=status.HTTP_200_OK)
def forgot_password_request(
    forgot_data: ForgotPassword,
    db: Session = Depends(get_db),
    security_key: str = Header(None)
):
    """
    Generate a reset token for a user.
    """
    validate_security_key(security_key)
    try:
        response = forgot_password(db, forgot_data, security_key)
        return {"status": "success", "message": response["message"], "data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send reset link")

# ---------------------- Change Password ----------------------

@router.put("/users/change-password/{user_id}", response_model=Any, status_code=status.HTTP_200_OK)
def change_password_request(
    user_id: int,
    change_data: ChangePassword,
    db: Session = Depends(get_db),
    security_key: str = Header(None)
):
    """
    Change the password for a user.
    """
    validate_security_key(security_key)
    try:
        response = change_password(db, user_id, change_data, security_key)
        return {"status": "success", "message": "Password changed successfully", "data": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------------------- Update Profile ----------------------

@router.put("/users/{user_id}/profile", response_model=Any, status_code=status.HTTP_200_OK)
def update_user_profile(
    user_id: int,
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
    security_key: str = Header(None)
):
    """
    Update a user's profile.
    """
    validate_security_key(security_key)
    try:
        updated_profile = update_profile(db, user_id, profile_data, security_key)
        return {"status": "success", "message": "Profile updated successfully", "data": updated_profile}
    except Exception as e:
        raise HTTPException(status_code=404, detail="User not found")
