from sqlalchemy.orm import Session
from app.models.UserModules.users import User
from app.models.UserModules.authmodules import UserSession
from app.schemas.UserModules.users import (
    RegisterUser, UserLogin, ChangePassword, ForgotPassword
)
from datetime import datetime, timedelta
from secrets import token_urlsafe
from passlib.context import CryptContext
from fastapi import HTTPException, status

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
        """Fetch a user by their email."""
        user = self.db.query(User).filter(User.Email == email, User.Is_Deleted == "N").first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def get_user_by_id(self, user_id: int) -> User:
        """Fetch a user by their ID."""
        user = self.db.query(User).filter(User.User_Id == user_id, User.Is_Deleted == "N").first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def create_user(self, user_data: RegisterUser) -> User:
        """Register a new user."""
        if self.db.query(User).filter(User.Email == user_data.Email, User.Is_Deleted == "N").first():
            raise HTTPException(status_code=400, detail="Email already registered")

        if user_data.Password != user_data.Confirm_Password:
            raise HTTPException(status_code=400, detail="Passwords do not match")

        hashed_password = self.get_password_hash(user_data.Password)
        new_user = User(
            Full_Name=user_data.Full_Name,
            Email=user_data.Email,
            Password_Hash=hashed_password,
            User_Type_Id=user_data.User_Type_Id,
            Phone=user_data.Phone,
            Alt_Phone=user_data.Alt_Phone,
            Gender=user_data.Gender,
            Address=user_data.Address,
            Postal_Code=user_data.Postal_Code,
            City=user_data.City,
            State=user_data.State,
            Is_Active="Y",
            Is_Verified=False,
            Is_Deleted="N",
            Added_On=datetime.utcnow()
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

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
        """Authenticate a user."""
        user = self.get_user_by_email(login_data.Email)
        # Check if user exists
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if user is marked deleted
        if user.Is_Deleted == "Y":
            raise HTTPException(status_code=400, detail="User account is deleted")

        # Check password
        if not self.verify_password(login_data.Password, user.Password_Hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return user

    def change_password(self, user_id: int, change_data: ChangePassword) -> dict:
        """Change a user's password."""
        user = self.get_user_by_id(user_id)

        if not self.verify_password(change_data.Current_Password, user.Password_Hash):
            raise HTTPException(status_code=400, detail="Invalid current password")

        if change_data.New_Password != change_data.Confirm_Password:
            raise HTTPException(status_code=400, detail="Passwords do not match")

        user.Password_Hash = self.get_password_hash(change_data.New_Password)
        user.Modified_On = datetime.utcnow()
        self.db.commit()
        return {"message": "Password updated successfully"}

    def forgot_password(self, forgot_data: ForgotPassword) -> dict:
        """Generate a reset token for a user."""
        user = self.get_user_by_email(forgot_data.Email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        reset_token = token_urlsafe(32)
        user.Forgot_Token = reset_token
        user.Forgot_Token_Expiry = datetime.utcnow() + timedelta(minutes=15)
        self.db.commit()

        # Placeholder for sending the reset token via email
        # You can integrate an email service here
        return {"message": "Password reset link sent to your email", "reset_token": reset_token}

    # ---------------------- Session Management ----------------------

    def create_session(self, user_id: int, token: str, device_info: str, ip_address: str, expires_in_minutes: int = 60) -> UserSession:
        """Create a new user session."""
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        session = UserSession(
            User_Id=user_id,
            Token=token,
            Device_Info=device_info,
            IP_Address=ip_address,
            Expires_At=expires_at,
            Is_Active=True,
            Created_At=datetime.utcnow()
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_active_session(self, token: str) -> UserSession:
        """Fetch an active session by token."""
        session = self.db.query(UserSession).filter(UserSession.Token == token, UserSession.Is_Active == True).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or inactive")
        return session

    def end_session(self, token: str):
        """End a user session."""
        session = self.get_active_session(token)
        session.Is_Active = False
        session.Logout_Timestamp = datetime.utcnow()
        self.db.commit()
        return {"message": "Session ended successfully"}