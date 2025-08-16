from sqlalchemy.orm import Session
from app.repositories.UserModules.authrepositories import AuthRepository
from app.repositories.UserModules.users import UserRepository
from app.repositories.UserModules.userpermissions import UserPermissionRepository
from app.repositories.UserModules.usertypes import UserTypeRepository
from app.schemas.UserModules.users import (
    RegisterUser, UserLogin, ChangePassword, ForgotPassword, ResetPassword, DynamicRegisterUser, BusinessRegistrationData
)
from app.services.UserModules.users import create_access_token
from app.core.config import Config as settings
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import socket
import os

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.auth_repo = AuthRepository(db)
        self.user_repo = UserRepository(db)
        self.user_permission_repo = UserPermissionRepository(db)
        self.user_type_repo = UserTypeRepository(db)
        self.notification_service = None  # Defensive: prevent attribute error

    # ---------------------- Utility Functions ----------------------

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a hashed password."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a plain text password."""
        return pwd_context.hash(password)

    def validate_security_key(self, provided_key: str):
        """Validate the security key for API access."""
        if provided_key != SECRET_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid security key."
            )

    def send_email(self, to_email: str, subject: str, body: str):
        """Send an email using SMTP."""
        msg = MIMEText(body, "html")
        msg["Subject"] = subject
        msg["From"] = formataddr(("AppointmentTech", settings.SMTP_SENDER))
        msg["To"] = to_email
        # Encourage no-reply behavior and suppress auto-responses
        try:
            domain = settings.SMTP_USER.split("@", 1)[1] if "@" in (settings.SMTP_USER or "") else None
        except Exception:
            domain = None
        reply_to = f"no-reply@{domain}" if domain else (settings.SMTP_SENDER or "no-reply@example.com")
        msg["Reply-To"] = reply_to
        msg["Auto-Submitted"] = "auto-generated"
        msg["X-Auto-Response-Suppress"] = "All"
        msg["Precedence"] = "bulk"

        # Preflight DNS/host validation to provide clearer errors
        host = (settings.SMTP_SERVER or "").strip()
        port = int(getattr(settings, "SMTP_PORT", 587) or 587)
        if not host:
            raise HTTPException(status_code=500, detail="SMTP_SERVER is empty. Please set SMTP_SERVER in environment.")
        try:
            socket.getaddrinfo(host, port)
        except Exception:
            raise HTTPException(status_code=500, detail=f"SMTP host resolution failed for '{host}:{port}'. Check SMTP_SERVER and DNS connectivity.")

        try:
            with smtplib.SMTP(host, port) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(msg["From"], [msg["To"]], msg.as_string())
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

    # ---------------------- Email OTP ----------------------

    def send_registration_otp(self, email: str, user_id: int = None):
        record, otp_plain = self.auth_repo.create_or_update_email_otp(email=email, user_id=user_id, purpose="EMAIL_VERIFICATION", ttl_minutes=10)

        # Simple, branded HTML template
        html = f"""
        <div style='font-family: Arial, sans-serif; color: #333;'>
            <h2 style='color:#2b6cb0;margin-bottom:8px;'>Verify your email</h2>
            <p>Hello,</p>
            <p>Your OTP for verifying your AppointmentTech account is:</p>
            <p style='font-size:24px;letter-spacing:4px;font-weight:bold;color:#2b6cb0'>{otp_plain}</p>
            <p>This code will expire in 10 minutes. Do not share it with anyone.</p>
            <hr style='border:none;border-top:1px solid #eee;margin:16px 0'>
            <p style='font-size:12px;color:#777'>If you did not request this, you can ignore this email.</p>
        </div>
        """

        self.send_email(to_email=email, subject="Your OTP for email verification", body=html)
        return {"message": "OTP sent to email"}

    def verify_registration_otp(self, email: str, otp: str):
        ok = self.auth_repo.verify_email_otp(email=email, otp=otp, purpose="EMAIL_VERIFICATION")
        if not ok:
            raise HTTPException(status_code=400, detail="OTP verification failed")
        # Optionally mark user as verified
        try:
            user = self.user_repo.get_user_by_email(email)
            if user and not user.is_verified:
                user.is_verified = True
                self.db.commit()
        except Exception:
            # Non-fatal if user fetch/verify fails (supports pre-registration OTP)
            pass
        return {"message": "Email verified successfully"}

    def validate_token(self, token: str):
        """Validate a JWT token and check its expiry."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
                raise HTTPException(status_code=401, detail="Token has expired")
            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    # ---------------------- Dynamic Register User ----------------------

    def register_user_dynamic(self, user_data: DynamicRegisterUser, device_info: str, ip_address: str):
        """
        Register a new user with dynamic registration based on user type.
        Supports business and regular user registration with audit logging and notifications.
        """
        try:
            # Validate user_type exists BEFORE creating user (user-friendly error if invalid)
            try:
                self.user_type_repo.get_by_id(user_data.user_type_id)
            except HTTPException as httex:
                if httex.status_code == 404:
                    raise HTTPException(status_code=400, detail="Invalid user_type_id. Please select a valid user type.")
                raise

            # Normalize and validate gender if provided
            if user_data.gender:
                normalized_gender = str(user_data.gender).strip().title()
                allowed_genders = {"Male", "Female", "Other"}
                if normalized_gender not in allowed_genders:
                    raise HTTPException(status_code=400, detail="Invalid gender. Allowed values: Male, Female, Other.")
                user_data.gender = normalized_gender

            # Create base user
            user = self.auth_repo.create_user_dynamic(user_data)
            
            # Create welcome notification (simplified for now)
            # self.notification_service.create_registration_notification(
            #     user_id=user.user_id,
            #     user_email=user.email,
            #     user_name=user.full_name
            # )
            
            # Create audit log for user creation
            self.auth_repo.create_audit_log(
                user_id=user.user_id,
                action_type="CREATE",
                table_name="users",
                record_id=user.user_id,
                new_values={
                    "full_name": user.full_name,
                    "email": user.email,
                    "user_type_id": user.user_type_id,
                    "phone": user.phone
                },
                ip_address=ip_address,
                user_agent=device_info
            )
            
            # Business user creation removed for now
            # business_users = []
            # if user_data.user_type_id == 2 and user_data.business_data:  # Business user
            #     business_users = self.auth_repo.create_business_user(user, user_data.business_data)
            #     
            #     # Create business registration notification
            #     for bu in business_users:
            #         self.notification_service.create_business_registration_notification(
            #             user_id=user.user_id,
            #             user_email=user.email,
            #             user_name=user.full_name,
            #             business_name=bu.business_name
            #         )
            #     
            #     # Create audit log for business user creation
            #     for bu in business_users:
            #         self.auth_repo.create_audit_log(
            #             user_id=user.user_id,
            #             action_type="CREATE",
            #             table_name="business_users",
            #             record_id=bu.business_user_id,
            #             new_values={
            #             "business_name": bu.business_name,
            #             "business_type_id": bu.business_type_id,
            #             "user_id": bu.user_id
            #         },
            #         ip_address=ip_address,
            #         user_agent=device_info
            #     )
            
            # Create user session
            token = create_access_token(data={"sub": user.email})
            session = self.auth_repo.create_session(user.user_id, token, device_info, ip_address)
            
            # Get user info and permissions
            user_info = self.user_repo.get_user_by_email(user_data.email)
            user_type_info = self.user_type_repo.get_by_id(user_data.user_type_id)
            user_permissions = self.user_permission_repo.get_user_permissions_with_pages(user_data.user_type_id)
            
            # Create audit log for session creation
            self.auth_repo.create_audit_log(
                user_id=user.user_id,
                action_type="LOGIN",
                table_name="user_sessions",
                record_id=session.session_id,
                new_values={
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "ip_address": session.ip_address
                },
                ip_address=ip_address,
                user_agent=device_info,
                session_id=session.session_id
            )
            
            # Prepare response data following the same structure as login
            return {
                "status": "success",
                "message": "User registered successfully. A welcome email has been sent.",
                "access_token": token,
                "session_id": session.session_id,
                "user_info": user_info,
                "user_type_data": user_type_info,
                "user_type_name": user_type_info.type_name,
                "user_type_id": user_type_info.user_type_id,
                "default_page": user_type_info.default_page,
                "user_id": user.user_id,
                "user_type": user.user_type_id,
                "user_permission": user_permissions
            }
            
        except Exception as e:
            # Create audit log for failed registration
            if 'user' in locals():
                self.auth_repo.create_audit_log(
                    user_id=user.user_id if hasattr(user, 'user_id') else None,
                    action_type="CREATE",
                    table_name="users",
                    record_id=0,
                    old_values={"error": str(e)},
                    ip_address=ip_address,
                    user_agent=device_info
                )
            raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

    # ---------------------- Register User (Legacy) ----------------------

    def register_user(self, user_data: RegisterUser, device_info: str, ip_address: str):
        """
        Register a new user, create a session, and send notifications.
        """
        try:
            # Validate and create the user
            user = self.auth_repo.create_user(user_data)
            
            # Create welcome notification (simplified for now)
            # self.notification_service.create_registration_notification(
            #     user_id=user.user_id,
            #     user_email=user.email,
            #     user_name=user.full_name
            # )
            
            # Create a session for the user
            token = create_access_token(data={"sub": user.email})
            session = self.auth_repo.create_session(user.user_id, token, device_info, ip_address)
            
            # Get user info and permissions
            user_info = self.user_repo.get_user_by_email(user_data.email)
            user_type_info = self.user_type_repo.get_by_id(user_data.user_type_id)
            user_permission_info = self.user_permission_repo.get_user_permissions_with_pages(user_info.user_type_id)
            
            # Ensure user_permission_info is always a list (empty if no permissions)
            if user_permission_info is None:
                user_permission_info = []

            # Create audit log for registration
            self.auth_repo.create_audit_log(
                user_id=user.user_id,
                action_type="REGISTER",
                table_name="users",
                record_id=user.user_id,
                new_values={
                    "full_name": user.full_name,
                    "email": user.email,
                    "user_type_id": user.user_type_id
                },
                ip_address=ip_address,
                user_agent=device_info
            )

            # Convert SQLAlchemy objects to dictionaries for proper serialization
            user_info_dict = {
                "user_id": user.user_id,
                "full_name": user.full_name,
                "email": user.email,
                "phone": user.phone,
                "alt_phone": user.alt_phone,
                "user_type_id": user.user_type_id,
                "profile_image": user.profile_image,
                "background_image": user.background_image,
                "bio": user.bio,
                "website": user.website,
                "social_links": user.social_links,
                "gender": user.gender,
                "dob": user.dob.isoformat() if user.dob else None,
                "occupation": user.occupation,
                "company_name": user.company_name,
                "gst_number": user.gst_number,
                "referral_code": user.referral_code,
                "address": user.address,
                "city": user.city,
                "state": user.state,
                "country": user.country,
                "postal_code": user.postal_code,
                "preferred_language": user.preferred_language,
                "is_verified": user.is_verified,
                "is_active": user.is_active,
                "is_deleted": user.is_deleted,
                "wallet_balance": float(user.wallet_balance) if user.wallet_balance else 0.0,
                "currency": user.currency,
                "last_transaction_id": user.last_transaction_id,
                "payment_mode": user.payment_mode,
                "is_wallet_enabled": user.is_wallet_enabled,
                "failed_login_attempts": user.failed_login_attempts,
                "account_locked_until": user.account_locked_until.isoformat() if user.account_locked_until else None,
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
                "last_login_ip": user.last_login_ip,
                "security_questions": user.security_questions,
                "two_factor_enabled": user.two_factor_enabled,
                "two_factor_secret": user.two_factor_secret,
                "added_by": user.added_by,
                "added_on": user.added_on.isoformat() if user.added_on else None,
                "modified_by": user.modified_by,
                "modified_on": user.modified_on.isoformat() if user.modified_on else None,
                "deleted_by": user.deleted_by,
                "deleted_on": user.deleted_on.isoformat() if user.deleted_on else None
            }
            
            user_type_dict = {
                "user_type_id": user_type_info.user_type_id,
                "type_name": user_type_info.type_name,
                "description": user_type_info.description,
                "default_page": user_type_info.default_page,
                "is_active": user_type_info.is_active,
                "created_at": user_type_info.created_at.isoformat() if user_type_info.created_at else None,
                "updated_at": user_type_info.updated_at.isoformat() if user_type_info.updated_at else None
            }
            
            return {
                "status": "success",
                "message": "User registered successfully. A welcome email has been sent.",
                "access_token": token,
                "session_id": session.session_id,
                "user_info": user_info_dict,
                "user_type": user_type_dict,
                "user_type_name": user_type_info.type_name,
                "user_type_id": user_type_info.user_type_id,
                "default_page": user_type_info.default_page,
                "user_id": user.user_id,
                "user_type": user.user_type_id,
                "user_permission": user_permission_info
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

    # ---------------------- Login User ----------------------

    def login_user(self, login_data: UserLogin, device_info: str, ip_address: str):
        """
        Authenticate a user, create a session, and send login notification.
        """
        try:
            # Validate user credentials
            user = self.auth_repo.login_user(login_data)
            user_info = self.user_repo.get_user_by_email(login_data.email)
            user_permission_info = self.user_permission_repo.get_user_permissions_with_pages(user_info.user_type_id)
            user_type_info = self.user_type_repo.get_by_id(user_info.user_type_id)
            
            # Get user permissions (can be empty array if no permissions assigned)
            # Note: Users can login even without specific page permissions
            if user_permission_info is None:
                user_permission_info = []
            
            # Check if user exists and is not deleted
            if not user_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found."
                )
            
            if user_info.is_deleted == "Y":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User account is deleted."
                )
            
            if not self.verify_password(login_data.password, user_info.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials."
                )

            # Enforce password policy
            if len(login_data.password) < 8:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password must be at least 8 characters long."
                )
            if not any(char.isdigit() for char in login_data.password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password must contain at least one digit."
                )
            if not any(char.isupper() for char in login_data.password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password must contain at least one uppercase letter."
                )

            # Create a session for the user
            token = create_access_token(data={"sub": user.email})
            session = self.auth_repo.create_session(user.user_id, token, device_info, ip_address)

            # Create login notification (check if suspicious login)
            # is_suspicious = self._check_suspicious_login(user.user_id, ip_address, device_info)
            # self.notification_service.create_login_notification(
            #     user_id=user.user_id,
            #     user_email=user.email,
            #     user_name=user.full_name,
            #     ip_address=ip_address,
            #     device_info=device_info,
            #     is_suspicious=is_suspicious
            # )

            # Create audit log for login
            self.auth_repo.create_audit_log(
                user_id=user.user_id,
                action_type="LOGIN",
                table_name="user_sessions",
                record_id=session.session_id,
                new_values={
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "ip_address": session.ip_address
                },
                ip_address=ip_address,
                user_agent=device_info,
                session_id=session.session_id
            )

            # Convert SQLAlchemy objects to dictionaries for proper serialization
            user_info_dict = {
                "user_id": user_info.user_id,
                "full_name": user_info.full_name,
                "email": user_info.email,
                "phone": user_info.phone,
                "alt_phone": user_info.alt_phone,
                "user_type_id": user_info.user_type_id,
                "profile_image": user_info.profile_image,
                "background_image": user_info.background_image,
                "bio": user_info.bio,
                "website": user_info.website,
                "social_links": user_info.social_links,
                "gender": user_info.gender,
                "dob": user_info.dob.isoformat() if user_info.dob else None,
                "occupation": user_info.occupation,
                "company_name": user_info.company_name,
                "gst_number": user_info.gst_number,
                "referral_code": user_info.referral_code,
                "address": user_info.address,
                "city": user_info.city,
                "state": user_info.state,
                "country": user_info.country,
                "postal_code": user_info.postal_code,
                "preferred_language": user_info.preferred_language,
                "is_verified": user_info.is_verified,
                "is_active": user_info.is_active,
                "is_deleted": user_info.is_deleted,
                "wallet_balance": float(user_info.wallet_balance) if user_info.wallet_balance else 0.0,
                "currency": user_info.currency,
                "last_transaction_id": user_info.last_transaction_id,
                "payment_mode": user_info.payment_mode,
                "is_wallet_enabled": user_info.is_wallet_enabled,
                "failed_login_attempts": user_info.failed_login_attempts,
                "account_locked_until": user_info.account_locked_until.isoformat() if user_info.account_locked_until else None,
                "last_login_at": user_info.last_login_at.isoformat() if user_info.last_login_at else None,
                "last_login_ip": user_info.last_login_ip,
                "security_questions": user_info.security_questions,
                "two_factor_enabled": user_info.two_factor_enabled,
                "two_factor_secret": user_info.two_factor_secret,
                "added_by": user_info.added_by,
                "added_on": user_info.added_on.isoformat() if user_info.added_on else None,
                "modified_by": user_info.modified_by,
                "modified_on": user_info.modified_on.isoformat() if user_info.modified_on else None,
                "deleted_by": user_info.deleted_by,
                "deleted_on": user_info.deleted_on.isoformat() if user_info.deleted_on else None
            }
            
            user_type_dict = {
                "user_type_id": user_type_info.user_type_id,
                "type_name": user_type_info.type_name,
                "description": user_type_info.description,
                "default_page": user_type_info.default_page,
                "is_active": user_type_info.is_active,
                "created_at": user_type_info.created_at.isoformat() if user_type_info.created_at else None,
                "updated_at": user_type_info.updated_at.isoformat() if user_type_info.updated_at else None
            }
            
            return {
                "status": "success",
                "message": "Login successful.",
                "access_token": token,
                "session_id": session.session_id,
                "user_info": user_info_dict,
                "user_permission": user_permission_info,
                "user_type": user_type_dict,
                "user_type_name": user_type_info.type_name,
                "user_type_id": user_type_info.user_type_id,
                "default_page": user_type_info.default_page,
                "user_id": user_info.user_id
            }
            
        except HTTPException:
            raise
        except Exception as e:
            import traceback
            traceback.print_exc()  # Log the full traceback to server logs
            raise HTTPException(status_code=500, detail="Login failed due to an internal error.")

    def _check_suspicious_login(self, user_id: int, ip_address: str, device_info: str) -> bool:
        """Check if the login is suspicious based on IP and device info."""
        # This is a simplified check - in production, you'd have more sophisticated logic
        # For now, we'll just check if it's a new IP address
        try:
            # Get user's last login IP
            user = self.user_repo.get_user_by_id(user_id)
            if user.last_login_ip and user.last_login_ip != ip_address:
                return True
            return False
        except:
            return False

    # ---------------------- Logout User ----------------------

    def logout_user(self, token: str, ip_address: str = None, user_agent: str = None):
        """
        Logout a user by ending their session and writing an audit log.
        """
        try:
            # Fetch active session first to capture identifiers for audit logging
            session = self.auth_repo.get_active_session(token)

            # End the session (sets logout_timestamp internally)
            self.auth_repo.end_session(token)

            # Write audit log for logout action
            try:
                self.auth_repo.create_audit_log(
                    user_id=session.user_id,
                    action_type="LOGOUT",
                    table_name="user_sessions",
                    record_id=session.session_id,
                    old_values=None,
                    new_values={"session_ended": True},
                    ip_address=ip_address,
                    user_agent=user_agent,
                    session_id=str(session.session_id),
                )
            except Exception:
                # Do not fail logout if audit logging encounters an issue
                pass

            return {
                "status": "success",
                "message": "User logged out successfully."
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")

    # ---------------------- Change Password ----------------------

    def change_password(self, user_id: int, change_data: ChangePassword):
        """
        Change a user's password.
        """
        try:
            # Validate and update the password
            self.auth_repo.change_password(user_id, change_data)

            # Fetch the user for audit log
            user = self.auth_repo.get_user_by_id(user_id)

            # Create audit log for password change
            self.auth_repo.create_audit_log(
                user_id=user_id,
                action_type="PASSWORD_CHANGE",
                table_name="users",
                record_id=user_id,
                new_values={"password_changed": True},
                ip_address=None,
                user_agent=None
            )

            return {
                "status": "success",
                "message": "Password changed successfully."
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Password change failed: {str(e)}")

    # ---------------------- Forgot Password ----------------------

    def forgot_password(self, forgot_data: ForgotPassword):
        """
        Generate a reset token for password reset and send a secure email link.
        """
        try:
            # Generate a reset token
            reset_info = self.auth_repo.forgot_password(forgot_data)

            # Build reset link (frontend page should handle token + email)
            base_url = os.getenv("FRONTEND_BASE_URL", "http://localhost:8080")
            reset_path = os.getenv("FRONTEND_RESET_PATH", "/reset-password")
            reset_link = f"{base_url}{reset_path}?email={forgot_data.email}&token={reset_info['reset_token']}"

            # Send email with a branded HTML template
            html = f"""
            <div style='font-family:Arial,Helvetica,sans-serif;background:#f8fafc;padding:24px'>
              <table role='presentation' width='100%' cellpadding='0' cellspacing='0' style='max-width:640px;margin:0 auto;background:#ffffff;border-radius:8px;box-shadow:0 1px 6px rgba(0,0,0,0.06)'>
                <tr>
                  <td style='padding:24px 24px 8px 24px;'>
                    <h1 style='margin:0;color:#1e293b;font-size:20px;'>Reset your password</h1>
                  </td>
                </tr>
                <tr>
                  <td style='padding:0 24px 16px 24px;color:#334155;font-size:14px;line-height:1.6;'>
                    We received a request to reset the password for your AppointmentTech account.
                    Click the button below to reset your password. This link will expire in 24 hours.
                  </td>
                </tr>
                <tr>
                  <td style='padding:0 24px 24px 24px;'>
                    <a href='{reset_link}' style='display:inline-block;background:#2563eb;color:#ffffff;text-decoration:none;padding:12px 18px;border-radius:6px;font-weight:600'>Reset Password</a>
                  </td>
                </tr>
                <tr>
                  <td style='padding:0 24px 16px 24px;color:#64748b;font-size:12px;'>
                    If you did not request this, you can safely ignore this email. For security reasons, do not forward this email to anyone.
                  </td>
                </tr>
                <tr>
                  <td style='padding:0 24px 24px 24px;color:#94a3b8;font-size:12px;border-top:1px solid #e2e8f0;'>
                    AppointmentTech • Do not reply to this automated email
                  </td>
                </tr>
              </table>
            </div>
            """

            self.send_email(
                to_email=forgot_data.email,
                subject="Reset your AppointmentTech password",
                body=html,
            )

            # Create audit log for password reset request
            user = self.auth_repo.get_user_by_email(forgot_data.email)
            self.auth_repo.create_audit_log(
                user_id=user.user_id,
                action_type="PASSWORD_RESET_REQUEST",
                table_name="users",
                record_id=user.user_id,
                new_values={"reset_link_sent": True},
                ip_address=None,
                user_agent=None
            )

            return {
                "status": "success",
                "message": "Password reset link has been sent to your email."
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Password reset failed: {str(e)}")

    def reset_password(self, reset_data: ResetPassword):
        """
        Reset password using token (single-use).
        """
        try:
            # Reset password using token
            result = self.auth_repo.reset_password({
                'email': reset_data.email,
                'token': reset_data.token,
                'new_password': reset_data.new_password
            })

            # Create audit log for password reset
            user = self.auth_repo.get_user_by_email(reset_data.email)
            self.auth_repo.create_audit_log(
                user_id=user.user_id,
                action_type="PASSWORD_RESET",
                table_name="users",
                record_id=user.user_id,
                new_values={"password_reset": True},
                ip_address=None,
                user_agent=None
            )

            return {
                "status": "success",
                "message": "Password has been reset successfully. You can now log in with your new password."
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Password reset failed: {str(e)}")