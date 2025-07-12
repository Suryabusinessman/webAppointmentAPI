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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRepository:
    def __init__(self, db: Session):
        self.db = db  # Use the Session object directly

    def get_password_hash(self, password: str) -> str:
        """Hash a plain text password."""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a hashed password."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_all_users(self) -> List[User]:
        """Fetch all active users."""
        return self.db.query(User).filter(User.Is_Deleted == 'N').all()

    def get_user_by_id(self, user_id: int) -> User:
        """Fetch a user by their ID."""
        user = self.db.query(User).filter(User.User_Id == user_id, User.Is_Deleted == 'N').first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def get_user_by_email(self, email: str) -> User:
        """Fetch a user by their email."""
        return self.db.query(User).filter(User.Email == email, User.Is_Deleted == 'N').first()

    def get_users_by_name(self, name: str) -> List[User]:
        """Fetch users by their name (partial match)."""
        return self.db.query(User).filter(
            User.Full_Name.ilike(f"%{name}%"),
            User.Is_Deleted == 'N'
        ).all()

    # def create_user(self, user_data: UserCreate) -> User:
    #     """Create a new user."""
    #     if self.get_user_by_email(user_data.Email):
    #         raise HTTPException(status_code=400, detail="Email already registered")

    #     user = User(
    #         **user_data.dict(exclude={"Password"}),
    #         Password_Hash=self.get_password_hash(user_data.Password),
    #         Is_Active='Y',
    #         Is_Verified=False,
    #         Is_Deleted='N'
    #     )
    #     self.db.add(user)
    #     self.db.commit()
    #     self.db.refresh(user)
    #     return user

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        if self.get_user_by_email(user_data.Email):
            raise HTTPException(status_code=400, detail="Email already registered")

        # Exclude Confirm_Password and hash the password
        user = User(
            **user_data.dict(exclude={"Password", "Confirm_Password"}),  # Exclude Confirm_Password
            Password_Hash=self.get_password_hash(user_data.Password),  # Hash the password
            Is_Active='Y',
            Is_Verified=False,
            Is_Deleted='N'
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    # def register_user(self, data: RegisterUser) -> User:
    #     """Register a new user."""
    #     if data.Password != data.Confirm_Password:
    #         raise HTTPException(status_code=400, detail="Passwords do not match")
    #     return self.create_user(data)
    def register_user(self, data: RegisterUser) -> User:
        """Register a new user."""
        if data.Password != data.Confirm_Password:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        # Pass the data to create_user after validation
        return self.create_user(data)

    def login_user(self, data: UserLogin) -> User:
        """Authenticate a user."""
        user = self.get_user_by_email(data.Email)
        if not user or not self.verify_password(data.Password, user.Password_Hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user

    def update_user(self, user_id: int, data: UserUpdate) -> User:
        """Update an existing user."""
        user = self.get_user_by_id(user_id)
        update_data = data.dict(exclude_unset=True)

        if "Password" in update_data:
            user.Password_Hash = self.get_password_hash(update_data.pop("Password"))

        for field, value in update_data.items():
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> dict:
        """Soft delete a user by their ID."""
        user = self.get_user_by_id(user_id)
        user.Is_Deleted = 'Y'
        self.db.commit()
        return {"message": "User deleted successfully"}

    def forgot_password(self, data: ForgotPassword) -> dict:
        """Generate a reset token for a user."""
        user = self.get_user_by_email(data.Email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        token = secrets.token_urlsafe(32)
        user.Forgot_Token = token
        self.db.commit()
        # Here you can trigger email logic
        return {"message": "Reset link sent", "token": token}

    def change_password(self, user_id: int, data: ChangePassword) -> dict:
        """Change a user's password."""
        user = self.get_user_by_id(user_id)

        if not self.verify_password(data.Current_Password, user.Password_Hash):
            raise HTTPException(status_code=400, detail="Invalid current password")

        if data.New_Password != data.Confirm_Password:
            raise HTTPException(status_code=400, detail="Passwords do not match")

        user.Password_Hash = self.get_password_hash(data.New_Password)
        self.db.commit()
        return {"message": "Password updated successfully"}

    def update_profile(self, user_id: int, data: ProfileUpdate) -> User:
        """Update a user's profile."""
        user = self.get_user_by_id(user_id)
        update_data = data.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user