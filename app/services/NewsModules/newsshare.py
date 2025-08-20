from fastapi import HTTPException, status as http_status
from app.repositories.NewsModules.newsshare import NewsShareRepository
from app.schemas.NewsModules.newsshare import NewsShareCreate, NewsShareResponse
from app.models.NewsModules.newspost import NewsShare
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class NewsShareService:
    """Service for NewsShare operations"""
    
    def __init__(self, share_repository: NewsShareRepository, security_key: str):
        self.share_repository = share_repository
        self.security_key = security_key

    def get_shares_by_news_id(self, news_id: int, security_key: str):
        """Get all shares for a specific news post."""
        shares = self.share_repository.get_shares_by_news_id(news_id)
        return {
            "status": "success",
            "message": f"Retrieved {len(shares)} shares for news post {news_id}",
            "data": shares
        }

    def create_share(self, share_data: NewsShareCreate, security_key: str):
        """Create a new share."""
        # Convert Pydantic model to dict
        share_dict = share_data.model_dump()
        
        new_share = self.share_repository.create_share(share_dict)
        if not new_share:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create share."
            )
        return {
            "status": "success",
            "message": "Share created successfully.",
            "data": new_share
        }

    def get_user_shares(self, user_id: int, security_key: str, limit: int = 20):
        """Get shares by a specific user."""
        shares = self.share_repository.get_user_shares(user_id, limit)
        return {
            "status": "success",
            "message": f"Retrieved {len(shares)} shares for user {user_id}",
            "data": shares
        }

    def get_share_analytics(self, news_id: int, security_key: str):
        """Get share analytics for a news post."""
        analytics = self.share_repository.get_share_analytics(news_id)
        return {
            "status": "success",
            "message": f"Share analytics retrieved for news post {news_id}",
            "data": analytics
        }

    def get_platform_shares(self, platform: str, security_key: str, limit: int = 20):
        """Get shares by platform."""
        shares = self.share_repository.get_platform_shares(platform, limit)
        return {
            "status": "success",
            "message": f"Retrieved {len(shares)} shares for platform {platform}",
            "data": shares
        }
