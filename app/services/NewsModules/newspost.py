from fastapi import HTTPException, status as http_status
from app.repositories.NewsModules.newspost import (
    NewsPostRepository, 
    NewsCommentRepository, 
    NewsLikeRepository, 
    NewsShareRepository
)
from app.schemas.NewsModules.newspost import (
    NewsPostCreate, 
    NewsPostUpdate, 
    NewsPostResponse, 
    NewsPostListResponse,
    NewsPostDetailResponse,
    NewsCommentCreate,
    NewsCommentUpdate,
    NewsCommentResponse,
    NewsLikeCreate,
    NewsLikeResponse,
    NewsShareCreate,
    NewsShareResponse,
    NewsPostQueryParams,
    NewsPostAnalytics,
    NewsStatus
)
from app.models.NewsModules.newspost import NewsPost, NewsComment, NewsLike, NewsShare
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class NewsPostService:
    """Service for NewsPost operations"""
    
    def __init__(self, news_repository: NewsPostRepository, security_key: str):
        self.news_repository = news_repository
        self.security_key = security_key

    def get_all_news_posts(self, security_key: str):
        """Fetch all news posts."""
        news_posts = self.news_repository.get_all()
        return {
            "status": "success",
            "message": "News posts retrieved successfully.",
            "data": news_posts
        }

    def get_news_post_by_id(self, news_id: int, security_key: str):
        """Fetch a news post by its ID."""
        news_post = self.news_repository.get_by_id(news_id)
        if not news_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"News post with ID {news_id} not found."
            )
        return {
            "status": "success",
            "message": f"News post with ID {news_id} retrieved successfully.",
            "data": news_post
        }

    def create_news_post(self, title: str, content: str, author_id: int, 
                        summary: Optional[str] = None, category: Optional[str] = None,
                        tags: Optional[List[str]] = None, featured_image: Optional[str] = None,
                        status: str = "DRAFT", publish_date: Optional[str] = None,
                        expiry_date: Optional[str] = None, is_featured: bool = False,
                        is_top_story: bool = False, seo_title: Optional[str] = None,
                        seo_description: Optional[str] = None, seo_keywords: Optional[str] = None,
                        meta_data: Optional[Dict[str, Any]] = None, business_user_id: Optional[int] = None, 
                        secret_key: str = None, added_by: int = None):
        """Create a new news post."""
        # Check if a news post with the same title already exists
        existing_news_post = self.news_repository.get_by_title(title)
        if existing_news_post:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"News post with title '{title}' already exists."
            )

        # Validate and convert status if provided
        validated_status = NewsStatus.DRAFT  # Default
        if status:
            try:
                validated_status = NewsStatus(status.upper())
            except ValueError:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status '{status}'. Must be one of: {[s.value for s in NewsStatus]}"
                )
        
        # Create news post data
        news_post_data = NewsPostCreate(
            title=title,
            content=content,
            author_id=author_id,
            summary=summary,
            category=category,
            tags=tags,
            featured_image=featured_image,
            status=validated_status,
            publish_date=publish_date,
            expiry_date=expiry_date,
            is_featured=is_featured,
            is_top_story=is_top_story,
            seo_title=seo_title,
            seo_description=seo_description,
            seo_keywords=seo_keywords,
            meta_data=meta_data,
            business_user_id=business_user_id
        )

        # Create the new news post
        new_news_post = self.news_repository.create(news_post_data, added_by)
        if not new_news_post:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create news post."
            )
        return {
            "status": "success",
            "message": "News post created successfully.",
            "data": new_news_post
        }

    def update_news_post(self, news_id: int, title: Optional[str] = None,
                        content: Optional[str] = None, summary: Optional[str] = None,
                        category: Optional[str] = None, tags: Optional[str] = None,
                        featured_image: Optional[str] = None, status: Optional[str] = None,
                        publish_date: Optional[str] = None, expiry_date: Optional[str] = None,
                        is_featured: Optional[bool] = None, is_top_story: Optional[bool] = None,
                        seo_title: Optional[str] = None, seo_description: Optional[str] = None,
                        seo_keywords: Optional[str] = None, meta_data: Optional[Dict[str, Any]] = None,
                        secret_key: str = None, modified_by: int = None):
        """Update a news post."""
        # Check if news post exists
        existing_news_post = self.news_repository.get_by_id(news_id)
        if not existing_news_post:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"News post with ID {news_id} not found."
            )

        # Validate and convert status if provided
        validated_status = None
        if status:
            try:
                validated_status = NewsStatus(status.upper())
            except ValueError:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status '{status}'. Must be one of: {[s.value for s in NewsStatus]}"
                )
        
        # Create update data
        update_data = NewsPostUpdate(
            title=title,
            content=content,
            summary=summary,
            category=category,
            tags=tags,
            featured_image=featured_image,
            status=validated_status,
            publish_date=publish_date,
            expiry_date=expiry_date,
            is_featured=is_featured,
            is_top_story=is_top_story,
            seo_title=seo_title,
            seo_description=seo_description,
            seo_keywords=seo_keywords,
            meta_data=meta_data
        )

        # Update the news post
        updated_news_post = self.news_repository.update(news_id, update_data, modified_by)
        if not updated_news_post:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update news post."
            )
        return {
            "status": "success",
            "message": "News post updated successfully.",
            "data": updated_news_post
        }

    def delete_news_post(self, news_id: int, secret_key: str = None, deleted_by: int = None):
        """Delete a news post (soft delete)."""
        # Check if news post exists
        existing_news_post = self.news_repository.get_by_id(news_id)
        if not existing_news_post:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"News post with ID {news_id} not found."
            )
        
        # Delete the news post
        success = self.news_repository.delete(news_id, deleted_by)
        if not success:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete news post."
            )
        return {
            "status": "success",
            "message": "News post deleted successfully.",
            "data": {"news_id": news_id}
        }
