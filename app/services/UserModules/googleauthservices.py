from sqlalchemy.orm import Session
from app.models.UserModules.users import User
from app.models.UserModules.authmodules import UserSession
from app.models.BusinessModules.businessmanuser import BusinessmanUser
from app.models.UserModules.usertypes import UserType
from app.repositories.UserModules.users import UserRepository
from app.repositories.UserModules.userpermissions import UserPermissionRepository
from app.repositories.UserModules.usertypes import UserTypeRepository
from datetime import datetime, timedelta
from jose import jwt
import random
import string
import os
from fastapi import HTTPException, status

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

class GoogleAuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.user_permission_repo = UserPermissionRepository(db)
        self.user_type_repo = UserTypeRepository(db)

    def generate_random_password(self, length: int = 12) -> str:
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(chars) for _ in range(length))

    def create_access_token(self, user: User) -> str:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(user.User_Id),
            "email": user.Email,
            "exp": expire,
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def google_signin(self, email, full_name, picture, user_type_id, business_type_ids=None, brand_name=None, business_type_name=None, extra_fields=None, device_info=None, ip_address=None):
        # Check if user exists
        user = self.db.query(User).filter(User.Email == email).first()
        if user:
            raise HTTPException(status_code=400, detail="User with this email already exists. Please sign in instead.")

        # Create new user
        user = User(
            Email=email,
            Full_Name=full_name,
            Profile_Image=picture,
            Password_Hash=self.generate_random_password(),
            Is_Verified=True,
            Is_Active='Y',
            Is_Deleted='N',
            User_Type_Id=user_type_id,
            Added_On=datetime.utcnow(),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # If user_type_id == 2 (Businessman), insert into businessmanusers
        if user_type_id == 2:
            if not (business_type_ids and brand_name):
                raise HTTPException(status_code=400, detail="Businessman registration requires business_type_ids (array) and brand_name. Please provide all required fields.")
            business_type_name = business_type_name if business_type_name is not None else ""
            for business_type_id in business_type_ids:
                business_user = BusinessmanUser(
                    User_Id=user.User_Id,
                    User_Type_Id=user_type_id,
                    Business_Type_Id=business_type_id,
                    Brand_Name=brand_name,
                    Business_Type_Name=business_type_name,
                    Is_Active='Y',
                    Is_Deleted='N',
                    Added_On=datetime.utcnow(),
                    **{k: v for k, v in (extra_fields or {}).items() if v is not None and hasattr(BusinessmanUser, k)}
                )
                self.db.add(business_user)
            self.db.commit()

        # Create session
        access_token = self.create_access_token(user)
        user_session = UserSession(
            User_Id=user.User_Id,
            Device_Info=device_info,
            IP_Address=ip_address,
            Token=access_token,
            Is_Active=True,
            Created_At=datetime.utcnow(),
            Login_Timestamp=datetime.utcnow()
        )
        self.db.add(user_session)
        self.db.commit()

        # Gather context for frontend
        userInfo = self.user_repo.get_user_by_email(email)
        userTypeInfo = self.user_type_repo.get_by_id(user.User_Type_Id)
        userPermissionInfo = self.user_permission_repo.get_user_permissions_with_pages(user.User_Type_Id)

        return {
            "status": "success",
            "message": "Login successful.",
            "access_token": access_token,
            "session_id": user_session.Session_Id,
            "user_info": userInfo,
            "user_permission": userPermissionInfo,
            "user_type": userTypeInfo,
            "user_type_name": userTypeInfo.User_Type_Name if userTypeInfo else None,
            "user_type_id": userTypeInfo.User_Type_Id if userTypeInfo else None,
            "default_page": userTypeInfo.Default_Page if userTypeInfo else None,
            "user_id": userInfo.User_Id if userInfo else None,
        }
