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
from typing import Optional
import logging

load_dotenv()
router = APIRouter()
logger = logging.getLogger(__name__)

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")  # Replace with actual client ID
SECRET_KEY = "88AC1A95756D9259823CCA6E17145A0"  # Same as security.py
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# ---------------------- Utility Function ----------------------

def validate_secret_key(secret_key: str = Header(...)):
    """Validate the secret key from request header."""
    if not secret_key or secret_key != SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid SECRET_KEY provided."
        )

def get_device_info_and_ip(request: Request):
    """Extract device info and IP address from request."""
    device_info = request.headers.get("User-Agent", "Unknown Device")
    ip_address = request.headers.get("X-Forwarded-For")
    if ip_address:
        ip_address = ip_address.split(",")[0].strip()
    else:
        ip_address = request.client.host
    return device_info, ip_address

class GoogleTokenSchema(BaseModel, extra=Extra.allow):
    token: str
    state: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    address: Optional[str] = None

@router.post("/auth/google")
async def google_login(
    data: GoogleTokenSchema, 
    request: Request, 
    db: Session = Depends(get_db), 
    secret_key: str = Header(None)
):
    """
    Handle Google OAuth login/registration for simple users only.
    
    This endpoint:
    1. Validates the Google ID token
    2. Checks if user exists
    3. Creates new user if doesn't exist (always as user_type_id = 3)
    4. Returns consistent response format
    """
    try:
        # Validate SECRET_KEY from header
        validate_secret_key(secret_key)
        
        # Validate Google ID token
        try:
            idinfo = id_token.verify_oauth2_token(
                data.token,
                grequests.Request(),
                CLIENT_ID
            )
        except ValueError as e:
            logger.warning(f"Invalid Google token provided: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid Google token. Please try again."
            )
        
        # Extract user information from token
        email = idinfo.get("email")
        full_name = idinfo.get("name")
        picture = idinfo.get("picture")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Email not found in Google token"
            )
        
        if not full_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Name not found in Google token"
            )

        # Prepare extra fields for user creation
        extra_fields = {}
        for field in ['state', 'city', 'postal_code', 'address']:
            if hasattr(data, field) and getattr(data, field):
                extra_fields[field.capitalize() if field != 'postal_code' else 'Postal_Code'] = getattr(data, field)

        # Get device info and IP address
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Initialize service and process Google signin
        service = GoogleAuthService(db)
        result = service.google_signin(
            email=email,
            full_name=full_name,
            picture=picture,
            extra_fields=extra_fields,
            device_info=device_info,
            ip_address=ip_address
        )
        
        # Log successful Google authentication
        logger.info(f"Google authentication successful for email: {email}")
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log unexpected errors and return generic message
        logger.error(f"Unexpected error in Google login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google authentication failed. Please try again later."
        )
