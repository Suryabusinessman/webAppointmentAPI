from sqlalchemy.orm import Session
from app.models.UserModules.users import User
from app.repositories.UserModules.users import UserRepository
from app.repositories.UserModules.userpermissions import UserPermissionRepository
from app.repositories.UserModules.usertypes import UserTypeRepository
from datetime import datetime
import random
import string
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
import logging
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash a plain text password."""
    return pwd_context.hash(password)

class GoogleAuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.user_permission_repo = UserPermissionRepository(db)
        self.user_type_repo = UserTypeRepository(db)

    def generate_random_password(self, length: int = 12) -> str:
        """Generate a secure random password for Google OAuth users."""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(chars) for _ in range(length))

    # Removed create_access_token method - now using the same method as normal login

    # Removed _serialize_user_info method - now using the same format as normal login

    # Removed _serialize_user_type method - now using the same format as normal login

    def google_signin(self, email: str, full_name: str, picture: str, 
                      extra_fields: Optional[Dict] = None, 
                      device_info: Optional[str] = None, ip_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Handle Google OAuth sign-in for simple users only.
        Always creates users with user_type_id = 3 (Simple User).
        """
        try:
            # Check if user already exists
            existing_user = self.db.query(User).filter(
                User.email == email, 
                User.is_deleted == "N"
            ).first()
            
            if existing_user:
                # User exists, handle login flow
                return self._handle_existing_user_login(existing_user, device_info, ip_address)
            
            # User doesn't exist, handle registration flow
            return self._handle_new_user_registration(
                email, full_name, picture, extra_fields, device_info, ip_address
            )
            
        except Exception as e:
            logger.error(f"Error in Google signin: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Google signin failed: {str(e)}"
            )

    def _handle_existing_user_login(self, user: User, device_info: str, ip_address: str) -> Dict[str, Any]:
        """Handle login for existing Google OAuth users."""
        try:
            # Update last login information
            user.last_login_at = datetime.utcnow()
            user.last_login_ip = ip_address
            self.db.commit()
            
            # Create new session using the same method as normal login
            from app.services.UserModules.authservices import AuthService
            auth_service = AuthService(self.db)
            
            # Create access token using the same method as normal login
            from app.auth.jwt import create_access_token
            token = create_access_token(data={"sub": user.email})
            
            # Create session using the same method as normal login
            session = auth_service.auth_repo.create_session(user.user_id, token, device_info, ip_address)
            
            # Get user info and permissions (same as normal login)
            user_permission_info = self.user_permission_repo.get_user_permissions_with_pages(user.user_type_id)
            user_type_info = self.user_type_repo.get_by_id(user.user_type_id)
            
            # Ensure user_permission_info is always a list
            if user_permission_info is None:
                user_permission_info = []
            
            # Convert SQLAlchemy objects to dictionaries for proper serialization (same as normal login)
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
            
            # Return exact same format as normal login
            return {
                "status": "success",
                "message": "Google login successful.",
                "access_token": token,
                "session_id": session.session_id,
                "user_info": user_info_dict,
                "user_permission": user_permission_info,
                "user_type": user_type_dict,
                "user_type_name": user_type_info.type_name,
                "user_type_id": user_type_info.user_type_id,
                "default_page": user_type_info.default_page,
                "user_id": user.user_id
            }
            
        except Exception as e:
            logger.error(f"Error handling existing user login: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Login failed: {str(e)}"
            )

    def _handle_new_user_registration(self, email: str, full_name: str, picture: str, 
                                    extra_fields: Optional[Dict], device_info: str, 
                                    ip_address: str) -> Dict[str, Any]:
        """Handle registration for new Google OAuth users as simple users."""
        try:
            # Always set user_type_id to 3 (Simple User) for Google OAuth
            user_type_id = 3
            
            # Generate secure password for Google OAuth user
            secure_password = self.generate_random_password()
            password_hash = get_password_hash(secure_password)
            
            # Create new user
            user = User(
                email=email,
                full_name=full_name,
                profile_image=picture,
                password_hash=password_hash,
                is_verified=True,  # Google users are pre-verified
                is_active='Y',
                is_deleted='N',
                user_type_id=user_type_id,  # Always 3 for simple users
                added_on=datetime.utcnow(),
                last_login_at=datetime.utcnow(),
                last_login_ip=ip_address
            )
            
            # Add extra fields if provided
            if extra_fields:
                for field, value in extra_fields.items():
                    if hasattr(user, field) and value is not None:
                        setattr(user, field, value)
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            # Create session using the same method as normal login
            from app.services.UserModules.authservices import AuthService
            auth_service = AuthService(self.db)
            
            # Create access token using the same method as normal login
            from app.auth.jwt import create_access_token
            token = create_access_token(data={"sub": user.email})
            
            # Create session using the same method as normal login
            session = auth_service.auth_repo.create_session(user.user_id, token, device_info, ip_address)
            
            # Get user info and permissions (same as normal login)
            user_type_info = self.user_type_repo.get_by_id(user.user_type_id)
            user_permission_info = self.user_permission_repo.get_user_permissions_with_pages(user.user_type_id)
            
            # Ensure user_permission_info is always a list
            if user_permission_info is None:
                user_permission_info = []
            
            # Convert SQLAlchemy objects to dictionaries for proper serialization (same as normal login)
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
            
            # Return exact same format as normal login
            return {
                "status": "success",
                "message": "Google registration successful.",
                "access_token": token,
                "session_id": session.session_id,
                "user_info": user_info_dict,
                "user_permission": user_permission_info,
                "user_type": user_type_dict,
                "user_type_name": user_type_info.type_name,
                "user_type_id": user_type_info.user_type_id,
                "default_page": user_type_info.default_page,
                "user_id": user.user_id
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error handling new user registration: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {str(e)}"
            )

    # Legacy method removed - simplified to use only google_signin()
