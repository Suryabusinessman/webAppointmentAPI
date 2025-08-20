from fastapi import APIRouter, Depends, HTTPException, Header, Request, status as http_status, Form, File, UploadFile
from sqlalchemy.orm import Session
from app.schemas.NewsModules.newspost import NewsPostCreate, NewsPostUpdate, NewsPostResponse
from app.services.NewsModules.newspost import NewsPostService
from app.repositories.NewsModules.newspost import NewsPostRepository
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

# ---------------------- Get Available Authors ----------------------

@router.get("/available-authors", response_model=dict)
def get_available_authors(
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Get list of available users that can be used as authors for news posts.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": "/available-authors", "method": "GET"}
        )
        
        # Get all active users
        from app.models.UserModules.users import User
        users = db.query(User).filter(User.is_active == "Y", User.is_deleted == "N").all()
        
        authors = []
        for user in users:
            authors.append({
                "user_id": user.user_id,
                "full_name": user.full_name,
                "email": user.email,
                "phone": user.phone
            })
        
        return {
            "status": "success",
            "message": f"Found {len(authors)} available authors",
            "data": authors
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting available authors: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Get All News Posts ----------------------

@router.get("/all-news-posts", response_model=dict)
def get_all_news_posts(
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch all news posts.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": "/all-news-posts", "method": "GET"}
        )
        
        service = NewsPostService(NewsPostRepository(db), config.SECRET_KEY)
        result = service.get_all_news_posts(secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting all news posts: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Get News Post by ID ----------------------

@router.get("/news-posts/{news_id}", response_model=dict)
def get_news_post_by_id(
    news_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Fetch a news post by its ID.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": f"/news-posts/{news_id}", "method": "GET"}
        )
        
        service = NewsPostService(NewsPostRepository(db), config.SECRET_KEY)
        result = service.get_news_post_by_id(news_id, secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting news post {news_id}: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Create News Post ----------------------

@router.post("/create-news-post", response_model=dict)
def create_news_post(
    title: str = Form(...),
    content: str = Form(...),
    author_id: int = Form(...),
    summary: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # JSON string
    featured_image: Optional[UploadFile] = File(None),  # File upload
    status: str = Form("DRAFT"),
    publish_date: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    is_featured: bool = Form(False),
    is_top_story: bool = Form(False),
    seo_title: Optional[str] = Form(None),
    seo_description: Optional[str] = Form(None),
    seo_keywords: Optional[str] = Form(None),
    meta_data: Optional[str] = Form(None),  # JSON string
    business_user_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Create a new news post.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": "/create-news-post", "method": "POST"}
        )
        
        # Validate that the author_id exists in the users table
        from app.models.UserModules.users import User
        user = db.query(User).filter(User.user_id == author_id).first()
        if not user:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Author with ID {author_id} does not exist. Please use a valid user ID."
            )
        
        # Check if user is Admin (user_type_id = 1) - Admin users don't need business_user_id
        # This allows Admin users to create news posts without being associated with a specific business
        is_admin = user.user_type_id == 1
        
        # Validate business_user_id if provided and user is not Admin
        # Non-Admin users must provide a valid business_user_id
        if business_user_id and not is_admin:
            from app.models.BusinessModules.businessmanuser import BusinessUser
            business_user = db.query(BusinessUser).filter(BusinessUser.business_user_id == business_user_id).first()
            if not business_user:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail=f"Business user with ID {business_user_id} does not exist. Please use a valid business user ID."
                )
        
        # For Admin users, set business_user_id to None if not provided
        # This allows Admin users to create system-wide news posts
        if is_admin and not business_user_id:
            business_user_id = None
        
        # Handle file upload
        featured_image_path = None
        if featured_image:
            from app.utils.file_upload import save_upload_file
            UPLOAD_DIRECTORY_NEWS_IMAGES = "uploads/news_images"
            featured_image_path = save_upload_file(featured_image, UPLOAD_DIRECTORY_NEWS_IMAGES)
        
        # Parse tags from JSON string
        parsed_tags = None
        if tags:
            import json
            try:
                parsed_tags = json.loads(tags)
            except json.JSONDecodeError:
                # If not valid JSON, treat as comma-separated string
                parsed_tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Parse dates
        parsed_publish_date = None
        parsed_expiry_date = None
        
        if publish_date:
            try:
                from datetime import datetime
                parsed_publish_date = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
            except ValueError:
                # Try different date formats
                try:
                    parsed_publish_date = datetime.strptime(publish_date, "%Y-%m-%d")
                except ValueError:
                    pass
        
        if expiry_date:
            try:
                from datetime import datetime
                parsed_expiry_date = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
            except ValueError:
                # Try different date formats
                try:
                    parsed_expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d")
                except ValueError:
                    pass
        
        # Parse meta_data from JSON string
        parsed_meta_data = None
        if meta_data:
            import json
            # Debug logging
            logger.info(f"Received meta_data: '{meta_data}' (type: {type(meta_data)})")
            
            # Handle empty strings or whitespace-only strings
            if isinstance(meta_data, str):
                meta_data_clean = meta_data.strip()
                if not meta_data_clean:
                    logger.info("meta_data is empty or whitespace-only, setting to None")
                    parsed_meta_data = None
                else:
                    try:
                        # Remove any extra quotes if the string is wrapped in quotes
                        if meta_data_clean.startswith('"') and meta_data_clean.endswith('"'):
                            meta_data_clean = meta_data_clean[1:-1]
                        logger.info(f"Cleaned meta_data: '{meta_data_clean}'")
                        parsed_meta_data = json.loads(meta_data_clean)
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error for meta_data: {str(e)}")
                        raise HTTPException(
                            status_code=http_status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid meta_data JSON format: {str(e)}. Please provide valid JSON like: {{\"key\": \"value\"}} or leave empty."
                        )
            elif isinstance(meta_data, dict):
                parsed_meta_data = meta_data
            else:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="meta_data must be a valid JSON string, dict, or empty"
                )
        
        service = NewsPostService(NewsPostRepository(db), config.SECRET_KEY)
        result = service.create_news_post(
            title=title,
            content=content,
            author_id=author_id,
            summary=summary,
            category=category,
            tags=parsed_tags,
            featured_image=featured_image_path,
            status=status,
            publish_date=parsed_publish_date,
            expiry_date=parsed_expiry_date,
            is_featured=is_featured,
            is_top_story=is_top_story,
            seo_title=seo_title,
            seo_description=seo_description,
            seo_keywords=seo_keywords,
            meta_data=parsed_meta_data,
            business_user_id=business_user_id,
            secret_key=secret_key,
            added_by=author_id
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating news post: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Update News Post ----------------------

@router.put("/update-news-post/{news_id}", response_model=dict)
def update_news_post(
    news_id: int,
    title: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    summary: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    featured_image: Optional[UploadFile] = File(None),  # File upload
    status: Optional[str] = Form(None),
    publish_date: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    is_featured: Optional[bool] = Form(None),
    is_top_story: Optional[bool] = Form(None),
    seo_title: Optional[str] = Form(None),
    seo_description: Optional[str] = Form(None),
    seo_keywords: Optional[str] = Form(None),
    meta_data: Optional[str] = Form(None),  # JSON string
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Update a news post.
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": f"/update-news-post/{news_id}", "method": "PUT"}
        )
        
        # Handle file upload
        featured_image_path = None
        if featured_image:
            from app.utils.file_upload import save_upload_file
            UPLOAD_DIRECTORY_NEWS_IMAGES = "uploads/news_images"
            featured_image_path = save_upload_file(featured_image, UPLOAD_DIRECTORY_NEWS_IMAGES)
        
        # Parse tags from JSON string
        parsed_tags = None
        if tags:
            import json
            try:
                parsed_tags = json.loads(tags)
            except json.JSONDecodeError:
                # If not valid JSON, treat as comma-separated string
                parsed_tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Parse dates
        parsed_publish_date = None
        parsed_expiry_date = None
        
        if publish_date:
            try:
                from datetime import datetime
                parsed_publish_date = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
            except ValueError:
                # Try different date formats
                try:
                    parsed_publish_date = datetime.strptime(publish_date, "%Y-%m-%d")
                except ValueError:
                    pass
        
        if expiry_date:
            try:
                from datetime import datetime
                parsed_expiry_date = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
            except ValueError:
                # Try different date formats
                try:
                    parsed_expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d")
                except ValueError:
                    pass
        
        # Parse meta_data from JSON string
        parsed_meta_data = None
        if meta_data:
            import json
            # Debug logging
            logger.info(f"Received meta_data: '{meta_data}' (type: {type(meta_data)})")
            
            # Handle empty strings or whitespace-only strings
            if isinstance(meta_data, str):
                meta_data_clean = meta_data.strip()
                if not meta_data_clean:
                    logger.info("meta_data is empty or whitespace-only, setting to None")
                    parsed_meta_data = None
                else:
                    try:
                        # Remove any extra quotes if the string is wrapped in quotes
                        if meta_data_clean.startswith('"') and meta_data_clean.endswith('"'):
                            meta_data_clean = meta_data_clean[1:-1]
                        logger.info(f"Cleaned meta_data: '{meta_data_clean}'")
                        parsed_meta_data = json.loads(meta_data_clean)
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error for meta_data: {str(e)}")
                        raise HTTPException(
                            status_code=http_status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid meta_data JSON format: {str(e)}. Please provide valid JSON like: {{\"key\": \"value\"}} or leave empty."
                        )
            elif isinstance(meta_data, dict):
                parsed_meta_data = meta_data
            else:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="meta_data must be a valid JSON string, dict, or empty"
                )
        
        service = NewsPostService(NewsPostRepository(db), config.SECRET_KEY)
        result = service.update_news_post(
            news_id=news_id,
            title=title,
            content=content,
            summary=summary,
            category=category,
            tags=parsed_tags,
            featured_image=featured_image_path,
            status=status,
            publish_date=parsed_publish_date,
            expiry_date=parsed_expiry_date,
            is_featured=is_featured,
            is_top_story=is_top_story,
            seo_title=seo_title,
            seo_description=seo_description,
            seo_keywords=seo_keywords,
            meta_data=parsed_meta_data,
            secret_key=secret_key,
            modified_by=1  # You might want to get this from authentication
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating news post {news_id}: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# ---------------------- Delete News Post ----------------------

@router.delete("/delete-news-post/{news_id}", response_model=dict)
def delete_news_post(
    news_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    secret_key: str = Depends(validate_secret_key)
):
    """
    Delete a news post (soft delete).
    """
    try:
        device_info, ip_address = get_device_info_and_ip(request)
        
        # Log security event
        security_service = SecurityService(db)
        security_service.log_security_event(
            event_type=SecurityEventType.API_ACCESS,
            ip_address=ip_address,
            user_agent=device_info,
            event_metadata={"endpoint": f"/delete-news-post/{news_id}", "method": "DELETE"}
        )
        
        service = NewsPostService(NewsPostRepository(db), config.SECRET_KEY)
        result = service.delete_news_post(news_id, secret_key, deleted_by=1)  # You might want to get this from authentication
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting news post {news_id}: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


