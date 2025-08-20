from fastapi import APIRouter, Depends, HTTPException, Header, Request, status as http_status, Form, File, UploadFile
from sqlalchemy.orm import Session
from app.schemas.NewsModules.newsshare import NewsShareCreate, NewsShareResponse
from app.services.NewsModules.newsshare import NewsShareService
from app.repositories.NewsModules.newsshare import NewsShareRepository
from app.services.SecurityModules.security_service import SecurityService
from app.models.SecurityModules.security_events import SecurityEventType, SecurityEventSeverity
from app.core.database import get_db
from app.core.config import config
from typing import Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Define the router
router = APIRouter()

# ---------------------- Utility Function ----------------------

def validate_secret_key(secret_key: str = Header(..., alias="secret-key")):
    """Validate the SECRET_KEY from the request header."""
    if secret_key != config.SECRET_KEY:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Invalid SECRET_KEY provided."
        )

def get_device_info_and_ip(request: Request):
    """Extract device information and IP address from the request."""
    device_info = request.headers.get("User-Agent", "Unknown Device")
    ip_address = request.headers.get("X-Forwarded-For")
    if ip_address:
        ip_address = ip_address.split(",")[0].strip()
    else:
        ip_address = request.client.host
    return device_info, ip_address

# ---------------------- Get Shares by News ID ----------------------

@router.get("/get-shares/{news_id}", response_model=dict)
def get_shares_by_news_id(
    news_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Get all shares for a specific news post.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": f"/get-shares/{news_id}", "method": "GET"}
        )
        
        # Get shares
        share_repo = NewsShareRepository(db)
        shares = share_repo.get_shares_by_news_id(news_id)
        
        return {
            "status": "success",
            "message": f"Retrieved {len(shares)} shares for news post {news_id}",
            "data": shares
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting shares for news {news_id}: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Create Share ----------------------

@router.post("/create-share", response_model=dict)
def create_share(
    news_id: int = Form(...),
    user_id: int = Form(...),
    share_platform: str = Form(...),
    share_url: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Create a new share record for a news post.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": "/create-share", "method": "POST"}
        )
        
        # Validate news post exists
        from app.repositories.NewsModules.newspost import NewsPostRepository
        news_repo = NewsPostRepository(db)
        news_post = news_repo.get_by_id(news_id)
        if not news_post:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"News post with ID {news_id} not found"
            )
        
        # Validate user exists
        from app.models.UserModules.users import User
        user = db.query(User).filter(User.user_id == user_id, User.is_active == "Y", User.is_deleted == "N").first()
        if not user:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"User with ID {user_id} not found or inactive"
            )
        
        # Validate share platform
        valid_platforms = ["FACEBOOK", "TWITTER", "LINKEDIN", "WHATSAPP", "EMAIL", "COPY_LINK"]
        if share_platform not in valid_platforms:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid share platform. Must be one of: {valid_platforms}"
            )
        
        # Create share
        share_data = {
            "news_id": news_id,
            "user_id": user_id,
            "share_platform": share_platform,
            "share_url": share_url
        }
        
        share_repo = NewsShareRepository(db)
        new_share = share_repo.create_share(share_data)
        
        return {
            "status": "success",
            "message": "Share created successfully",
            "data": new_share
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating share: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Get Share Analytics ----------------------

@router.get("/share-analytics/{news_id}", response_model=dict)
def get_share_analytics(
    news_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Get analytics for shares of a specific news post.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": f"/share-analytics/{news_id}", "method": "GET"}
        )
        
        # Get shares
        share_repo = NewsShareRepository(db)
        shares = share_repo.get_shares_by_news_id(news_id)
        
        # Calculate analytics
        platform_counts = {}
        total_shares = len(shares)
        
        for share in shares:
            platform = share.share_platform
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        analytics = {
            "total_shares": total_shares,
            "platform_breakdown": platform_counts,
            "most_popular_platform": max(platform_counts.items(), key=lambda x: x[1])[0] if platform_counts else None
        }
        
        return {
            "status": "success",
            "message": f"Share analytics retrieved for news post {news_id}",
            "data": analytics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting share analytics for news {news_id}: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Get User Share History ----------------------

@router.get("/user-shares/{user_id}", response_model=dict)
def get_user_share_history(
    user_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Get share history for a specific user.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": f"/user-shares/{user_id}", "method": "GET"}
        )
        
        # Validate user exists
        from app.models.UserModules.users import User
        user = db.query(User).filter(User.user_id == user_id, User.is_active == "Y", User.is_deleted == "N").first()
        if not user:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"User with ID {user_id} not found or inactive"
            )
        
        # Get user shares
        share_repo = NewsShareRepository(db)
        shares = share_repo.get_user_shares(user_id)
        
        return {
            "status": "success",
            "message": f"Retrieved {len(shares)} shares for user {user_id}",
            "data": shares
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user share history for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
