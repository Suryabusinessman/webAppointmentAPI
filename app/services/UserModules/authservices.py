from sqlalchemy.orm import Session
from app.repositories.UserModules.authrepositories import AuthRepository
from app.repositories.UserModules.users import UserRepository
from app.repositories.UserModules.userpermissions import UserPermissionRepository
from app.repositories.UserModules.usertypes import UserTypeRepository
from app.schemas.UserModules.users import (
    RegisterUser, UserLogin, ChangePassword, ForgotPassword
)
from app.services.UserModules.users import create_access_token
from app.core.config import Config as settings
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
import smtplib
from email.mime.text import MIMEText

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
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_SENDER
        msg["To"] = to_email

        try:
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(msg["From"], [msg["To"]], msg.as_string())
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

    def validate_token(self, token: str):
        """Validate a JWT token and check its expiry."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
                raise HTTPException(status_code=401, detail="Token has expired")
            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    # ---------------------- Register User ----------------------

    def register_user(self, user_data: RegisterUser, device_info: str, ip_address: str):
        """
        Register a new user, create a session, and send a welcome email.
        """
        # Validate and create the user
        user = self.auth_repo.create_user(user_data)
        
        # Create a session for the user
        token = create_access_token(data={"sub": user.Email})
        session = self.auth_repo.create_session(user.User_Id, token, device_info, ip_address)
        # user = self.auth_repo.login_user(login_data)
        userInfo = self.user_repo.get_user_by_email(user_data.Email)
        userTypeInfo = self.user_type_repo.get_by_id(user_data.User_Type_Id)
        userPermissionInfo = self.user_permission_repo.get_user_permissions_with_pages(userInfo.User_Type_Id)

        # if not userPermissionInfo:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="User does not have permission to access this page."
        #     )
        # Send a welcome email
        # email_subject = "Welcome to Our Platform"
        # email_body = f"Hi {user.Full_Name},\n\nThank you for registering with us. Your account has been successfully created."
        # self.send_email(user.Email, email_subject, email_body)
        return {
            "message": "User registered successfully. A welcome email has been sent.",
            "access_token": token,
            "session_id": session.Session_Id,
            "user_info": user,
            "user_type_data": userTypeInfo,
            "user_type_name": userTypeInfo.User_Type_Name,
            "user_type_id": userTypeInfo.User_Type_Id,
            "default_page": userTypeInfo.Default_Page,
            "user_id": user.User_Id,
            "user_type": user.User_Type_Id,
            "user_permission": userPermissionInfo,
            # "page_id": userPermissionInfo.User_Type_Id
        }
    

    # ---------------------- Login User ----------------------

    def login_user(self, login_data: UserLogin, device_info: str, ip_address: str):
        """
        Authenticate a user, create a session, and enforce password policy.
        """
        # Validate user credentials
        user = self.auth_repo.login_user(login_data)
        userInfo = self.user_repo.get_user_by_email(login_data.Email)
        userPermissionInfo = self.user_permission_repo.get_user_permissions_with_pages(userInfo.User_Type_Id)
        userTypeInfo = self.user_type_repo.get_by_id(userInfo.User_Type_Id)
        # Check if user has permission to access the page
        if not userPermissionInfo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to access this page."
            )
        # Check if user exists and is not deleted
        if not userInfo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        if userInfo.Is_Deleted == "Y":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is deleted."
            )
        if not self.verify_password(login_data.Password, userInfo.Password_Hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials."
            )
        

        # Enforce password policy
        if len(login_data.Password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long."
            )
        if not any(char.isdigit() for char in login_data.Password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one digit."
            )
        if not any(char.isupper() for char in login_data.Password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one uppercase letter."
            )

        # Create a session for the user
        token = create_access_token(data={"sub": user.Email})
        session = self.auth_repo.create_session(user.User_Id, token, device_info, ip_address)

        return {
            "message": "Login successful.",
            "access_token": token,
            "session_id": session.Session_Id,
            "user_info": userInfo,
            "user_permission": userPermissionInfo,
            "user_type": userTypeInfo,
            "user_type_name": userTypeInfo.User_Type_Name,
            "user_type_id": userTypeInfo.User_Type_Id,
            "default_page": userTypeInfo.Default_Page,
            "user_id": userInfo.User_Id,
            # "user_type": userInfo.User_Type_Id,

            
        }

    # ---------------------- Logout User ----------------------

    def logout_user(self, token: str):
        """
        Logout a user by ending their session.
        """
        # End the session
        self.auth_repo.end_session(token)

        return {"message": "User logged out successfully."}

    # ---------------------- Change Password ----------------------

    def change_password(self, user_id: int, change_data: ChangePassword):
        """
        Change a user's password and send a confirmation email.
        """
        # Validate and update the password
        self.auth_repo.change_password(user_id, change_data)

        # Fetch the user to send an email
        user = self.auth_repo.get_user_by_id(user_id)

        # Send a confirmation email
        email_subject = "Password Changed Successfully"
        email_body = f"Hi {user.Full_Name},\n\nYour password has been successfully changed. If you did not make this change, please contact support immediately."
        self.send_email(user.Email, email_subject, email_body)

        return {"message": "Password changed successfully. A confirmation email has been sent."}

    # ---------------------- Forgot Password ----------------------

    def forgot_password(self, forgot_data: ForgotPassword):
        """
        Generate a reset token, send a reset link, and notify the user.
        """
        # Generate a reset token
        reset_info = self.auth_repo.forgot_password(forgot_data)

        # Send a reset email
        reset_link = f"https://yourfrontend.com/reset-password?token={reset_info['reset_token']}"
        email_subject = "Password Reset Request"
        email_body = f"Hi,\n\nWe received a request to reset your password. Click the link below to reset your password:\n\n{reset_link}\n\nIf you did not request this, please ignore this email."
        self.send_email(forgot_data.Email, email_subject, email_body)

        return {"message": "Password reset link sent to your email."}