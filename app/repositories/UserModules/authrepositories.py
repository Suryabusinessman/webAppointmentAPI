from sqlalchemy.orm import Session
from app.models.UserModules.users import User
from app.models.UserModules.authmodules import UserSession, EmailOTP
from app.models.BusinessModules.businessmanuser import BusinessUser
from app.models.common import AuditLog, Notification
from app.schemas.UserModules.users import (
    RegisterUser, UserLogin, ChangePassword, ForgotPassword, DynamicRegisterUser, BusinessRegistrationData
)
from datetime import datetime, timedelta
from secrets import token_urlsafe
from passlib.context import CryptContext
from fastapi import HTTPException, status
import json

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------------------- Utility Functions ----------------------

    def get_password_hash(self, password: str) -> str:
        """Hash a plain text password."""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a hashed password."""
        return pwd_context.verify(plain_password, hashed_password)

    # ---------------------- User Management ----------------------

    def get_user_by_email(self, email: str) -> User:
        """Fetch a user by their email with enhanced error handling."""
        try:
            user = self.db.query(User).filter(User.email == email, User.is_deleted == "N").first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

    def get_user_by_id(self, user_id: int) -> User:
        """Fetch a user by their ID with enhanced error handling."""
        try:
            user = self.db.query(User).filter(User.user_id == user_id, User.is_deleted == "N").first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

    def create_user(self, user_data: RegisterUser) -> User:
        """Register a new user with enhanced validation and security."""
        try:
            # Check if email already exists
            if self.db.query(User).filter(User.email == user_data.email, User.is_deleted == "N").first():
                raise HTTPException(status_code=400, detail="Email already registered")

            # Validate passwords match
            if user_data.password != user_data.confirm_password:
                raise HTTPException(status_code=400, detail="Passwords do not match")

            # Validate password strength
            if len(user_data.password) < 8:
                raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

            # Hash password
            hashed_password = self.get_password_hash(user_data.password)

            # Create user
            new_user = User(
                full_name=user_data.full_name,
                email=user_data.email,
                password_hash=hashed_password,
                user_type_id=user_data.user_type_id,
                phone=user_data.phone,
                alt_phone=user_data.alt_phone,
                gender=user_data.gender,
                address=user_data.address,
                postal_code=user_data.postal_code,
                city=user_data.city,
                state=user_data.state,
                is_active="Y",
                is_verified=False,
                is_deleted="N",
                failed_login_attempts=0,
                two_factor_enabled=False,
                added_on=datetime.utcnow()
            )
            
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            
            return new_user
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

    def create_user_dynamic(self, user_data: DynamicRegisterUser) -> User:
        """Create a new user with dynamic registration and enhanced security."""
        try:
            # Check if email already exists
            if self.db.query(User).filter(User.email == user_data.email, User.is_deleted == "N").first():
                raise HTTPException(status_code=400, detail="This email is already registered.")

            # Check if phone already exists (if provided)
            if getattr(user_data, 'phone', None):
                existing_phone = self.db.query(User).filter(
                    User.phone == user_data.phone,
                    User.is_deleted == "N"
                ).first()
                if existing_phone:
                    raise HTTPException(status_code=400, detail="This phone number is already registered.")

            # Validate passwords match
            if user_data.password != user_data.confirm_password:
                raise HTTPException(status_code=400, detail="Passwords do not match")

            # Validate password strength
            if len(user_data.password) < 8:
                raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")

            # Validate phone format (if provided): 10-15 digits
            if user_data.phone:
                digits = ''.join(ch for ch in user_data.phone if ch.isdigit())
                if len(digits) < 10 or len(digits) > 15:
                    raise HTTPException(status_code=400, detail="Invalid phone number. Provide 10-15 digits.")

            # Hash password
            hashed_password = self.get_password_hash(user_data.password)

            # Create user
            new_user = User(
                full_name=user_data.full_name,
                email=user_data.email,
                password_hash=hashed_password,
                user_type_id=user_data.user_type_id,
                phone=user_data.phone,
                alt_phone=user_data.alt_phone,
                gender=user_data.gender,
                address=user_data.address,
                city=user_data.city,
                state=user_data.state,
                postal_code=user_data.postal_code,
                is_active="Y",
                is_verified=False,
                is_deleted="N",
                failed_login_attempts=0,
                two_factor_enabled=False,
                added_on=datetime.utcnow()
            )
            
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            
            return new_user
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            # Map common SQLAlchemy errors to user-friendly messages
            msg = str(e)
            if ("Duplicate entry" in msg or "UNIQUE constraint" in msg):
                if "email" in msg or "users.email" in msg:
                    raise HTTPException(status_code=400, detail="This email is already registered.")
                if "phone" in msg or "users.phone" in msg:
                    raise HTTPException(status_code=400, detail="This phone number is already registered.")
                # Fallback duplicate
                raise HTTPException(status_code=400, detail="Duplicate value provided.")
            
    def create_business_user(self, user: User, business_data: BusinessRegistrationData) -> BusinessUser:
        """Create business user records for multiple business types."""
        business_users = []
        
        for business_type_id in business_data.business_type_ids:
            business_user = BusinessUser(
                user_id=user.user_id,
                user_type_id=user.user_type_id,
                business_type_id=business_type_id,
                business_name=business_data.business_name,
                business_description=business_data.business_description,
                business_phone=business_data.business_phone,
                business_email=business_data.business_email,
                business_address=business_data.business_address,
                business_website=business_data.business_website,
                gst_number=business_data.gst_number,
                pan_number=business_data.pan_number,
                business_license=business_data.business_license,
                is_verified="N",
                is_featured="N",
                rating=0.00,
                total_reviews=0,
                added_on=datetime.utcnow()
            )
            
            self.db.add(business_user)
            business_users.append(business_user)
        
        self.db.commit()
        
        # Refresh all business users to get their IDs
        for bu in business_users:
            self.db.refresh(bu)
        
        return business_users

    def create_audit_log(self, user_id: int, action_type: str, table_name: str, 
                        record_id: int, old_values: dict = None, new_values: dict = None,
                        ip_address: str = None, user_agent: str = None, session_id: str = None):
        """Create audit log entry."""
        audit_log = AuditLog(
            user_id=user_id,
            action_type=action_type,
            table_name=table_name,
            record_id=record_id,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            created_at=datetime.utcnow()
        )
        
        self.db.add(audit_log)
        self.db.commit()
        return audit_log

    def create_notification(self, user_id: int, title: str, message: str, 
                          notification_type: str = "INFO", priority: str = "MEDIUM"):
        """Create notification for user."""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            is_read="N",
            created_at=datetime.utcnow()
        )
        
        self.db.add(notification)
        self.db.commit()
        return notification

    # def login_user(self, login_data: UserLogin) -> User:
    #     """Authenticate a user."""
    #     user = self.get_user_by_email(login_data.Email)
    #     print('--------------', user.Password_Hash, login_data.Password)
    #     if user.Is_Deleted == "Y":
    #         raise HTTPException(status_code=400, detail="User account is deleted")
        
    #     if not self.verify_password(login_data.Password, user.Password_Hash):
    #         raise HTTPException(status_code=401, detail="Invalid credentials")
    #     return user

    def login_user(self, login_data: UserLogin) -> User:
        """Authenticate a user with enhanced security."""
        try:
            # Get user by email
            user = self.get_user_by_email(login_data.email)
            
            # Check if user exists
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Check if user is marked deleted
            if user.is_deleted == "Y":
                raise HTTPException(status_code=400, detail="User account is deleted")

            # Check if user is active
            if user.is_active == "N":
                raise HTTPException(status_code=400, detail="User account is inactive")

            # Check if account is locked
            if user.account_locked_until and user.account_locked_until > datetime.utcnow():
                raise HTTPException(status_code=423, detail="Account is temporarily locked due to multiple failed login attempts")

            # Verify password
            if not self.verify_password(login_data.password, user.password_hash):
                # Increment failed login attempts
                user.failed_login_attempts += 1
                
                # Lock account if too many failed attempts
                if user.failed_login_attempts >= 5:
                    user.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
                
                self.db.commit()
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Reset failed login attempts on successful login
            user.failed_login_attempts = 0
            user.account_locked_until = None
            user.last_login_at = datetime.utcnow()
            user.last_login_ip = login_data.ip_address if hasattr(login_data, 'ip_address') else None
            
            self.db.commit()
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

    def change_password(self, user_id: int, change_data: ChangePassword) -> dict:
        """Change user password."""
        user = self.get_user_by_id(user_id)
        
        # Verify current password
        if not self.verify_password(change_data.current_password, user.password_hash):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Hash new password
        new_hashed_password = self.get_password_hash(change_data.new_password)
        
        # Update password
        user.password_hash = new_hashed_password
        user.modified_on = datetime.utcnow()
        
        self.db.commit()
        
        return {"message": "Password changed successfully"}

    def forgot_password(self, forgot_data: ForgotPassword) -> dict:
        """Generate password reset token (single-use)."""
        # Look up user without raising to provide a friendly message if not found
        user = self.db.query(User).filter(User.email == forgot_data.email, User.is_deleted == "N").first()
        if not user:
            raise HTTPException(status_code=404, detail="This email is not registered with us. Please check and try again.")
        
        # Clear any existing reset tokens first
        user.reset_token = None
        user.reset_token_expires = None
        
        # Generate new reset token
        reset_token = token_urlsafe(32)
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=24)
        
        self.db.commit()
        
        # Return token to service layer (not exposed to clients)
        return {"message": "Password reset token generated", "reset_token": reset_token, "expires_at": user.reset_token_expires}

    def reset_password(self, reset_data: dict) -> dict:
        """Reset password using token (single-use)."""
        user = self.get_user_by_email(reset_data['email'])
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if token exists and is valid
        if not user.reset_token or not user.reset_token_expires:
            raise HTTPException(status_code=400, detail="No reset token found")
        
        # Check if token matches
        if user.reset_token != reset_data['token']:
            raise HTTPException(status_code=400, detail="Invalid reset token")
        
        # Check if token is expired
        if user.reset_token_expires < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Reset token has expired")
        
        # Hash new password
        new_hashed_password = self.get_password_hash(reset_data['new_password'])
        
        # Update password and clear token (single-use)
        user.password_hash = new_hashed_password
        user.reset_token = None  # Clear token after use
        user.reset_token_expires = None  # Clear expiration
        user.modified_on = datetime.utcnow()
        
        self.db.commit()
        
        return {"message": "Password reset successfully"}

    def create_session(self, user_id: int, token: str, device_info: str, ip_address: str, expires_in_minutes: int = 60) -> UserSession:
        """Create a new user session."""
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        
        session = UserSession(
            user_id=user_id,
            token=token,
            device_info=device_info,
            ip_address=ip_address,
            is_active=True,
            expires_at=expires_at,
            login_timestamp=datetime.utcnow()
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return session

    # ---------------------- Email OTP ----------------------

    def _hash_otp(self, otp: str) -> str:
        from hashlib import sha256
        return sha256(otp.encode()).hexdigest()

    def create_or_update_email_otp(self, email: str, user_id: int = None, purpose: str = "EMAIL_VERIFICATION", ttl_minutes: int = 10) -> tuple[EmailOTP, str]:
        """Create a new OTP or update existing pending OTP for an email. Returns (record, plain_otp)."""
        otp_plain = str(__import__("random").randint(100000, 999999))
        otp_hash = self._hash_otp(otp_plain)

        record = self.db.query(EmailOTP).filter(
            EmailOTP.email == email,
            EmailOTP.purpose == purpose,
            EmailOTP.is_used == False,
        ).first()

        expires_at = datetime.utcnow() + timedelta(minutes=ttl_minutes)

        if record:
            # Rate limit sends
            now = datetime.utcnow()
            if record.last_sent_at and (now - record.last_sent_at).seconds < 60:
                raise HTTPException(status_code=429, detail="Please wait before requesting another OTP.")

            record.otp_hash = otp_hash
            record.expires_at = expires_at
            record.last_sent_at = datetime.utcnow()
            record.send_count = (record.send_count or 0) + 1
        else:
            record = EmailOTP(
                user_id=user_id,
                email=email,
                otp_hash=otp_hash,
                purpose=purpose,
                attempts=0,
                is_used=False,
                created_at=datetime.utcnow(),
                expires_at=expires_at,
                last_sent_at=datetime.utcnow(),
                send_count=1,
            )
            self.db.add(record)

        self.db.commit()
        self.db.refresh(record)
        return record, otp_plain

    def verify_email_otp(self, email: str, otp: str, purpose: str = "EMAIL_VERIFICATION") -> bool:
        record = self.db.query(EmailOTP).filter(
            EmailOTP.email == email,
            EmailOTP.purpose == purpose,
            EmailOTP.is_used == False,
        ).order_by(EmailOTP.created_at.desc()).first()

        if not record:
            raise HTTPException(status_code=400, detail="No pending OTP found")

        # Expiry check
        if record.expires_at < datetime.utcnow():
            raise HTTPException(status_code=400, detail="OTP has expired")

        # Attempts limit
        if record.attempts >= 5:
            raise HTTPException(status_code=429, detail="Too many invalid attempts")

        # Verify OTP
        if self._hash_otp(otp) != record.otp_hash:
            record.attempts += 1
            self.db.commit()
            raise HTTPException(status_code=400, detail="Invalid OTP")

        # Success: mark used
        record.is_used = True
        record.used_at = datetime.utcnow()
        self.db.commit()
        return True

    def get_active_session(self, token: str) -> UserSession:
        """Get active session by token."""
        session = self.db.query(UserSession).filter(
            UserSession.token == token,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            raise HTTPException(status_code=401, detail="Invalid or expired session")
        
        return session

    def end_session(self, token: str):
        """End a user session. If the session is already inactive/expired, still stamp logout time."""
        # Try to find any session by token (active or not)
        session = self.db.query(UserSession).filter(UserSession.token == token).first()
        if not session:
            raise HTTPException(status_code=401, detail="Invalid or expired session")

        # Ensure is_active is set to False
        if session.is_active:
            session.is_active = False

        # Always stamp logout timestamp (idempotent)
        session.logout_timestamp = datetime.utcnow()

        self.db.commit()

        return {"message": "Session ended successfully"}