from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.UserModules.authservices import AuthService
from app.schemas.UserModules.users import RegisterUser, UserLogin, ChangePassword, ForgotPassword
from app.schemas.UserModules.authschema import LogoutRequest
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access SECRET_KEY from .env
SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter(
    # prefix="/auth",
    # tags=["Authentication"],
    # responses={404: {"description": "Not found"}}
)

# ---------------------- Utility Function ----------------------

def validate_secret_key(secret_key: str = Header(...)):
    """Validate the SECRET_KEY from the request header."""
    if secret_key != SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid SECRET_KEY provided."
        )

def get_device_info_and_ip(request: Request):
    """Extract device information and IP address from the request."""
    # Extract device information from the User-Agent header
    device_info = request.headers.get("User-Agent", "Unknown Device")

    # Extract IP address from X-Forwarded-For or Remote-Addr headers
    ip_address = request.headers.get("X-Forwarded-For")
    if ip_address:
        # X-Forwarded-For may contain multiple IPs, take the first one
        ip_address = ip_address.split(",")[0].strip()
    else:
        ip_address = request.client.host  # Fallback to Remote-Addr

    return device_info, ip_address

# ---------------------- Register User ----------------------

@router.post("/register", response_model=dict)
def register_user(
    user_data: RegisterUser,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Register a new user, create a session, and send a welcome email.
    """
    device_info, ip_address = get_device_info_and_ip(request)
    auth_service = AuthService(db)
    result = auth_service.register_user(user_data, device_info, ip_address)
    return {"status": "success", "message": result["message"], "data": result}

# ---------------------- Login User ----------------------

@router.post("/login", response_model=dict)
def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Authenticate a user, create a session, and enforce password policy.
    """
    device_info, ip_address = get_device_info_and_ip(request)
    auth_service = AuthService(db)
    result = auth_service.login_user(login_data, device_info, ip_address)
    return {"status": "success","color":"success", "message": result["message"], "data": result}

# ---------------------- Logout User ----------------------

@router.post("/logout", response_model=dict)
def logout_user(
    # token: str = Header(...),
    payload: LogoutRequest,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Logout a user by ending their session.
    """
    
    auth_service = AuthService(db)
    result = auth_service.logout_user(payload.token)
    return {"status": "success", "message": result["message"]}

# ---------------------- Change Password ----------------------

@router.post("/change-password", response_model=dict)
def change_password(
    user_id: int,
    change_data: ChangePassword,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Change a user's password and send a confirmation email.
    """
    auth_service = AuthService(db)
    result = auth_service.change_password(user_id, change_data)
    return {"status": "success", "message": result["message"]}

# ---------------------- Forgot Password ----------------------

@router.post("/forgot-password", response_model=dict)
def forgot_password(
    forgot_data: ForgotPassword,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Generate a reset token, send a reset link, and notify the user.
    """
    device_info, ip_address = get_device_info_and_ip(request)
    auth_service = AuthService(db)
    result = auth_service.forgot_password(forgot_data)
    return {"status": "success", "message": result["message"]}