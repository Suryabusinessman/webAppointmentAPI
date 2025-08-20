from fastapi import APIRouter, Depends, HTTPException, Header, Request, status as http_status, Form, File, UploadFile
from sqlalchemy.orm import Session
from app.schemas.NewsModules.newslike import NewsLikeCreate, NewsLikeResponse
from app.services.NewsModules.newslike import NewsLikeService
from app.repositories.NewsModules.newslike import NewsLikeRepository
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

# ---------------------- Get Likes by News ID ----------------------

@router.get("/get-likes/{news_id}", response_model=dict)
def get_likes_by_news_id(
    news_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Get all likes for a specific news post.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": f"/get-likes/{news_id}", "method": "GET"}
        )
        
        # Get likes
        like_repo = NewsLikeRepository(db)
        likes = like_repo.get_likes_by_news_id(news_id)
        
        return {
            "status": "success",
            "message": f"Retrieved {len(likes)} likes for news post {news_id}",
            "data": likes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting likes for news {news_id}: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Create Like ----------------------

@router.post("/create-like", response_model=dict)
def create_like(
    news_id: int = Form(...),
    user_id: int = Form(...),
    like_type: str = Form("LIKE"),
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Create a new like on a news post.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": "/create-like", "method": "POST"}
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
        
        # Validate like type
        valid_like_types = ["LIKE", "LOVE", "HELPFUL", "INSIGHTFUL"]
        if like_type not in valid_like_types:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid like type. Must be one of: {valid_like_types}"
            )
        
        # Create like
        like_data = {
            "news_id": news_id,
            "user_id": user_id,
            "like_type": like_type
        }
        
        like_repo = NewsLikeRepository(db)
        new_like = like_repo.create_like(like_data)
        
        # Check if this is a new like or existing like
        if hasattr(new_like, 'like_id') and new_like.like_id:
            message = "Like created successfully"
        else:
            message = "Like already exists for this user and news post"
        
        return {
            "status": "success",
            "message": message,
            "data": new_like
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating like: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Remove Like ----------------------

@router.delete("/remove-like/{news_id}/{user_id}", response_model=dict)
def remove_like(
    news_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Remove a like from a news post.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": f"/remove-like/{news_id}/{user_id}", "method": "DELETE"}
        )
        
        # Remove like
        like_repo = NewsLikeRepository(db)
        success = like_repo.remove_like(news_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Like not found for news {news_id} and user {user_id}"
            )
        
        return {
            "status": "success",
            "message": "Like removed successfully",
            "data": {"news_id": news_id, "user_id": user_id}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing like: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Check User Like Status ----------------------

@router.get("/check-like/{news_id}/{user_id}", response_model=dict)
def check_user_like_status(
    news_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Check if a user has liked a specific news post.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": f"/check-like/{news_id}/{user_id}", "method": "GET"}
        )
        
        # Check like status
        like_repo = NewsLikeRepository(db)
        likes = like_repo.get_likes_by_news_id(news_id)
        
        user_like = None
        for like in likes:
            if like.user_id == user_id:
                user_like = like
                break
        
        return {
            "status": "success",
            "message": "Like status checked successfully",
            "data": {
                "has_liked": user_like is not None,
                "like_type": user_like.like_type if user_like else None,
                "like_id": user_like.like_id if user_like else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking like status: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
