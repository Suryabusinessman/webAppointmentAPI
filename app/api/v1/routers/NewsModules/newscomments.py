from fastapi import APIRouter, Depends, HTTPException, Header, Request, status as http_status, Form, File, UploadFile
from sqlalchemy.orm import Session
from app.schemas.NewsModules.newscomments import NewsCommentCreate, NewsCommentUpdate, NewsCommentResponse
from app.services.NewsModules.newscomments import NewsCommentService
from app.repositories.NewsModules.newscomments import NewsCommentRepository
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

# ---------------------- Get Comments by News ID ----------------------

@router.get("/get-comments/{news_id}", response_model=dict)
def get_comments_by_news_id(
    news_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Get all comments for a specific news post.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": f"/get-comments/{news_id}", "method": "GET"}
        )
        
        # Get comments
        comment_repo = NewsCommentRepository(db)
        comments = comment_repo.get_comments_by_news_id(news_id)
        
        return {
            "status": "success",
            "message": f"Retrieved {len(comments)} comments for news post {news_id}",
            "data": comments
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting comments for news {news_id}: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Create Comment ----------------------

@router.post("/create-comment", response_model=dict)
def create_comment(
    news_id: int = Form(...),
    user_id: int = Form(...),
    content: str = Form(...),
    parent_comment_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Create a new comment on a news post.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": "/create-comment", "method": "POST"}
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
        
        # Validate parent comment if provided
        if parent_comment_id:
            comment_repo = NewsCommentRepository(db)
            parent_comment = comment_repo.get_by_id(parent_comment_id)
            if not parent_comment:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail=f"Parent comment with ID {parent_comment_id} not found"
                )
        
        # Create comment
        comment_data = {
            "news_id": news_id,
            "user_id": user_id,
            "parent_comment_id": parent_comment_id if parent_comment_id else None,
            "content": content,
            "added_by": user_id
        }
        
        comment_repo = NewsCommentRepository(db)
        new_comment = comment_repo.create_comment(comment_data, user_id)
        
        return {
            "status": "success",
            "message": "Comment created successfully",
            "data": new_comment
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating comment: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Update Comment ----------------------

@router.put("/update-comment/{comment_id}", response_model=dict)
def update_comment(
    comment_id: int,
    content: str = Form(...),
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Update an existing comment.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": f"/update-comment/{comment_id}", "method": "PUT"}
        )
        
        # Update comment
        comment_repo = NewsCommentRepository(db)
        update_data = {"content": content}
        updated_comment = comment_repo.update_comment(comment_id, update_data, 1)  # Using user_id 1 as default
        
        if not updated_comment:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Comment with ID {comment_id} not found"
            )
        
        return {
            "status": "success",
            "message": "Comment updated successfully",
            "data": updated_comment
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating comment {comment_id}: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Delete Comment ----------------------

@router.delete("/delete-comment/{comment_id}", response_model=dict)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Delete a comment (soft delete).
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": f"/delete-comment/{comment_id}", "method": "DELETE"}
        )
        
        # Delete comment
        comment_repo = NewsCommentRepository(db)
        success = comment_repo.delete_comment(comment_id)
        
        if not success:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Comment with ID {comment_id} not found"
            )
        
        return {
            "status": "success",
            "message": "Comment deleted successfully",
            "data": {"comment_id": comment_id}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting comment {comment_id}: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
