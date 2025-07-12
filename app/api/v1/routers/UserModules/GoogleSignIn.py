# File: app/auth/google_auth.py
from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from pydantic import BaseModel, Extra
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from app.core.database import get_db
from app.models.UserModules.users import User
from app.models.UserModules.authmodules import UserSession
from app.models.UserModules.usertypes import UserType
from app.models.BusinessModules.businessmanuser import BusinessmanUser
from datetime import datetime, timedelta
import random
import string
from dotenv import load_dotenv
from jose import jwt
import os
from typing import List, Optional

load_dotenv()
router = APIRouter()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")  # Replace with actual client ID
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# ---------------------- Utility Function ----------------------

def validate_secret_key(secret_key: str = Header(...)):
    if secret_key != SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid SECRET_KEY provided."
        )

def get_device_info_and_ip(request: Request):
    device_info = request.headers.get("User-Agent", "Unknown Device")
    ip_address = request.headers.get("X-Forwarded-For")
    if ip_address:
        ip_address = ip_address.split(",")[0].strip()
    else:
        ip_address = request.client.host
    return device_info, ip_address

class GoogleTokenSchema(BaseModel, extra=Extra.allow):
    token: str
    user_type_id: int
    business_type_ids: Optional[List[int]] = None
    brand_name: Optional[str] = None
    business_type_name: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    address: Optional[str] = None

    def __init__(self, **data):
        # Convert user_type_id to int if string
        if 'user_type_id' in data and isinstance(data['user_type_id'], str):
            data['user_type_id'] = int(data['user_type_id'])
        super().__init__(**data)

def generate_random_password(length: int = 12) -> str:
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

def create_access_token(user: User) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user.User_Id),
        "email": user.Email,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/auth/google")
def google_login(data: GoogleTokenSchema, request: Request, db: Session = Depends(get_db), secret_key: str = Header(None)):
    # Validate SECRET_KEY from header
    if not secret_key or secret_key != SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid SECRET_KEY provided."
        )
    print("Google login request received with data:", data)
    try:
        idinfo = id_token.verify_oauth2_token(
            data.token,
            grequests.Request(),
            CLIENT_ID
        )

        email = idinfo.get("email")
        full_name = idinfo.get("name")
        picture = idinfo.get("picture")

        if not email:
            raise HTTPException(status_code=400, detail="Email not found in token")

        user = db.query(User).filter(User.Email == email).first()

        if user:
            # If user already exists, do not allow sign up again
            raise HTTPException(status_code=400, detail="User with this email already exists. Please sign in instead.")

        # New user: store all info
        user = User(
            Email=email,
            Full_Name=full_name,
            Profile_Image=picture,
            Password_Hash=generate_random_password(),
            Is_Verified=True,
            Is_Active='Y',
            Is_Deleted='N',
            User_Type_Id=data.user_type_id,
            Added_On=datetime.utcnow(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # If user_type_id == 2 (Businessman), insert into businessmanusers
        if data.user_type_id == 2:
            # Check for all required fields
            if not (data.business_type_ids and data.brand_name):
                raise HTTPException(status_code=400, detail="Businessman registration requires business_type_ids (array) and brand_name. Please provide all required fields.")
            # Use empty string if business_type_name is missing
            business_type_name = data.business_type_name if data.business_type_name is not None else ""
            # Prepare extra fields if present
            extra_fields = {}
            for field in ['state', 'city', 'postal_code', 'address']:
                if hasattr(data, field):
                    extra_fields[field.capitalize() if field != 'postal_code' else 'Postal_Code'] = getattr(data, field)
            # Insert a record for each business_type_id
            for business_type_id in data.business_type_ids:
                business_user = BusinessmanUser(
                    User_Id=user.User_Id,
                    User_Type_Id=data.user_type_id,
                    Business_Type_Id=business_type_id,
                    Brand_Name=data.brand_name,
                    Business_Type_Name=business_type_name,
                    Is_Active='Y',
                    Is_Deleted='N',
                    Added_On=datetime.utcnow(),
                    **{k: v for k, v in extra_fields.items() if v is not None and hasattr(BusinessmanUser, k)}
                )
                db.add(business_user)
            db.commit()
        # If user exists, do not update user info, just create a session
        access_token = create_access_token(user)
        device_info, ip_address = get_device_info_and_ip(request)

        user_session = UserSession(
            User_Id=user.User_Id,
            Device_Info=device_info,
            IP_Address=ip_address,
            Token=access_token,
            Is_Active=True,
            Created_At=datetime.utcnow(),
            Login_Timestamp=datetime.utcnow()
        )
        db.add(user_session)
        db.commit()

        return {
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "email": user.Email,
                "full_name": user.Full_Name,
                "user_id": user.User_Id,
                "user_type": user.User_Type_Id,
                "is_verified": user.Is_Verified
            }
        }

    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token")
