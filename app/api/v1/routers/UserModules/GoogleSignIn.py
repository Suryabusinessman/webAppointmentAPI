# File: app/auth/google_auth.py
from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from pydantic import BaseModel, Extra
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from app.core.database import get_db
# Service layer import
from app.services.UserModules.googleauthservices import GoogleAuthService
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



@router.post("/auth/google")
def google_login(data: GoogleTokenSchema, request: Request, db: Session = Depends(get_db), secret_key: str = Header(None)):
    # Validate SECRET_KEY from header
    if not secret_key or secret_key != SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid SECRET_KEY provided."
        )
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

        # Prepare extra fields
        extra_fields = {}
        for field in ['state', 'city', 'postal_code', 'address']:
            if hasattr(data, field):
                extra_fields[field.capitalize() if field != 'postal_code' else 'Postal_Code'] = getattr(data, field)

        device_info, ip_address = get_device_info_and_ip(request)
        service = GoogleAuthService(db)
        result = service.google_signin(
            email=email,
            full_name=full_name,
            picture=picture,
            user_type_id=data.user_type_id,
            business_type_ids=data.business_type_ids,
            brand_name=data.brand_name,
            business_type_name=data.business_type_name,
            extra_fields=extra_fields,
            device_info=device_info,
            ip_address=ip_address
        )
        # If tuple, it's (dict, status_code)
        if isinstance(result, tuple):
            # Patch the status key if present
            if isinstance(result[0], dict) and "success" in result[0]:
                result_dict = result[0]
                result_dict["status"] = "success" if result_dict["success"] else "failed"
                del result_dict["success"]
                return result_dict, result[1]
            return result
        # Patch the status key if present
        if isinstance(result, dict) and "success" in result:
            result["status"] = "success" if result["success"] else "failed"
            del result["success"]
        return result
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token")
