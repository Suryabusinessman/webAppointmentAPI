from fastapi import HTTPException, status as http_status
from app.repositories.NewsModules.newslike import NewsLikeRepository
from app.schemas.NewsModules.newslike import NewsLikeCreate, NewsLikeResponse
from app.models.NewsModules.newspost import NewsLike
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class NewsLikeService:
    """Service for NewsLike operations"""
    
    def __init__(self, like_repository: NewsLikeRepository, security_key: str):
        self.like_repository = like_repository
        self.security_key = security_key

    def get_likes_by_news_id(self, news_id: int, security_key: str):
        """Get all likes for a specific news post."""
        likes = self.like_repository.get_likes_by_news_id(news_id)
        return {
            "status": "success",
            "message": f"Retrieved {len(likes)} likes for news post {news_id}",
            "data": likes
        }

    def create_like(self, like_data: NewsLikeCreate, security_key: str):
        """Create a new like or return existing like."""
        # Convert Pydantic model to dict
        like_dict = like_data.model_dump()
        
        new_like = self.like_repository.create_like(like_dict)
        if not new_like:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create like."
            )
        
        # Check if this is a new like or existing like
        if hasattr(new_like, 'like_id') and new_like.like_id:
            message = "Like created successfully."
        else:
            message = "Like already exists for this user and news post."
            
        return {
            "status": "success",
            "message": message,
            "data": new_like
        }

    def remove_like(self, news_id: int, user_id: int, security_key: str):
        """Remove a like."""
        success = self.like_repository.remove_like(news_id, user_id)
        if not success:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Like not found for news {news_id} and user {user_id}"
            )
        return {
            "status": "success",
            "message": "Like removed successfully.",
            "data": {"news_id": news_id, "user_id": user_id}
        }

    def check_user_like(self, news_id: int, user_id: int, security_key: str):
        """Check if a user has liked a specific news post."""
        user_like = self.like_repository.check_user_like(news_id, user_id)
        
        return {
            "status": "success",
            "message": "Like status checked successfully",
            "data": {
                "has_liked": user_like is not None,
                "like_type": user_like.like_type if user_like else None,
                "like_id": user_like.like_id if user_like else None
            }
        }

    def get_user_likes(self, user_id: int, security_key: str, limit: int = 20):
        """Get likes by a specific user."""
        likes = self.like_repository.get_user_likes(user_id, limit)
        return {
            "status": "success",
            "message": f"Retrieved {len(likes)} likes for user {user_id}",
            "data": likes
        }

    def get_like_analytics(self, news_id: int, security_key: str):
        """Get like analytics for a news post."""
        analytics = self.like_repository.get_like_analytics(news_id)
        return {
            "status": "success",
            "message": f"Like analytics retrieved for news post {news_id}",
            "data": analytics
        }
