from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.schemas.UserModules.users import (
    UserCreate, UserLogin, UserUpdate, RegisterUser, ForgotPassword,
    ChangePassword, ProfileUpdate, UserOut
)
from app.models.UserModules.users import User
from app.repositories.UserModules.users import UserRepository
from app.core.config import Config as settings
from secrets import token_urlsafe
import smtplib
from email.mime.text import MIMEText

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

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
    validate_security_key(security_key, settings.SECRET_KEY)
    user_repo = UserRepository(db)
    users = user_repo.get_all_users()
    return {"status": "success", "message": "Users retrieved successfully", "data": users}

def get_user_by_id(db: Session, user_id: int, security_key: str):
    """Fetch a user by their ID."""
    validate_security_key(security_key, settings.SECRET_KEY)
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "message": "User retrieved successfully", "data": user}

def get_users_by_name(db: Session, name: str, security_key: str):
    """Fetch users by their name."""
    validate_security_key(security_key, settings.SECRET_KEY)
    user_repo = UserRepository(db)
    users = user_repo.get_users_by_name(name)
    return {"status": "success", "message": "Users retrieved successfully", "data": users}

def create_user(db: Session, user_data: UserCreate, security_key: str):
    """Create a new user."""
    validate_security_key(security_key, settings.SECRET_KEY)
    user_repo = UserRepository(db)
    if user_repo.get_user_by_email(user_data.Email):
        raise HTTPException(status_code=409, detail="Email already exists")
    user_data.Password = get_password_hash(user_data.Password)
    user = user_repo.create_user(user_data)
    return {"status": "success", "message": "User created successfully", "data": user}

def register_user(db: Session, user_data: RegisterUser, security_key: str):
    """Register a new user."""
    validate_security_key(security_key, settings.SECRET_KEY)
    if user_data.Password != user_data.Confirm_Password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    return create_user(db, user_data, security_key)

def login_user(db: Session, user_data: UserLogin, security_key: str):
    """Authenticate a user and return a JWT token."""
    validate_security_key(security_key, settings.SECRET_KEY)
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(user_data.Email)
    if not user or not verify_password(user_data.Password, user.Password_Hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.Email})
    return {"status": "success", "message": "Login successful", "data": {"access_token": access_token, "token_type": "bearer"}}

def update_user(db: Session, user_id: int, user_data: UserUpdate, security_key: str):
    """
    Update an existing user's details.
    """
    validate_security_key(security_key, settings.SECRET_KEY)
    user_repo = UserRepository(db)
    existing_user = user_repo.get_user_by_id(user_id)

    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Hash the password if it is being updated
    if user_data.Password:
        user_data.Password = get_password_hash(user_data.Password)

    # Update the user
    updated_user = user_repo.update_user(user_id, user_data)
    return {"status": "success", "message": "User updated successfully", "data": updated_user}

def delete_user(db: Session, user_id: int, security_key: str):
    """Soft delete a user."""
    validate_security_key(security_key, settings.SECRET_KEY)
    user_repo = UserRepository(db)
    if not user_repo.get_user_by_id(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    user_repo.delete_user(user_id)
    return {"status": "success", "message": "User deleted successfully", "data": {"user_id": user_id}}

def forgot_password(db: Session, forgot_data: ForgotPassword, security_key: str):
    """Generate a reset token for a user and send it via email."""
    validate_security_key(security_key, settings.SECRET_KEY)
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(forgot_data.Email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate reset token
    token = token_urlsafe(32)
    user_repo.save_reset_token(user.User_Id, token)

    # Send reset email
    reset_link = f"https://yourfrontend.com/reset-password?token={token}"
    msg = MIMEText(f"Hi {user.Full_Name},\n\nClick the link to reset your password: {reset_link}")
    msg["Subject"] = "Password Reset Request"
    msg["From"] = settings.SMTP_SENDER
    msg["To"] = forgot_data.Email

    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(msg["From"], [msg["To"]], msg.as_string())
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to send reset email")

    return {"status": "success", "message": "Reset link sent to your email.", "data": None}

def change_password(db: Session, user_id: int, change_data: ChangePassword, security_key: str):
    """Change a user's password."""
    validate_security_key(security_key, settings.SECRET_KEY)
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(user_id)
    if not user or not verify_password(change_data.Current_Password, user.Password_Hash):
        raise HTTPException(status_code=401, detail="Invalid current password")
    if change_data.New_Password != change_data.Confirm_Password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    hashed_password = get_password_hash(change_data.New_Password)
    user_repo.update_password(user_id, hashed_password)
    return {"status": "success", "message": "Password changed successfully", "data": None}

def update_profile(db: Session, user_id: int, profile_data: ProfileUpdate, security_key: str):
    """Update a user's profile."""
    validate_security_key(security_key, settings.SECRET_KEY)
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_repo.update_profile(user_id, profile_data)
    return {"status": "success", "message": "Profile updated successfully", "data": None}

# ---------------------- Role-based Access ----------------------

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

def get_current_user(db: Session, token: str = Depends(oauth2_scheme)):
    """Get the current logged-in user."""
    credentials_exception = HTTPException(
        status_code=401,
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
    """Role-based access control."""
    def dependency(current_user: User = Depends(get_current_user)):
        if current_user.User_Type_Id != required_role_id:
            raise HTTPException(status_code=403, detail="Permission denied")
        return current_user
    return dependency