from fastapi import HTTPException, status, Depends, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.schemas.UserModules.users import (
    UserCreate, UserLogin, UserUpdate, RegisterUser, ForgotPassword,
    ChangePassword, ProfileUpdate, UserResponse
)
from app.models.UserModules.users import User
from app.repositories.UserModules.users import UserRepository
from app.core.config import config
from app.utils.file_upload import save_upload_file
from secrets import token_urlsafe
import smtplib
from email.mime.text import MIMEText

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = config.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# File upload directories
UPLOAD_DIRECTORY_PROFILE_IMAGES = "uploads/profile_images"
UPLOAD_DIRECTORY_BACKGROUND_IMAGES = "uploads/background_images"

# ---------------------- Utility Functions ----------------------

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a plain text password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def validate_security_key(provided_key: str, expected_key: str):
    """Validate the security key for API access."""
    if provided_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid security key."
        )

# ---------------------- Service Functions ----------------------

def get_all_users(db: Session, security_key: str):
    """Fetch all users."""
    # Debug logging
    print(f"Service received security_key: {security_key}")
    print(f"Config SECRET_KEY: {config.SECRET_KEY}")
    print(f"Keys match: {security_key == config.SECRET_KEY}")
    
    validate_security_key(security_key, config.SECRET_KEY)
    user_repo = UserRepository(db)
    users = user_repo.get_all_users()
    return {"status": "success", "message": "Users retrieved successfully", "data": users}

def get_user_by_id(db: Session, user_id: int, security_key: str):
    """Fetch a user by their ID."""
    validate_security_key(security_key, config.SECRET_KEY)
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "message": "User retrieved successfully", "data": user}

def get_users_by_name(db: Session, name: str, security_key: str):
    """Fetch users by their name."""
    validate_security_key(security_key, config.SECRET_KEY)
    user_repo = UserRepository(db)
    users = user_repo.get_users_by_name(name)
    return {"status": "success", "message": "Users retrieved successfully", "data": users}

def create_user(db: Session, user_data: UserCreate, security_key: str, 
                profile_image: Optional[UploadFile] = None, 
                background_image: Optional[UploadFile] = None):
    """Create a new user with enhanced validation, security, and file uploads."""
    try:
        validate_security_key(security_key, config.SECRET_KEY)
        user_repo = UserRepository(db)
        
        # Check if email already exists
        if user_repo.get_user_by_email(user_data.email):
            raise HTTPException(status_code=409, detail="Email already exists")
        
        # Validate password strength
        if len(user_data.password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        
        # Handle file uploads
        profile_image_path = None
        background_image_path = None
        
        if profile_image:
            profile_image_path = save_upload_file(profile_image, UPLOAD_DIRECTORY_PROFILE_IMAGES)
        
        if background_image:
            background_image_path = save_upload_file(background_image, UPLOAD_DIRECTORY_BACKGROUND_IMAGES)
        
        # Update user data with file paths
        user_data.profile_image = profile_image_path
        user_data.background_image = background_image_path
        
        # Hash password
        user_data.password = get_password_hash(user_data.password)
        user = user_repo.create_user(user_data)
        
        return {"status": "success", "message": "User created successfully", "data": user}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User creation failed: {str(e)}")

def register_user(db: Session, user_data: RegisterUser, security_key: str,
                 profile_image: Optional[UploadFile] = None,
                 background_image: Optional[UploadFile] = None):
    """Register a new user with enhanced validation and file uploads."""
    try:
        validate_security_key(security_key, config.SECRET_KEY)
        user_repo = UserRepository(db)
        
        # Check if email already exists
        if user_repo.get_user_by_email(user_data.email):
            raise HTTPException(status_code=409, detail="Email already exists")
        
        # Validate password strength
        if len(user_data.password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        
        # Handle file uploads
        profile_image_path = None
        background_image_path = None
        
        if profile_image:
            profile_image_path = save_upload_file(profile_image, UPLOAD_DIRECTORY_PROFILE_IMAGES)
        
        if background_image:
            background_image_path = save_upload_file(background_image, UPLOAD_DIRECTORY_BACKGROUND_IMAGES)
        
        # Create user data with file paths
        user_create_data = UserCreate(
            full_name=user_data.full_name,
            email=user_data.email,
            phone=user_data.phone,
            password=user_data.password,
            user_type_id=user_data.user_type_id,
            profile_image=profile_image_path,
            background_image=background_image_path
        )
        
        user = user_repo.create_user(user_create_data)
        
        return {"status": "success", "message": "User registered successfully", "data": user}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User registration failed: {str(e)}")

def login_user(db: Session, user_data: UserLogin, security_key: str):
    """Login a user with enhanced security."""
    try:
        validate_security_key(security_key, config.SECRET_KEY)
        user_repo = UserRepository(db)
        
        # Get user by email
        user = user_repo.get_user_by_email(user_data.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not verify_password(user_data.password, user.password_hash):
            # Increment failed login attempts
            user_repo.increment_failed_login_attempts(user.user_id)
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Check if account is locked
        if user.account_locked_until and user.account_locked_until > datetime.utcnow():
            raise HTTPException(status_code=423, detail="Account is temporarily locked")
        
        # Reset failed login attempts
        user_repo.reset_failed_login_attempts(user.user_id)
        
        # Update last login
        user_repo.update_last_login(user.user_id)
        
        # Create access token
        access_token = create_access_token(data={"sub": user.email})
        
        return {
            "status": "success",
            "message": "Login successful",
            "data": {
                "access_token": access_token,
                "user": user
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

def update_user(db: Session, user_id: int, user_data: UserUpdate, security_key: str,
                profile_image: Optional[UploadFile] = None,
                background_image: Optional[UploadFile] = None):
    """Update a user with file upload support and existing file preservation."""
    try:
        validate_security_key(security_key, config.SECRET_KEY)
        user_repo = UserRepository(db)
        
        # Get existing user
        existing_user = user_repo.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Handle file uploads - preserve existing files if no new files provided
        profile_image_path = existing_user.profile_image  # Keep existing file
        background_image_path = existing_user.background_image  # Keep existing file
        
        if profile_image:
            profile_image_path = save_upload_file(profile_image, UPLOAD_DIRECTORY_PROFILE_IMAGES)
        
        if background_image:
            background_image_path = save_upload_file(background_image, UPLOAD_DIRECTORY_BACKGROUND_IMAGES)
        
        # Update user data with file paths
        user_data.profile_image = profile_image_path
        user_data.background_image = background_image_path
        
        user = user_repo.update_user(user_id, user_data)
        
        return {"status": "success", "message": "User updated successfully", "data": user}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User update failed: {str(e)}")

def delete_user(db: Session, user_id: int, security_key: str):
    """Delete a user with enhanced security."""
    try:
        validate_security_key(security_key, config.SECRET_KEY)
        user_repo = UserRepository(db)
        
        # Check if user exists
        user = user_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Perform soft delete
        user_repo.delete_user(user_id)
        
        return {"status": "success", "message": "User deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User deletion failed: {str(e)}")

def forgot_password(db: Session, forgot_data: ForgotPassword, security_key: str):
    """Handle forgot password with enhanced security."""
    try:
        validate_security_key(security_key, config.SECRET_KEY)
        user_repo = UserRepository(db)
        
        # Get user by email
        user = user_repo.get_user_by_email(forgot_data.email)
        if not user:
            # Don't reveal if email exists or not for security
            return {"status": "success", "message": "If email exists, reset instructions have been sent"}
        
        # Generate reset token
        reset_token = token_urlsafe(32)
        user_repo.set_reset_token(user.user_id, reset_token)
        
        # TODO: Send email with reset token
        # For now, just return success
        
        return {"status": "success", "message": "Password reset instructions sent to email"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Password reset failed: {str(e)}")

def change_password(db: Session, user_id: int, change_data: ChangePassword, security_key: str):
    """Change user password with enhanced security."""
    try:
        validate_security_key(security_key, config.SECRET_KEY)
        user_repo = UserRepository(db)
        
        # Get user
        user = user_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify current password
        if not verify_password(change_data.current_password, user.password_hash):
            raise HTTPException(status_code=401, detail="Current password is incorrect")
        
        # Validate new password
        if len(change_data.new_password) < 8:
            raise HTTPException(status_code=400, detail="New password must be at least 8 characters long")
        
        # Hash new password
        new_password_hash = get_password_hash(change_data.new_password)
        
        # Update password
        user_repo.update_password(user_id, new_password_hash)
        
        return {"status": "success", "message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Password change failed: {str(e)}")

def update_profile(db: Session, user_id: int, profile_data: ProfileUpdate, security_key: str,
                  profile_image: Optional[UploadFile] = None,
                  background_image: Optional[UploadFile] = None):
    """Update user profile with file upload support."""
    try:
        validate_security_key(security_key, config.SECRET_KEY)
        user_repo = UserRepository(db)
        
        # Get existing user
        existing_user = user_repo.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Handle file uploads - preserve existing files if no new files provided
        profile_image_path = existing_user.profile_image  # Keep existing file
        background_image_path = existing_user.background_image  # Keep existing file
        
        if profile_image:
            profile_image_path = save_upload_file(profile_image, UPLOAD_DIRECTORY_PROFILE_IMAGES)
        
        if background_image:
            background_image_path = save_upload_file(background_image, UPLOAD_DIRECTORY_BACKGROUND_IMAGES)
        
        # Update profile data with file paths
        profile_data.profile_image = profile_image_path
        profile_data.background_image = background_image_path
        
        user = user_repo.update_user(user_id, profile_data)
        
        return {"status": "success", "message": "Profile updated successfully", "data": user}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile update failed: {str(e)}")

def activate_user(db: Session, user_id: int, security_key: str):
    """Activate a user."""
    try:
        validate_security_key(security_key, config.SECRET_KEY)
        user_repo = UserRepository(db)
        
        user = user_repo.activate_user(user_id)
        return {"status": "success", "message": "User activated successfully", "data": user}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User activation failed: {str(e)}")

def deactivate_user(db: Session, user_id: int, security_key: str):
    """Deactivate a user."""
    try:
        validate_security_key(security_key, config.SECRET_KEY)
        user_repo = UserRepository(db)
        
        user = user_repo.deactivate_user(user_id)
        return {"status": "success", "message": "User deactivated successfully", "data": user}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User deactivation failed: {str(e)}")

def get_active_users(db: Session, security_key: str):
    """Get all active users."""
    try:
        validate_security_key(security_key, config.SECRET_KEY)
        user_repo = UserRepository(db)
        
        users = user_repo.get_active_users()
        return {"status": "success", "message": "Active users retrieved successfully", "data": users}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active users: {str(e)}")

def get_inactive_users(db: Session, security_key: str):
    """Get all inactive users."""
    try:
        validate_security_key(security_key, config.SECRET_KEY)
        user_repo = UserRepository(db)
        
        users = user_repo.get_inactive_users()
        return {"status": "success", "message": "Inactive users retrieved successfully", "data": users}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get inactive users: {str(e)}")

# ---------------------- Authentication Dependencies ----------------------

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

def get_current_user(db: Session, token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(email)
    if user is None:
        raise credentials_exception
    return user

def require_role(required_role_id: int):
    """Dependency to require a specific user role."""
    def dependency(current_user: User = Depends(get_current_user)):
        if current_user.user_type_id != required_role_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return dependency