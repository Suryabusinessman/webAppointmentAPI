from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.UserModules.authservices import AuthService
from app.schemas.UserModules.users import RegisterUser, UserLogin, ChangePassword, ForgotPassword, ResetPassword, DynamicRegisterUser
from app.schemas.UserModules.authschema import LogoutRequest, SendEmailOtpRequest, VerifyEmailOtpRequest
from app.services.SecurityModules.security_service import SecurityService
from app.models.SecurityModules.security_events import SecurityEventType, SecurityEventSeverity
from app.core.security import SecurityManager
from dotenv import load_dotenv
import os
import logging

# Load environment variables from .env file
load_dotenv()

# Access SECRET_KEY from .env
SECRET_KEY = os.getenv("SECRET_KEY")

# Configure logging
logger = logging.getLogger(__name__)

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

# ---------------------- Enhanced Security Functions ----------------------

def check_rate_limits(ip_address: str, endpoint: str, db: Session):
    """Check rate limits for the endpoint"""
    security_service = SecurityService(db)
    
    # Different rate limits for different endpoints
    rate_limits = {
        "login": {"max_requests": 5, "window_seconds": 300},  # 5 attempts per 5 minutes
        "register": {"max_requests": 3, "window_seconds": 3600},  # 3 attempts per hour
        "forgot_password": {"max_requests": 3, "window_seconds": 3600}  # 3 attempts per hour
    }
    
    limit_config = rate_limits.get(endpoint, {"max_requests": 100, "window_seconds": 60})
    
    if not security_service.check_rate_limit(ip_address, endpoint, **limit_config):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many {endpoint} attempts. Please try again later."
        )

def log_security_event(event_type: SecurityEventType, user_id: int = None, ip_address: str = None, 
                      user_agent: str = None, device_fingerprint: str = None, suspicious_score: int = 0,
                      risk_factors: list = None, event_metadata: dict = None, db: Session = None):
    """Helper function to log security events"""
    try:
        if not db:
            db = next(get_db())
        
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            device_fingerprint=device_fingerprint,
            suspicious_score=suspicious_score,
            risk_factors=risk_factors,
            event_metadata=event_metadata,
        )
    except Exception as e:
        logger.error(f"Error logging security event: {str(e)}")

def calculate_suspicious_score(user_id: int, ip_address: str, device_fingerprint: str, 
                             request_data: dict, db: Session) -> int:
    """Calculate suspicious activity score"""
    try:
        security_service = SecurityService(db)
        return security_service.calculate_suspicious_score(
            user_id, ip_address, device_fingerprint, SecurityEventType.LOGIN_ATTEMPT, request_data
        )
    except Exception as e:
        logger.error(f"Error calculating suspicious score: {str(e)}")
        return 0

# ---------------------- Enhanced Dynamic Register User ----------------------

@router.post("/register", response_model=dict)
def register_user(
    user_data: DynamicRegisterUser,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Register a new user with dynamic registration based on user type.
    Supports business and regular user registration with enhanced security features.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Security checks
        check_rate_limits(ip_address, "register", db)
        
        # Generate device fingerprint
        security_service = SecurityService(db)
        device_fingerprint = security_service.generate_device_fingerprint(
            device_info, ip_address, dict(request.headers)
        )
        
        # Calculate suspicious score for registration
        suspicious_score = security_service.calculate_suspicious_score(
            None, ip_address, device_fingerprint, SecurityEventType.REGISTRATION,
            user_data.dict()
        )
        
        # Log registration attempt
        log_security_event(
            event_type=SecurityEventType.REGISTRATION,
            user_id=None, # No user_id for registration
            ip_address=ip_address,
            user_agent=device_info,
            device_fingerprint=device_fingerprint,
            suspicious_score=suspicious_score,
            event_metadata={
                "registration_data": {k: v for k, v in user_data.dict().items() if k not in ["password", "confirm_password"]},
                "suspicious_score": suspicious_score,
                "user_type_id": user_data.user_type_id
            },
            db=db
        )
        
        # Proceed with dynamic registration logic
        auth_service = AuthService(db)
        result = auth_service.register_user_dynamic(user_data, device_info, ip_address)
        
        # Return success response
        return result
        
    except HTTPException as he:
        # Normalize error responses to user-friendly messages
        raise HTTPException(status_code=he.status_code, detail=str(he.detail))
    except Exception as e:
        logger.error(f"Error in enhanced dynamic registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user. Please check your data and try again."
        )

# ---------------------- Enhanced Login User ----------------------

@router.post("/login", response_model=dict)
def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Authenticate a user with enhanced security features.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Security checks
        check_rate_limits(ip_address, "login", db)
        
        # Generate device fingerprint
        security_service = SecurityService(db)
        device_fingerprint = security_service.generate_device_fingerprint(
            device_info, ip_address, dict(request.headers)
        )
        
        # Proceed with existing login logic
        auth_service = AuthService(db)
        result = auth_service.login_user(login_data, device_info, ip_address)
        
        # If login successful, add security enhancements
        if result.get("status") == "success" and result.get("data", {}).get("user_id"):
            user_id = result["data"]["user_id"]
            user_email = result["data"]["email"]
            
            # Calculate suspicious score
            suspicious_score = calculate_suspicious_score(
                user_id, ip_address, device_fingerprint, 
                {"email": login_data.email, "headers": dict(request.headers)}, db
            )
            
            # Validate device consistency
            is_consistent, risk_factors = security_service.validate_device_consistency(
                user_id, device_fingerprint, ip_address
            )
            
            # Create security session
            access_token = result["data"].get("access_token")
            if access_token:
                security_session = security_service.create_security_session(
                    user_id=user_id,
                    user_email=user_email,
                    access_token=access_token,
                    device_fingerprint=device_fingerprint,
                    ip_address=ip_address,
                    device_info={"user_agent": device_info}
                )
            
            # Update user security info
            security_service.update_user_security_info(user_id, ip_address, login_success=True)
            
            # Log successful login
            log_security_event(
                event_type=SecurityEventType.LOGIN_SUCCESS,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=device_info,
                device_fingerprint=device_fingerprint,
                suspicious_score=suspicious_score,
                risk_factors=risk_factors,
                event_metadata={
                    "device_consistent": is_consistent,
                    "risk_factors": risk_factors,
                    "suspicious_score": suspicious_score
                },
                db=db
            )
            
            # Log suspicious activity (no blocking)
            if suspicious_score > 70:
                security_service.log_security_event(
                    event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                    user_id=user_id,
                    ip_address=ip_address,
                    device_fingerprint=device_fingerprint,
                    suspicious_score=suspicious_score,
                    severity=SecurityEventSeverity.HIGH,
                    event_metadata={"activity_type": "login", "suspicious_score": suspicious_score},
                    db=db
                )
            
            # Add security info to response
            result["data"]["security_info"] = {
                "device_consistent": is_consistent,
                "risk_factors": risk_factors,
                "suspicious_score": suspicious_score,
                "session_id": security_session.session_id if security_session else None
            }
            
        else:
            # Log failed login attempt
            log_security_event(
                event_type=SecurityEventType.LOGIN_FAILED,
                user_id=None, # No user_id for failed login
                ip_address=ip_address,
                user_agent=device_info,
                event_metadata={"reason": "Invalid credentials"},
                db=db
            )
        
        # Return the result directly since it already has the proper structure
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in enhanced login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please check your credentials and try again."
        )

# ---------------------- Enhanced Logout User ----------------------

@router.post("/logout", response_model=dict)
def logout_user(
    payload: LogoutRequest,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Logout a user with enhanced security features.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Proceed with existing logout logic (include IP and device in audit)
        auth_service = AuthService(db)
        result = auth_service.logout_user(payload.token, ip_address=ip_address, user_agent=device_info)
        
        # Log logout event
        log_security_event(
            event_type=SecurityEventType.LOGOUT,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"session_ended": True},
            db=db
        )
        
        return {"status": "success", "color": "success", "message": result["message"]}
        
    except Exception as e:
        logger.error(f"Error in logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout. Please try again later."
        )

# ---------------------- Registration Email OTP ----------------------

@router.post("/register/send-otp", response_model=dict)
def send_registration_otp(
    payload: SendEmailOtpRequest,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    try:
        device_info, ip_address = get_device_info_and_ip(request)

        # Rate limit OTP sends per IP
        check_rate_limits(ip_address, "register", db)

        auth_service = AuthService(db)
        result = auth_service.send_registration_otp(email=payload.email)

        # Log security event
        log_security_event(
            event_type=SecurityEventType.REGISTRATION,
            user_id=None,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"otp_sent": True, "email": payload.email},
            db=db,
        )
        return {"status": "success", "color": "success", "message": result["message"]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending registration OTP: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send OTP. Please try again later.")


@router.post("/register/verify-otp", response_model=dict)
def verify_registration_otp(
    payload: VerifyEmailOtpRequest,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    try:
        device_info, ip_address = get_device_info_and_ip(request)

        auth_service = AuthService(db)
        result = auth_service.verify_registration_otp(email=payload.email, otp=payload.otp)

        # Log security event
        log_security_event(
            event_type=SecurityEventType.REGISTRATION,
            user_id=None,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"otp_verified": True, "email": payload.email},
            db=db,
        )
        return {"status": "success", "color": "success", "message": result["message"]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying registration OTP: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to verify OTP. Please try again later.")

# ---------------------- Enhanced Change Password ----------------------

@router.post("/change-password", response_model=dict)
def change_password(
    user_id: int,
    change_data: ChangePassword,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Change a user's password with enhanced security features.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log password change event
        log_security_event(
            event_type=SecurityEventType.PASSWORD_CHANGE,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"password_changed": True},
            db=db
        )
        
        # Proceed with existing change password logic
        auth_service = AuthService(db)
        result = auth_service.change_password(user_id, change_data)
        
        return {"status": "success", "color": "success", "message": result["message"]}
        
    except Exception as e:
        logger.error(f"Error in enhanced change password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password. Please check your current password and try again."
        )

# ---------------------- Enhanced Forgot Password ----------------------

@router.post("/forgot-password", response_model=dict)
def forgot_password(
    forgot_data: ForgotPassword,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Generate a reset token with enhanced security features.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Security checks
        check_rate_limits(ip_address, "forgot_password", db)
        
        # Log forgot password event
        log_security_event(
            event_type=SecurityEventType.PASSWORD_RESET,
            user_id=None, # No user_id for forgot password
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"reset_requested": True},
            db=db
        )
        
        # Proceed with existing forgot password logic
        auth_service = AuthService(db)
        result = auth_service.forgot_password(forgot_data)
        
        return {"status": "success", "color": "success", "message": result["message"]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in enhanced forgot password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process password reset. Please try again later."
        )

# ---------------------- Enhanced Reset Password ----------------------

@router.post("/reset-password", response_model=dict)
def reset_password(
    reset_data: ResetPassword,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Reset password using token (single-use).
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Security checks
        check_rate_limits(ip_address, "reset_password", db)
        
        # Proceed with reset password logic
        auth_service = AuthService(db)
        result = auth_service.reset_password(reset_data)
        
        # Log password reset event
        user = auth_service.auth_repo.get_user_by_email(reset_data.email)
        log_security_event(
            event_type=SecurityEventType.PASSWORD_RESET,
            user_id=user.user_id,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"password_reset": True},
            db=db
        )
        
        return {"status": "success", "color": "success", "message": result["message"]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in reset password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password. Please try again later."
        )

# ---------------------- Business Types Endpoint ----------------------

@router.get("/business-types", response_model=dict)
def get_business_types(
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Get available business types for registration form.
    """
    try:
        from app.services.BusinessModules.businesstype import BusinessTypeService
        from app.repositories.BusinessModules.businesstype import BusinessTypeRepository
        
        business_type_repo = BusinessTypeRepository(db)
        business_types = business_type_repo.get_active_business_types()
        
        return {
            "status": "success",
            "message": "Business types retrieved successfully",
            "data": business_types
        }
        
    except Exception as e:
        logger.error(f"Error getting business types: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Security Report Endpoint ----------------------

@router.get("/security-report/{user_id}", response_model=dict)
def get_security_report(
    user_id: int,
    db: Session = Depends(get_db),
    secret_key: str = Depends(validate_secret_key)
):
    """
    Get comprehensive security report for user.
    """
    try:
        security_service = SecurityService(db)
        report = security_service.get_user_security_report(user_id)
        
        return {
            "status": "success",
            "message": "Security report retrieved successfully",
            "data": report
        }
        
    except Exception as e:
        logger.error(f"Error getting security report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )