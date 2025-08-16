from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.UserModules.users import User
from app.schemas.UserModules.users import (
    UserCreate, UserUpdate, RegisterUser, UserLogin, ChangePassword,
    ForgotPassword, ProfileUpdate
)
from fastapi import HTTPException, status
from passlib.context import CryptContext
from typing import List
import secrets
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_password_hash(self, password: str) -> str:
        """Hash a plain text password."""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a hashed password."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_all_users(self) -> List[User]:
        """Fetch all active users with enhanced error handling."""
        try:
            users = self.db.query(User).filter(User.is_deleted == 'N').all()
            if not users:
                raise HTTPException(status_code=404, detail="No users found")
            return users
        except HTTPException:
            raise
        except Exception as e:
            # Check if it's a database connection error
            if "Can't connect to MySQL server" in str(e) or "Connection refused" in str(e):
                raise HTTPException(
                    status_code=503, 
                    detail="Database connection failed. Please ensure MySQL server is running."
                )
            elif "Access denied" in str(e):
                raise HTTPException(
                    status_code=503, 
                    detail="Database access denied. Please check database credentials."
                )
            else:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Database error: {str(e)}"
                )

    def get_user_by_id(self, user_id: int) -> User:
        """Fetch a user by their ID with enhanced error handling."""
        try:
            user = self.db.query(User).filter(User.user_id == user_id, User.is_deleted == 'N').first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to retrieve user information. Please try again later.")

    def get_user_by_email(self, email: str) -> User:
        """Fetch a user by their email with enhanced error handling."""
        try:
            user = self.db.query(User).filter(User.email == email, User.is_deleted == 'N').first()
            return user  # Return None if not found, don't raise exception
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to retrieve user by email. Please try again later.")

    def get_users_by_name(self, name: str) -> List[User]:
        """Fetch users by their name (partial match) with enhanced error handling."""
        try:
            users = self.db.query(User).filter(
                User.full_name.ilike(f"%{name}%"),
                User.is_deleted == 'N'
            ).all()
            if not users:
                raise HTTPException(status_code=404, detail="No users found with that name")
            return users
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to search users by name. Please try again later.")

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user with enhanced validation and security."""
        try:
            # Check if email already exists
            existing_user = self.get_user_by_email(user_data.email)
            if existing_user:
                raise HTTPException(status_code=400, detail="This email is already registered.")

            # Phone duplicate check if provided
            if user_data.phone:
                dup_phone = self.db.query(User).filter(User.phone == user_data.phone, User.is_deleted == 'N').first()
                if dup_phone:
                    raise HTTPException(status_code=400, detail="This phone number is already registered.")

            # Validate password strength
            if len(user_data.password) < 8:
                raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

            # Create user
            user = User(
                full_name=user_data.full_name,
                email=user_data.email,
                password_hash=self.get_password_hash(user_data.password),
                user_type_id=user_data.user_type_id,
                phone=user_data.phone,
                alt_phone=user_data.alt_phone,
                bio=user_data.bio,
                website=user_data.website,
                social_links=user_data.social_links,
                gender=user_data.gender,
                occupation=user_data.occupation,
                company_name=user_data.company_name,
                gst_number=user_data.gst_number,
                referral_code=user_data.referral_code,
                address=user_data.address,
                city=user_data.city,
                state=user_data.state,
                country=user_data.country,
                postal_code=user_data.postal_code,
                preferred_language=user_data.preferred_language,
                wallet_balance=user_data.wallet_balance,
                currency=user_data.currency,
                is_wallet_enabled=user_data.is_wallet_enabled.upper() == "Y" if user_data.is_wallet_enabled else False,
                profile_image=user_data.profile_image,
                background_image=user_data.background_image,
                is_verified=user_data.is_verified.upper() == "Y" if user_data.is_verified else False,
                is_active=user_data.is_active
            )

            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create user. Please check your data and try again.")

    def register_user(self, data: RegisterUser) -> User:
        """Register a new user with enhanced validation."""
        try:
            # Check if email already exists
            existing_user = self.get_user_by_email(data.email)
            if existing_user:
                raise HTTPException(status_code=400, detail="This email is already registered.")

            # Phone duplicate check if provided
            if data.phone:
                dup_phone = self.db.query(User).filter(User.phone == data.phone, User.is_deleted == 'N').first()
                if dup_phone:
                    raise HTTPException(status_code=400, detail="This phone number is already registered.")

            # Validate password strength
            if len(data.password) < 8:
                raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

            # Create user
            user = User(
                full_name=data.full_name,
                email=data.email,
                password_hash=self.get_password_hash(data.password),
                user_type_id=data.user_type_id,
                phone=data.phone,
                alt_phone=data.alt_phone,
                gender=data.gender,
                address=data.address,
                city=data.city,
                state=data.state,
                postal_code=data.postal_code
            )

            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to register user. Please check your data and try again.")

    def login_user(self, data: UserLogin) -> User:
        """Authenticate a user with enhanced security."""
        try:
            user = self.get_user_by_email(data.email)
            if not user:
                raise HTTPException(status_code=401, detail="Invalid credentials")

            if not self.verify_password(data.password, user.password_hash):
                raise HTTPException(status_code=401, detail="Invalid credentials")

            if user.is_active == 'N':
                raise HTTPException(status_code=400, detail="User account is inactive")

            return user

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail="Login failed. Please check your credentials and try again.")

    def update_user(self, user_id: int, data: UserUpdate) -> User:
        """Update an existing user with enhanced validation."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Update fields if provided
            if data.full_name is not None:
                user.full_name = data.full_name
            if data.email is not None:
                # Check if new email already exists
                existing_user = self.get_user_by_email(data.email)
                if existing_user and existing_user.user_id != user_id:
                    raise HTTPException(status_code=400, detail="This email is already registered.")
                user.email = data.email
            if data.phone is not None:
                if data.phone:
                    dup_phone = self.db.query(User).filter(User.phone == data.phone, User.user_id != user_id, User.is_deleted == 'N').first()
                    if dup_phone:
                        raise HTTPException(status_code=400, detail="This phone number is already registered.")
                user.phone = data.phone
            if data.user_type_id is not None:
                user.user_type_id = data.user_type_id
            if data.profile_image is not None:
                user.profile_image = data.profile_image
            if data.background_image is not None:
                user.background_image = data.background_image
            if data.is_verified is not None:
                user.is_verified = data.is_verified.upper() == "Y" if data.is_verified else False
            if data.is_active is not None:
                user.is_active = data.is_active
            if data.alt_phone is not None:
                user.alt_phone = data.alt_phone
            if data.bio is not None:
                user.bio = data.bio
            if data.website is not None:
                user.website = data.website
            if data.social_links is not None:
                user.social_links = data.social_links
            if data.gender is not None:
                user.gender = data.gender
            if data.occupation is not None:
                user.occupation = data.occupation
            if data.company_name is not None:
                user.company_name = data.company_name
            if data.gst_number is not None:
                user.gst_number = data.gst_number
            if data.referral_code is not None:
                user.referral_code = data.referral_code
            if data.address is not None:
                user.address = data.address
            if data.city is not None:
                user.city = data.city
            if data.state is not None:
                user.state = data.state
            if data.country is not None:
                user.country = data.country
            if data.postal_code is not None:
                user.postal_code = data.postal_code
            if data.preferred_language is not None:
                user.preferred_language = data.preferred_language
            if data.wallet_balance is not None:
                user.wallet_balance = data.wallet_balance
            if data.currency is not None:
                user.currency = data.currency
            if data.is_wallet_enabled is not None:
                user.is_wallet_enabled = data.is_wallet_enabled.upper() == "Y" if data.is_wallet_enabled else False

            self.db.commit()
            self.db.refresh(user)
            return user

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to update user. Please check your data and try again.")

    def delete_user(self, user_id: int) -> dict:
        """Soft delete a user with enhanced error handling."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            user.is_deleted = 'Y'
            user.deleted_on = datetime.utcnow()
            self.db.commit()

            return {"message": "User deleted successfully", "user_id": user_id}

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to delete user. Please try again later.")

    def forgot_password(self, data: ForgotPassword) -> dict:
        """Handle forgot password with enhanced security."""
        try:
            user = self.get_user_by_email(data.email)
            if not user:
                # Don't reveal if email exists or not for security
                return {"message": "If email exists, reset instructions have been sent"}

            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            user.reset_token = reset_token
            user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)

            self.db.commit()
            return {"message": "Password reset instructions sent to email"}

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to process password reset. Please try again later.")

    def change_password(self, user_id: int, data: ChangePassword) -> dict:
        """Change user password with enhanced security."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Verify current password
            if not self.verify_password(data.current_password, user.password_hash):
                raise HTTPException(status_code=401, detail="Current password is incorrect")

            # Validate new password
            if len(data.new_password) < 8:
                raise HTTPException(status_code=400, detail="New password must be at least 8 characters long")

            # Update password
            user.password_hash = self.get_password_hash(data.new_password)
            self.db.commit()

            return {"message": "Password changed successfully"}

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to change password. Please check your current password and try again.")

    def update_profile(self, user_id: int, data: ProfileUpdate) -> User:
        """Update user profile with enhanced validation."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Update profile fields if provided
            if data.full_name is not None:
                user.full_name = data.full_name
            if data.phone is not None:
                user.phone = data.phone
            if data.profile_image is not None:
                user.profile_image = data.profile_image
            if data.background_image is not None:
                user.background_image = data.background_image
            if data.bio is not None:
                user.bio = data.bio
            if data.website is not None:
                user.website = data.website
            if data.social_links is not None:
                user.social_links = data.social_links
            if data.gender is not None:
                user.gender = data.gender
            if data.occupation is not None:
                user.occupation = data.occupation
            if data.company_name is not None:
                user.company_name = data.company_name
            if data.address is not None:
                user.address = data.address
            if data.city is not None:
                user.city = data.city
            if data.state is not None:
                user.state = data.state
            if data.postal_code is not None:
                user.postal_code = data.postal_code

            self.db.commit()
            self.db.refresh(user)
            return user

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to update profile. Please check your data and try again.")

    def activate_user(self, user_id: int) -> User:
        """Activate a user."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            user.is_active = 'Y'
            self.db.commit()
            self.db.refresh(user)
            return user

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to activate user. Please try again later.")

    def deactivate_user(self, user_id: int) -> User:
        """Deactivate a user."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            user.is_active = 'N'
            self.db.commit()
            self.db.refresh(user)
            return user

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to deactivate user. Please try again later.")

    def get_active_users(self) -> List[User]:
        """Get all active users."""
        try:
            users = self.db.query(User).filter(
                User.is_active == 'Y',
                User.is_deleted == 'N'
            ).all()
            return users
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to retrieve active users. Please try again later.")

    def get_inactive_users(self) -> List[User]:
        """Get all inactive users."""
        try:
            users = self.db.query(User).filter(
                User.is_active == 'N',
                User.is_deleted == 'N'
            ).all()
            return users
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to retrieve inactive users. Please try again later.")

    def increment_failed_login_attempts(self, user_id: int):
        """Increment failed login attempts and lock account if necessary."""
        try:
            user = self.get_user_by_id(user_id)
            user.failed_login_attempts += 1
            
            # Lock account if too many failed attempts
            if user.failed_login_attempts >= 5:
                user.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
            
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating login attempts: {str(e)}")

    def reset_failed_login_attempts(self, user_id: int):
        """Reset failed login attempts."""
        try:
            user = self.get_user_by_id(user_id)
            user.failed_login_attempts = 0
            user.account_locked_until = None
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error resetting login attempts: {str(e)}")

    def update_last_login(self, user_id: int):
        """Update last login timestamp."""
        try:
            user = self.get_user_by_id(user_id)
            user.last_login_at = datetime.utcnow()
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating last login: {str(e)}")

    def set_reset_token(self, user_id: int, reset_token: str):
        """Set password reset token."""
        try:
            user = self.get_user_by_id(user_id)
            user.reset_token = reset_token
            user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error setting reset token: {str(e)}")

    def update_password(self, user_id: int, new_password_hash: str):
        """Update user password."""
        try:
            user = self.get_user_by_id(user_id)
            user.password_hash = new_password_hash
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating password: {str(e)}")